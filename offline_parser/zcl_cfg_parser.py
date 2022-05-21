import sys
import json
import random
import re

MAP_SIZE = 65536


class BlockEntry:
    def __init__(self):
        self.block_number = 1
        self.location = 0
        self.succs = []
        self.statements = []

    def add_statement(self, stmt):
        self.statements.append(int(stmt))

    def num_statements(self):
        return len(self.statements)

    def toJSON(self):
        return json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=4)


class Function:
    def __init__(self):
        self.name = ""
        self.coverage = 0.0
        self.total_blocks = 1
        self.block_list = []

        initblock = BlockEntry()
        self.block_list.append(initblock)

    def add_block(self, block_entry):
        self.block_list.append(block_entry)

    def num_statements(self):
        total_stmt = 0
        for block in self.block_list:
            total_stmt += block.num_statements()
        return total_stmt

    def toJSON(self):
        return json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=4)


class Module:
    def __init__(self):
        self.name = ""
        self.coverage = 0.0
        self.total_functions = 0
        self.function_list = []
        self.total_statements = 0

    def add_function(self, function):
        self.function_list.append(function)

    def num_statements(self):
        total_stmt = 0
        for function in self.function_list:
            total_stmt += function.num_statements()
        return total_stmt

    def toJSON(self):
        return json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=4)


skip_function = ['zcl_Init', 'zcl_event_loop']
module_function_prefix = ";; Function"
block_prefix = "  <bb"
stmt_pattern = "[zcl.c]:[0-9]+:[0-9]+"
line_prefix = "Line"
module_prefix = "Module "
coverage_function_prefix = "Function "


def parse_zcl_cfg(module, cfg_file):
    cfg = open(cfg_file, "r")
    func_new = False
    block_new = False
    module.name = 'zcl'

    for line in cfg:
        if not func_new and module_function_prefix in line:
            fname = line.lstrip(module_function_prefix).split()[0]
            if fname not in skip_function and "register" not in fname:  # Find a new function
                current_function = Function()
                current_function.name = fname
                module.total_functions += 1
                module.add_function(current_function)
                func_new = True
        elif func_new and "succs" in line:  # Initialize block list and successors of each block for each function
            succs_line = line.split()
            block_no = succs_line[1]
            current_block = BlockEntry()
            current_block.block_number = block_no
            current_block.location = random.randint(1, MAP_SIZE)

            # Find successors of the current block
            succs_start = succs_line.index('{')
            succs_end = succs_line.index('}')
            succs_array = []
            for number in range(succs_start + 1, succs_end):
                succs_array.append(int(succs_line[number]))
            current_block.succs = succs_array
            current_function.add_block(current_block)
            current_function.total_blocks += 1
            block_new = False
        elif func_new and block_prefix in line:
            new_block_number = line.split()[1].rstrip('>')
            current_block = current_function.block_list[int(new_block_number) - 1]
            block_new = True
        elif block_new and re.findall(stmt_pattern, line):
            stmt_line_number = line.split()[0].split(':')[-2]
            if int(stmt_line_number) not in current_block.statements:
                current_block.add_statement(stmt_line_number)
        elif '}' in line:
            func_new = False
            block_new = False
    zcl_module.total_statements = zcl_module.num_statements()
    cfg.close()


# ----------------------------------------------------------- #
if __name__ == "__main__":
    if len(sys.argv) > 1:
        zcl_module = Module()
        parse_zcl_cfg(zcl_module, sys.argv[1])
        if zcl_module.total_functions > 0:
            cfg = open("zcl_cfg.json", "w")
            cfg.write(zcl_module.toJSON())
            cfg.close()
    else:
        print("Please provide CFG file of ZCL library.")
