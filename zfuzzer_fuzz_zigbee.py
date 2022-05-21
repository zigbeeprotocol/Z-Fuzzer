import lib_zstack
import lib_zstack_constants as constant
from mutation import *


def build_zcl_message():
    s_initialize("AFIncomingMSG")
    with s_block("header"):
        s_group("frame_control", values=constant.frame_control)
        with s_block("manuCode", dep="frame_control", dep_values=constant.manufacturer):
            # s_word(0, endian='<')
            s_static('\x01\x00', name="manu")
        # s_byte(1, name="tranSeq")
        s_static('\x01', name="tranSeq")
        s_group("commandId", values=constant.command_list)
    with s_block("payload"):
        # Read Attribute Command Block
        with s_block("read_attribute", dep="commandId", dep_value='\x00'):
            cmd_read_attribute_render()

        # Read Attribute Response Command Block
        with s_block("read_attribute_rsp", dep="commandId", dep_value='\x01'):
            cmd_read_attribute_rsp_render()

        # Write Attribute Command, Write Attribute Undivided Command, and Write Attribute No Response Block
        write_cmd = constant.hex_list_render([hex(0x02), hex(0x03), hex(0x05)])
        with s_block("write_attribute", dep="commandId", dep_values=write_cmd):
            cmd_write_attribute_render()

        # Write Attribute Response Command Block
        with s_block("write_attribute_rsp", dep="commandId", dep_value='\x04'):
            cmd_write_attribute_rsp_render()

        # Configure Reporting Command Block
        with s_block("config_report", dep="commandId", dep_value='\x06'):
            cmd_config_report_render()

        # Configure Reporting Response Command Block
        with s_block("config_report_rsp", dep="commandId", dep_value='\x07'):
            cmd_config_report_rsp_render()

        # Read Reporting Configuration Command Block
        with s_block("read_report_config", dep="commandId", dep_value='\x08'):
            cmd_read_report_config_render()

        # Read Reporting Configuration Response Command Block
        with s_block("read_report_config_rsp", dep="commandId", dep_value='\x09'):
            cmd_read_report_config_rsp_render()

        # Report Attribute Command Block
        with s_block("report_attribute", dep="commandId", dep_value='\x0a'):
            cmd_report_attribute_render()

        # Default Response Command Block
        with s_block("default_rsp", dep="commandId", dep_value='\x0b'):
            cmd_default_response_render()

        # Discover Attribute Command Block
        disc_attr = constant.hex_list_render([hex(0x0c), hex(0x15)])
        with s_block("discover_attribute", dep="commandId", dep_values=disc_attr):
            cmd_discover_attribute_render()

        # Discover Attribute Response Command Block
        with s_block("discover_attribute_rsp", dep="commandId", dep_value='\x0d'):
            cmd_discover_attribute_rsp_render()

        # Discover Command Received Command Block
        disc_cmd = constant.hex_list_render([hex(0x11), hex(0x13)])
        with s_block("discover_command_received", dep="commandId", dep_values=disc_cmd):
            cmd_discover_command_received_render()

        # Discover Command Received Response Command Block
        with s_block("discover_command_received_rsp", dep="commandId", dep_values=['\x12', '\x14']):
            cmd_discover_command_received_rsp_render()

        # Discover Attributes Ext Response Command Block
        with s_block("discover_attribute_ext_rsp", dep="commandId", dep_value='\x16'):
            cmd_discover_attribute_ext_rsp_render()
    return


def cmd_read_attribute_render():
    with s_block("command0"):
        s_word(0, endian='<', name="attributeId0")

    s_repeat("command0", max_reps=constant.max_attributes, name="repeat_0")
    return


