import copy
import json
import re
import socket
import coverage
import lib_zstack_constants as constant
from mutation import helpers, blocks


class QueueEntry:
    """
    The pending favored seed input
    """

    def __init__(self, mutant):
        self.mutant_name = mutant._name  # the name of current mutant field
        self.value = mutant._value  # current value of mutant, will keep if favored
        self.was_fuzzed = False
        self.favored = False
        self.bitmap_size = 0  # number of bits set in bitmap
        self.exec_cksum = 0
        self.exec_us = 0  # execution time in millisecond
        self.current_mutant_index = mutant.mutant_index  # mutation index of current primitive data
        self.interest_index = 0  # index in interesting values list
        self.trace_mini = None
        self.pending = True
        self.node_fields = []  # list of mutants construct the current node
        self.render_index = 0
        self.render_list = []  # list of rendered mutants in every fuzz iteration

    def __eq__(self, other):
        if not isinstance(other, QueueEntry):
            raise Exception("Not a Node object!")
        if self.mutant_name == other.mutant_name and self.value == other.value \
                and self.node_fields == other.node_fields and self.bitmap_size == other.bitmap_size:
            return True
        return False

    def nodes_initialized(self, node_list):
        for index, node in enumerate(node_list):
            self.node_fields.append(copy.copy(node))
            if node.name == self.mutant_name:
                self.render_index = index
        return

    def favored_change(self, fuzz_node):
        """
        If current entry is replaced by a new favored entry but not completes its mutation, save current information
        for future resume.
        :param fuzz_node:
        :return:
        """
        self.pending = True
        self.was_fuzzed = True
        for index, item in enumerate(self.node_fields):
            if item.fuzzable:
                original = fuzz_node.names[item._name]
                if index > self.render_index:
                    item._mutant_index = original._mutant_index
                    item._value = original._value
        return

    def mutate(self, fuzz_node):
        mutated = False
        if not self.pending and self.was_fuzzed:
            mutated = False
        elif self.pending and self.was_fuzzed:  # If current entry was fuzzed before but not completed
            self.pending = False
            self.was_fuzzed = False
            for index, item in enumerate(self.node_fields):
                if item.fuzzable:
                    original = fuzz_node.names[item._name]
                    if index > self.render_index:
                        original._mutant_index = item._mutant_index - 1
                        mutated = original.mutate()
                        if not mutated:
                            return False
                        if not isinstance(original, blocks.Block):
                            fuzz_node.mutant = original
                        break
                    else:
                        original._value = item._value
                        original._mutant_index = item._mutant_index
                        original._skip_mutation = True
        elif self.render_index == len(self.render_list) - 1:
            mutated = False
        else:
            for index, item in enumerate(self.node_fields):
                if item.fuzzable:
                    original = fuzz_node.names[item._name]
                    if index > self.render_index and original.mutate():
                        mutated = True
                        if not isinstance(original, blocks.Block):
                            fuzz_node.mutant = original
                        break
                    elif index < self.render_index:
                        original._skip_mutation = True
                        original._mutant_index = item._mutant_index
                        original._value = item._value
        return mutated

    def complete_mutate(self, fuzz_node):
        self.was_fuzzed = True
        self.pending = False
        for index, item in enumerate(self.render_list):
            if item.fuzzable:
                original = fuzz_node.names[item._name]
                if index > self.render_index and original.mutate():
                    if not original._fuzz_complete:
                        original.restart_mutation()
                    else:
                        original._fuzz_complete = False
                        original._skip_mutation = False
                        original._mutant_index = 0
                elif index <= self.render_index:
                    original._skip_mutation = False
        return


def unlikely(exp):
    if not not exp == 0:
        return False
    return True


def likely(exp):
    if not not exp == 1:
        return True
    return False


def FF(value):
    return 0xff << (value << 3)


def checksum(trace_bit):
    return hash(tuple(trace_bit))


# Address received execution status
unsuccessful_status = ["Process Failed!"]
for stat in range(1, 9):
    unsuccessful_status.append(str(stat))


