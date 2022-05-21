import struct
import os

buffer_size = 10000

map_size_pow2 = 16
map_size = 1 << map_size_pow2

proj_dir = os.getcwd()
seed_file = proj_dir + '\\zstack_iar\\seedfile'
coverage_file = proj_dir + '\\zstack_iar\\Coverage\\coverage.txt'
cfg_file = proj_dir + '\\offline_parser\\zcl_cfg.json'
cmd = 'C:\\\\Windows\\\\System32\\\\cmd.exe'
zstack_execution = proj_dir + '\\build\\zstack\\ZStackExecute.bat'
zstack_log_dir = proj_dir + '\\zstack_log\\'

zcl_valid_min_header_len = 3
max_attributes = 10

data_type = [hex(0x00), hex(0x08), hex(0x09), hex(0x0a), hex(0x0b), hex(0x0c), hex(0x0d), hex(0x0e), hex(0x0f),
             hex(0x10), hex(0x18), hex(0x19), hex(0x1a), hex(0x1b), hex(0x1c), hex(0x1d), hex(0x1e), hex(0x1f),
             hex(0x20), hex(0x22), hex(0x23), hex(0x24), hex(0x25), hex(0x26), hex(0x27), hex(0x28), hex(0x29),
             hex(0x2a), hex(0x2b), hex(0x2c), hex(0x2d), hex(0x2d), hex(0x2f), hex(0x30), hex(0x31), hex(0x38),
             hex(0x39), hex(0x3a), hex(0x41), hex(0x42), hex(0x43), hex(0x44), hex(0x48), hex(0x4c), hex(0x50),
             hex(0x51), hex(0xe0), hex(0xe1), hex(0xe2), hex(0xe8), hex(0xe9), hex(0xea), hex(0xf0), hex(0xf1),
             hex(0xff)]
cluster_list = [hex(0x0000), hex(0x0003), hex(0x0007), hex(0x0019)]
frame_control = [hex(0), hex(1), hex(4), hex(5), hex(8), hex(9), hex(12), hex(13), hex(16), hex(17), hex(20), hex(21),
                 hex(24), hex(25), hex(28), hex(29)]
manufacturer = [hex(4), hex(5), hex(12), hex(13), hex(20), hex(21), hex(28), hex(29)]
command_list = [hex(0x00), hex(0x01), hex(0x02), hex(0x03), hex(0x04), hex(0x05), hex(0x06), hex(0x07), hex(0x08),
                hex(0x09), hex(0x0a), hex(0x0b), hex(0x0c), hex(0x0d), hex(0x11), hex(0x12), hex(0x13), hex(0x14),
                hex(0x15), hex(0x16)]
status_codes = [hex(0x00), hex(0x01), hex(0x7e), hex(0x7f), hex(0x80), hex(0x81), hex(0x82), hex(0x83), hex(0x84),
                hex(0x85), hex(0x86), hex(0x87), hex(0x88), hex(0x89), hex(0x8a), hex(0x8b), hex(0x8c), hex(0x8d),
                hex(0x8e), hex(0x8f), hex(0x90), hex(0x91), hex(0x92), hex(0x93), hex(0x94), hex(0x95), hex(0x96),
                hex(0x97), hex(0x98), hex(0x99), hex(0x9a), hex(0xc0), hex(0xc1), hex(0xc2), hex(0xc3)]
analog_type = []
complex_type = [hex(0x48), hex(0x50), hex(0x51), hex(0x4c)]
for node in data_type:
    if node not in complex_type:
        analog_type.append(node)


def hex_list_render(data_list):
    new_list = []
    for data in data_list:
        new_list.append(struct.pack("B", int(data, 16)))
    return new_list


data_type = hex_list_render(data_type)
analog_type = hex_list_render(analog_type)
complex_type = hex_list_render(complex_type)
frame_control = hex_list_render(frame_control)
manufacturer = hex_list_render(manufacturer)
command_list = hex_list_render(command_list)
status_codes = hex_list_render(status_codes)

if __name__ == '__main__':
    print zstack_log_dir+"zstack_result.txt"