def cmd_read_attribute_rsp_render():
    cmd_status = constant.hex_list_render([hex(0x00), hex(0x86)])
    with s_block("command1"):
        s_word(0, endian='<', name="attributeId1")
        s_group("cmd_status", values=cmd_status)
        # Only include attribute data when status = SUCCESS
        with s_block("attribute_1_1", dep="cmd_status", dep_value='\x00'):
            s_group("data_type1", values=constant.data_type, default_value='\x08')
            # Data type is Array/Set/Bag
            with s_block("attribute_value_1_1", dep="data_type1", dep_values=constant.hex_list_render([hex(0x48), hex(0x50), hex(0x51)])):
                s_group("elem_type_1_1", values=constant.data_type, default_value='\x08')
                s_word(1, endian='<', name="num_elements_1_1")

                with s_block("elements_1_1", dep="num_elements_1_1", dep_values=[0, 65535], dep_compare='!='):
                    s_random("zcltest", min_length=1, max_length=64, step=1, num_mutations=64, name="data_1_1")

                with s_block("repeater_1_1", dep="num_elements_1_1", dep_values=[0, 65535], dep_compare='!='):
                    s_repeat("elements_1_1", max_reps=constant.max_attributes, name="repeat_1_1")

            # Data type is Structure
            with s_block("attribute_value_1_2", dep="data_type1", dep_value='\x4c'):
                s_word(1, endian='<', name="num_elements_1_2")
                with s_block("elements_1_2", dep="num_elements_1_2", dep_values=[0, 65535], dep_compare='!='):
                    s_group("elem_type_1_2", values=constant.data_type, default_value='\x08')
                    s_random("zcltest", min_length=1, max_length=64, step=1, num_mutations=64, name="data_1_2")
                with s_block("repeater_1_2", dep="num_elements_1_2", dep_values=[0, 65535], dep_compare='!='):
                    s_repeat("elements_1_2", max_reps=constant.max_attributes, name="repeat_1_2")

            # Other data types
            with s_block("attribute_value_1_3", dep="data_type1", dep_values=constant.analog_type):
                # cmd_data_type_value_render("data_type2", False)
                s_random("zcltest", min_length=1, max_length=64, step=1, num_mutations=64, name="data_1_3")

    s_repeat("command1", max_reps=constant.max_attributes, name="repeat_1")
    return


def cmd_write_attribute_render():
    with s_block("command2"):
        s_word(0, endian='>', name="attributeId2")
        s_group("data_type2", values=constant.data_type, default_value='\x08')
        # Data type is Array/Set/Bag
        with s_block("attribute_value_2_1", dep="data_type2", dep_values=constant.hex_list_render([hex(0x48), hex(0x50), hex(0x51)])):
            s_group("element_type_2_1", values=constant.data_type, default_value='\x08')
            s_word(1, endian='<', name="num_elements_2_1")

            with s_block("elements_2_1", dep="num_elements_2_1", dep_values=[0, 65535], dep_compare='!='):
                s_random("zcltest", min_length=1, max_length=64, step=1, num_mutations=64, name="data_2_1")

            with s_block("repeater_2_1", dep="num_elements_2_1", dep_values=[0, 65535], dep_compare='!='):
                s_repeat("elements_2_1", max_reps=constant.max_attributes, name="repeat_2_1")

        # Data type is Structure
        with s_block("attribute_value_2_2", dep="data_type2", dep_value='\x4c'):
            s_word(1, endian='<', name="num_elements_2_2")

            with s_block("elements_2_2", dep="num_elements_2_2", dep_values=[0, 65535], dep_compare='!='):
                s_group("element_type_2_2", values=constant.data_type, default_value='\x08')
                s_random("zcltest", min_length=1, max_length=64, step=1, num_mutations=64, name="data_2_2")

            with s_block("repeater_2_2", dep="num_elements_2_2", dep_values=[0, 65535], dep_compare='!='):
                s_repeat("elements_2_2", max_reps=constant.max_attributes, name="repeat_2_2")

        # Other data types
        with s_block("attribute_value_2_3", dep="data_type2", dep_values=constant.analog_type):
            # cmd_data_type_value_render("data_type2", False)
            s_random("zcltest", min_length=1, max_length=64, step=1, num_mutations=64, name="data_2_3")

    s_repeat("command2", max_reps=constant.max_attributes, name="repeat_2")
    return


