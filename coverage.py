import json
import lib_zstack_constants as constant
import lib_zstack as lib
from mutation import helpers


class Coverage:
    """
    Save the coverage information for the current session. Used to guid the fuzzing cycle.
    """
    def __init__(self):
        self.prev_interest = None  # previous interest from original seed library
        self.function_hits = [0] * (constant.map_size >> 8)  # cumulative hit counts of functions
        self.trace_bits = [0] * constant.map_size  # bitmap for the current execution
        self.virgin_bits = [255] * constant.map_size  # bitmap for all the tuples
        self.statement_bits = [0] * constant.map_size  # bitmap for statements
        self.trace = {}

        self.interest = []
        self.top_rated = []
        self.new_favored = False
        self.current_favored = None
        self.current_exec_us = 0
        self.pending_favored = 0

        self.bitmap_state = {'statement': 0, 'edge': 0.0}
        self.total_function = 0
        self.total_statement = 0
        self.total_edge = 0
        self.total_crash = 0
        self.uni_crash = 0
        self.crash_stack = {}
        self.hit_function = []
        self.hit_statement = 0
        self.status_hits = [0] * 10
        self.hit_stmt_index = []
        self.init_timestamp = str(helpers.get_milli_time())

        self.count_class_lookup8 = [0] * 256
        self.count_class_lookup8[1] = 1
        self.count_class_lookup8[2] = 2
        self.count_class_lookup8[3] = 4
        self.count_class_lookup8[4:7] = [8] * 4
        self.count_class_lookup8[8:15] = [16] * 8
        self.count_class_lookup8[16:31] = [32] * 16
        self.count_class_lookup8[32:127] = [64] * 96
        self.count_class_lookup8[128:] = [128] * 128
        self.count_class_lookup16 = [0] * constant.map_size

    def init_count_class16(self):
        i = 0
        j = 0
        for i in range(0, 256):
            for j in range(0, 256):
                self.count_class_lookup16[(i << 8) + j] = \
                    (self.count_class_lookup8[i] << 8) | self.count_class_lookup8[j]
        return

    def parse_coverage_result(self):
        """
        Parse CFG of ZCl module to calculate coverage of the current Z-Stack execution
        :return: the module coverage
        """
        with open(constant.cfg_file, 'r') as cfg:
            cfg_dict = json.load(cfg)

        module_prefix = 'Module '
        function_prefix = 'Function '
        line_keyword = 'Line'
        find_module = False
        find_function = False
        curr_function = None
        module_coverage = 0.0
        curr_function_index = 0

        total_statement = 0
        total_edge = 0
        self.trace_bits = [0] * constant.map_size
        coverage = open(constant.coverage_file, 'r')
        for line in coverage:
            if module_prefix in line and cfg_dict.get('name') in line:  # Find ZCL module
                find_module = True
                cov = line.split(':')[1][:-2]
                module_coverage = float(cov)
            elif find_module and function_prefix in line:  # Search function from CFG
                function_name = line.split()[1].strip('"')
                function_coverage = line.split(':')[1][:-2]
                function_rec = search_function(cfg_dict, function_name)
                if function_rec is not None:
                    self.total_function += 1
                    total_edge += get_num_edge(function_rec)
                    total_statement += get_num_statement(function_rec)
                    if curr_function is not None and curr_function.name != function_rec.get('name'):
                        # update bitmap for the current function
                        # prev_location = self.update_trace_bitmap(curr_function, prev_location)
                        self.update_trace_bitmap(curr_function)
                        self.update_trace(curr_function)
                    find_function = True
                    curr_function = Function(curr_function_index)
                    curr_function.name = function_name
                    curr_function.coverage = float(function_coverage)
                    curr_function.block_list = function_rec.get('block_list')
                    # Update function hit counts
                    if curr_function.coverage != 0.0:
                        if curr_function.name not in self.hit_function:
                            self.hit_function.append(curr_function.name)

                        funct_index = self.hit_function.index(curr_function.name)
                        self.function_hits[funct_index] += 1
                    curr_function_index += 1
                else:
                    find_function = False
            elif find_function and line_keyword in line:  # Collect uncovered statements for a given function
                line_array = line.split(':')[0].split()
                if len(line_array) == 2:
                    curr_function.add_uncovered(line_array[1])
                elif len(line_array) > 2:
                    rang = range(int(line_array[1]), int(line_array[3]) + 1)
                    for i in rang:
                        curr_function.add_uncovered(i)
            elif '=' in line and find_function:  # End of coverage file
                # Update bitmap for the last function
                self.update_trace_bitmap(curr_function)
                self.update_trace(curr_function)
                curr_function = None

        if self.total_statement == 0:
            self.total_statement = total_statement
        if self.total_edge == 0:
            self.total_edge = total_edge
        self.classify_counts(self.trace_bits)
        return module_coverage

    def update_trace(self, function):
        if function.name in self.trace.keys():
            current_trace = self.trace[function.name]
            for edge in function.block_trace:
                if edge not in current_trace:
                    current_trace.append(edge)
        else:
            self.trace[function.name] = function.block_trace
        return

    def classify_counts(self, trace_bits):
        """
        Destructively classify execution counts in a trace. This is used as a
        pre-processing step for any newly acquired traces.
        :param trace_bits: A bitmap of current execution trace
        """
        iterate = constant.map_size >> 2
        index = 0
        while iterate > 0:
            if lib.unlikely(trace_bits[index]):
                mem16 = trace_bits
                trace_bits[index] = self.count_class_lookup16[mem16[index]]
                trace_bits[index + 1] = self.count_class_lookup16[mem16[index + 1]]

            index += 1
            iterate -= 1
        return

    def update_trace_bitmap(self, function):
        """
        Update trace bitmap for the current function
        :param function: the current function found in coverage report
        """
        if function.coverage == 0.0:
            return
        prev_location = 0
        uncovered = function.uncovered_stmt
        block_list = function.block_list
        skip_block = []
        for block in block_list[1:-1]:
            if block.get('block_number') == "2":
                # Update trace bitmap
                location = block.get('location')
                self.trace_bits[location ^ prev_location] += 1
                function.block_trace.append("%d->%d" % (prev_location, location))
                prev_location = location >> 1
                # If a block is accessed, we also record its statements in statement bitmap
                self.update_statement_bitmap(block)
            elif int(block.get('block_number')) in skip_block or not is_accessed(block.get('statements'), uncovered):
                continue

            for succ in block.get('succs'):
                succ_block = block_list[succ - 1]
                if is_accessed(succ_block.get('statements'), uncovered):
                    location = block.get('location')
                    self.trace_bits[location ^ prev_location] += 1
                    function.block_trace.append("%d->%d" % (prev_location, location))
                    prev_location = location >> 1
                    # If a block is accessed, we also record its statements in statement bitmap
                    self.update_statement_bitmap(succ_block)
                elif succ not in skip_block:
                    skip_block.append(succ)
        return prev_location

    def update_statement_bitmap(self, block):
        stmt_list = block.get('statements')
        if len(stmt_list) > 0:
            for line_num in stmt_list:
                if line_num != 1:  # statement 1 means the last block
                    self.statement_bits[line_num] += 1
        return