# Update coverage information after each test case
def check_execution(target, fuzz_data_logger, session, sock, *args, **kwargs):
    session_coverage = session.coverage
    # Parse and calculate coverage information
    session_coverage.parse_coverage_result()

    # Check and update bitmap if it has new bits
    hnb = has_new_bit(session_coverage, session_coverage.virgin_bits)
    save_if_interest(session, hnb)

    # Check target execution status
    status = session.last_recv
    if status is not None and "Process Failed!" in status:
        session_coverage.total_crash += 1
        find_unique_crash(session_coverage, status)
    elif status == "Server Error!\n":
        # Server Error: no error message received
        session_coverage.total_crash += 1
        session_coverage.uni_crash += 1
    # else:
    #     stat_index = int(status)
    #     session_coverage.status_hits[stat_index] += 1

    show_stats(session, fuzz_data_logger)
    return


def find_unique_crash(curr_coverage, stack):
    start = stack.find("Call Stack:")
    if start != -1:  # Receive call stack information
        call_stack = stack[start + len("Call Stack:\r\n"):].split("\r\n")
        mem_address = []
        memory_ptn = "^0x[0-9a-zA-Z]+"
        # Extract memory address from call stack for hashing
        for line in call_stack:
            split_line = line.split(" ")
            for data in split_line:
                if re.search(memory_ptn, data):
                    mem_address.append(data)
                    break
        stack_hash = checksum(mem_address)
        if stack_hash not in curr_coverage.crash_stack:
            curr_coverage.crash_stack[stack_hash] = mem_address
            curr_coverage.uni_crash += 1
    else:
        # No call stack information returned from target, we just hash the whole stack information
        stack_hash = checksum(stack)
        if stack_hash not in curr_coverage.crash_stack:
            curr_coverage.crash_stack[stack_hash] = stack
            curr_coverage.uni_crash += 1
    return


def save_if_interest(session, has_new_bits):
    current_cov = session.coverage
    current_mutant = session.fuzz_node.mutant
    favored_list = current_cov.interest
    # Only insert node when it has covered new tuples
    if has_new_bits == 2:
        mutant = QueueEntry(current_mutant)
        mutant.exec_cksum = checksum(current_cov.trace_bits)
        mutant.favored = True
        mutant.exec_us = current_cov.current_exec_us
        mutant.bitmap_size = count_bits(current_cov.trace_bits)
        mutant.nodes_initialized(session.fuzz_node.render_list)

        redundant = False
        for favored in favored_list:
            if mutant.mutant_name == favored.mutant_name and mutant.value == favored.value:
                redundant = True
                break

        last_field = None
        for index in range(len(mutant.node_fields) - 1, -1, -1):
            item = mutant.node_fields[index]
            if item.fuzzable:
                last_field = item._name
                break

        if not redundant and last_field != mutant.mutant_name:
            mutant._render = session.last_send
            mutant.interest_index = len(favored_list)
            favored_list.append(mutant)
            current_cov.new_favored = True
            if mutant.interest_index == 0:
                current_cov.pending_favored += 1
                current_cov.current_favored = mutant
    return


# Select and render the seed which has the highest bitmap size
def select_seed(target, fuzz_data_logger, session, node, edge, *args, **kwargs):
    curr_coverage = session.coverage
    data = b""

    if session.coverage.new_favored:
        cull_favored(curr_coverage)
    if curr_coverage.pending_favored:
        favored = curr_coverage.top_rated[-1]
        if curr_coverage.current_favored is None:
            curr_coverage.current_favored = favored
        elif favored != curr_coverage.current_favored:
            prev_favored = curr_coverage.current_favored
            prev_favored.favored_change(node)

            curr_coverage.current_favored = favored
            favored.pending = True
        if favored.pending and not favored.was_fuzzed:
            favored.pending = False
            # Keep the current mutant in original request tree
            original_mutant = node.names[favored.mutant_name]
            original_mutant.skip_mutation = True
            original_mutant._mutant_index = favored.current_mutant_index
            original_mutant._value = favored.value

            favored.render_list = []
            for item in favored.node_fields:
                data += item.render()
                if isinstance(item, blocks.Block):
                    favored.render_list += item.render_list
                else:
                    favored.render_list.append(item)
        elif not favored.was_fuzzed:
            data = node.render()
            favored.render_list = node.render_list
        fuzz_data_logger.open_test_step("Current pending favored mutate: %s:%s" %
                                        (curr_coverage.current_favored.mutant_name,
                                         repr(curr_coverage.current_favored.value)))
    else:
        data = node.render()

    return data