def cmd_write_attribute_rsp_render():
    attr_status = constant.hex_list_render([hex(0x00), hex(0x86), hex(0x8d), hex(0x88), hex(0x7e), hex(0x87)])
    with s_block("command4"):
        if s_block_start("attribute_status"):
            s_group("attr_status", values=attr_status)
            s_word(0, endian='<', name="attributeId4")
            s_block_end()
    s_repeat("command4", max_reps=constant.max_attributes, name="repeat_4")
    return


def cmd_config_report_render():
    analog_type = constant.hex_list_render([hex(0x21), hex(0x22), hex(0x23), hex(0x24), hex(0x25), hex(0x26), hex(0x27), hex(0x28), hex(0x29),
                   hex(0x2a), hex(0x2b), hex(0x2c), hex(0x2d), hex(0x2e), hex(0x2f), hex(0x38), hex(0x39), hex(0x3a),
                   hex(0xe0), hex(0xe1), hex(0xe2)])
    with s_block("command6"):
        if s_block_start("attribute_record_6"):
            s_group("direction_6", values=constant.hex_list_render([hex(0x00), hex(0x01)]))
            with s_block("attribute_value_6", dep="direction_6", dep_value='\x00'):
                s_word(0, endian='<', name="attributeId6")
                s_group("data_type_6", values=constant.analog_type, default_value='\x08')
                s_word(0, endian='<', name="min_interval_6")
                s_word(0, endian='<', name="max_interval_6")
                # Reportable change field is depending on the data type
                with s_block("reportable_change_6_1", dep="data_type_6", dep_values=analog_type):
                    # cmd_data_type_value_render("data_type_6", True)
                    s_random("zcltest", min_length=1, max_length=64, step=1, num_mutations=64, name="data_6")
                s_word(1, endian='<', name="time_out_6")
            s_block_end()
    s_repeat("command6", max_reps=constant.max_attributes, name="repeat_6")
    return


def cmd_config_report_rsp_render():
    attr_status = constant.hex_list_render([hex(0x00), hex(0x86), hex(0x8c), hex(0x8d), hex(0x87)])
    with s_block("command7"):
        s_group("attr_status_7", values=attr_status)
        s_group("direction_7", values=constant.hex_list_render([hex(0x00), hex(0x01)]))
        s_word(0, endian='<', name="attributeId7")
    s_repeat("command7", max_reps=constant.max_attributes, name="repeat_7")
    return


def cmd_read_report_config_render():
    with s_block("command8"):
        s_group("direction_8", values=constant.hex_list_render([hex(0x00), hex(0x01)]))
        s_word(0, endian='<', name="attributeId8")
    s_repeat("command8", max_reps=constant.max_attributes, name="repeat_8")
    return


def cmd_read_report_config_rsp_render():
    attr_status = constant.hex_list_render([hex(0x00), hex(0x86), hex(0x8c), hex(0x8b)])
    analog_type = constant.hex_list_render([hex(0x21), hex(0x22), hex(0x23), hex(0x24), hex(0x25), hex(0x26), hex(0x27), hex(0x28), hex(0x29),
                   hex(0x2a), hex(0x2b), hex(0x2c), hex(0x2d), hex(0x2e), hex(0x2f), hex(0x38), hex(0x39), hex(0x3a),
                   hex(0xe0), hex(0xe1), hex(0xe2)])
    with s_block("command9"):
        s_group("attr_status_9", values=attr_status)
        s_group("direction_9", values=constant.hex_list_render([hex(0x00), hex(0x01)]))
        s_word(0, endian='<', name="attributeId9")
        with s_block("attribute_value_9_1", dep="direction_9", dep_value='\x00'):
            s_group("data_type_9_1", values=constant.analog_type, default_value='\x08')
            s_word(0, endian='<', name="min_interval_9_1")
            s_word(0, endian='<', name="max_interval_9_1")
            # Reportable change field is depending on the data type
            with s_block("reportable_change_9_1", dep="data_type_9_1", dep_values=analog_type):
                # cmd_data_type_value_render("data_type_9", True)
                s_random("zcltest", min_length=1, max_length=64, step=1, num_mutations=64, name="data_9_1")
        with s_block("attribute_value_9_2", dep="direction_9", dep_value='\x01'):
            s_group("data_type_9_2", values=constant.analog_type, default_value='\x08')
            s_word(0, endian='<', name="min_interval_9_2")
            s_word(0, endian='<', name="max_interval_9_2")
            # Reportable change field is depending on the data type and reporting interval
            with s_block("reportable_change_9_2", dep="data_type_9_2", dep_values=analog_type):
                # cmd_data_type_value_render("data_type_9", True)
                s_random("zcltest", min_length=1, max_length=64, step=1, num_mutations=64, name="data_9_2")
            s_word(1, endian='<', name="time_out_9")
    s_repeat("command9", max_reps=constant.max_attributes, name="repeat_9")
    return