class Function:
    """
    The current function in coverage report
    """
    def __init__(self, index):
        self.name = ""
        self.index = index
        self.coverage = 0.0
        self.uncovered_stmt = []
        self.block_list = []
        self.block_trace = []

    def add_uncovered(self, stmt):
        if int(stmt) not in self.uncovered_stmt:
            self.uncovered_stmt.append(int(stmt))

    def num_statement(self):
        total = 0
        for block in self.block_list:
            total += len(block.get('statements'))
        return total


def is_accessed(statements, uncovered):
    """
    Compare two list to see if a list contains any item of another list
    :param statements: a list of statements included in a basic block
    :param uncovered: a list of statement line number which is not uncovered in the previous execution
    :return: return False if all statements are not covered, otherwise return True
    """
    total_uncovered = 0
    if len(statements) == 0 or len(uncovered) == 0:
        return True
    for stmt in statements:
        if stmt in uncovered:
            total_uncovered += 1
    if total_uncovered == len(statements):
        return False
    return True


def search_function(cfg, name):
    """
    Find a specific function in CFG
    :param cfg: the CFG data of ZCL module
    :param name: function name
    :return: return the found function object
    """
    func_list = cfg.get('function_list')
    for function in func_list:
        if function.get('name') == name:
            return function
    return None


def get_num_statement(function):
    total = 0
    block_list = function.get("block_list")
    for block in block_list:
        total += len(block.get("statements"))
    return total


def get_num_edge(function):
    total = 0
    block_list = function.get("block_list")
    for block in block_list:
        total += len(block.get("succs"))
    return total
