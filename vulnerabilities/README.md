# Vulnerabilities in Z-Stack Implementation

We have detected several vulnerabilities with Z-Fuzzer on Z-Stack 3.0.1, developed by Texas Instruments.

Here we list the detected vulnerabilities and ZCL messages to discover those crashes.

## Target

We performed test with Z-Fuzzer on TI CC2538 devices with the SmartRF06 Evaluation Board.
We compiled and programmed Z-Stack 3.0.1 source code to the device.

## Vulnerabilities
1. Crash in function ``` [CVE-2020-27890] zclParseInWriteCmd() ```   

   The embedded device will fail to update the specific attribute's value if receives a malformed ZCL message with command identifier setting to 0x05, which means a Write Attributes No Response message.

2. Crash in function ``` [CVE-2020-27891] zclHandleExternal() ```

   The embedded device will crash if receives a malformed ZCL message with command identifier setting to 0x09, which means a Read Reporting Configuration Response message.
   
3. Crash in function ``` [CVE-2020-27892] zclParseInDiscCmdsRspCmd() ```

   The embedded device will crash if receives a ZCL message with command identifier setting to 0x12 or 0x14, which which means a Discover Commands Received Response message or a Discover Commands Generated Response message.