def cmd_report_attribute_render():
    with s_block("command0a"):
        s_word(0, endian='<', name="attributeId0a")
        s_group("data_type_0a", values=constant.analog_type, default_value='\x08')
        s_random("zcltest", min_length=1, max_length=64, step=1, num_mutations=64, name="data_0a")
    s_repeat("command0a", max_reps=constant.max_attributes, name="repeat_a")
    return


def cmd_default_response_render():
    cmd_id = constant.hex_list_render([hex(0x00), hex(0x02), hex(0x03), hex(0x05), hex(0x06), hex(0x08), hex(0x0c),
              hex(0x11), hex(0x13), hex(0x15)])
    with s_block("command0b"):
        s_group("commandId_0b", values=cmd_id)
        s_group("status_0b", values=constant.status_codes)
    return


def cmd_discover_attribute_render():
    with s_block("command0c"):
        s_word(0, endian='>', name="start_attrId")
        s_byte(1, endian='<', name="max_attrIds")
    return


def cmd_discover_attribute_rsp_render():
    with s_block("command0d"):
        # 1 means no more attribute to be discovered
        s_group("discover_complete_0d", values=constant.hex_list_render([hex(0x00), hex(0x01)]))
        if s_block_start("attribute_info"):
            s_word(0, endian='<', name="attributeId0d")
            s_group("attribute_type0d", values=constant.data_type)
            s_block_end()
        s_repeat("attribute_info", max_reps=constant.max_attributes, name="repeat_d")
    return


def cmd_discover_command_received_render():
    with s_block("command11"):
        s_byte(0, endian='<', name="start_cmdId")
        s_byte(1, endian='<', name="max_cmdIds")
    return


def cmd_discover_command_received_rsp_render():
    with s_block("command12"):
        # 1 means no more attribute to be discovered
        s_group("discover_complete_12", values=constant.hex_list_render([hex(0x00), hex(0x01)]))
        if s_block_start("command_info"):
            s_byte(0, endian='<', name="commandId_12")
            s_block_end()
        s_repeat("command_info", max_reps=constant.max_attributes, name="repeat_12")
    return


def cmd_discover_attribute_ext_rsp_render():
    with s_block("command16"):
        # 1 means no more attribute to be discovered
        s_group("discover_complete_16", values=constant.hex_list_render([hex(0x00), hex(0x01)]))
        if s_block_start("attribute_ext"):
            s_word(0, endian='>', name="attributeId16")
            s_group("attribute_type16", values=constant.data_type)
            s_bit_field(0, width=3, name="access_control")
            s_block_end()
        s_repeat("attribute_ext", max_reps=constant.max_attributes, name="repeat_16")
    return


def main():
    session = Session(
        target=Target(connection=SocketConnection("127.0.0.1", 34567, proto='tcp', recv_timeout=90.0)),
        receive_data_after_fuzz=True,
        sleep_time=2.5,
        restart_callbacks=[lib_zstack.restart_callback],
    )

    build_zcl_message()
    session.connect(s_get("AFIncomingMSG"), callback=lib_zstack.select_seed)
    session.register_post_test_case_callback(lib_zstack.check_execution)
    session.fuzz()
    return


# -------------------------------------------------------------- #
if __name__ == '__main__':
    main()