def cull_favored(cur_coverage):
    favored_queue = cur_coverage.interest
    cur_coverage.new_favored = False
    if len(favored_queue) <= 1:
        cur_coverage.top_rated = copy.copy(favored_queue)
        cur_coverage.pending_favored = len(cur_coverage.top_rated)
        return

    del cur_coverage.top_rated[:]
    # Remove fuzzed favored for sorting
    favored_queue = []
    for favored in cur_coverage.interest:
        if not favored.was_fuzzed:
            favored_queue.append(favored)

    def sort_favored(x):
        return x.bitmap_size * (len(x.node_fields) * -1)

    cur_coverage.top_rated = sorted(favored_queue, key=sort_favored)
    cur_coverage.pending_favored = len(cur_coverage.top_rated)
    return


def restart_callback(target, fuzz_data_logger, session, sock):
    try:
        data = target.recv(constant.buffer_size)
        if not data:
            raise
    except socket.error:
        session.fuzz_node.reset()
        target.close()
        exit(1)
    return


def has_new_bit(curr_coverage, virgin_map):
    current = curr_coverage.trace_bits
    virgin = virgin_map
    iterate = constant.map_size
    index = 0
    ret = 0
    current_non_255_bits = count_non_255_bits(virgin)
    while iterate > 0:
        if current[index]:
            virgin[index] &= ~current[index]
            ret = 1
        index += 1
        iterate -= 1
    new_non_255_bits = count_non_255_bits(virgin)
    if current_non_255_bits != new_non_255_bits:
        ret = 2
    return ret


# Set up bitmap when the session start. Only execute one time.
def setup_bitmap(session):
    if not hasattr(session, 'coverage') or session.coverage is None:
        session.coverage = coverage.Coverage()
        session.coverage.init_count_class16()
    return


# Calculate bitmap coverage
def show_stats(session, fuzz_data_logger):
    curr_coverage = session.coverage
    edge_bits = count_non_255_bits(curr_coverage.virgin_bits)
    stmt_bits = count_bits(curr_coverage.statement_bits)
    statement = (float(stmt_bits) * 100) / curr_coverage.total_statement
    edge = (float(edge_bits) * 100) / curr_coverage.total_edge
    curr_coverage.bitmap_state['statement'] = statement
    curr_coverage.bitmap_state['edge'] = edge

    # Log necessary information for analysis
    hit_stmt = []
    for index, bit in enumerate(curr_coverage.statement_bits):
        if bit:
            hit_stmt.append(index)
    curr_coverage.hit_stmt_index = sorted(hit_stmt)

    hit_edge = []
    for index, bit in enumerate(curr_coverage.virgin_bits):
        if bit != 255:
            hit_edge.append(index)

    fuzz_data_logger.log_info(
        "Total Crash: %d (%d unique); Statement coverage: %d (%.2f%%); Edge coverage: %d (%.2f%%)" %
        (curr_coverage.total_crash, curr_coverage.uni_crash, stmt_bits, statement, edge_bits, edge)
    )
    coverage_stat = open(".\\\\coverage_stat\\\\coverage_stat_" + curr_coverage.init_timestamp + ".txt", "a")
    coverage_stat.write(
        "\nMessage%d: %s\r\nTime: %s\n\rFavored seed:%d\r\nHit functions:%d\r\nBitmap_state:%s\r\nHit statements:%s\r\n"
        "Status hits:%s\r\nHit edges:%s\r\nBlock Trace:%s\r\n" %
        (session.total_mutant_index, repr(session.last_send), helpers.get_time_stamp(), len(curr_coverage.interest),
         len(curr_coverage.hit_function), curr_coverage.bitmap_state, curr_coverage.hit_stmt_index,
         curr_coverage.status_hits, sorted(hit_edge), json.dumps(curr_coverage.trace)))
    coverage_stat.close()
    return


# Count bits set in a bitmap. Non zero value.
def count_bits(bitmap):
    count = 0
    for bit in bitmap:
        if bit:
            count += 1
    return count


def count_non_255_bits(bitmap):
    count = 0
    for bit in bitmap:
        if bit != 255:
            count += 1
    return count
