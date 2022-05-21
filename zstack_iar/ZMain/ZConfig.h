#include <stdio.h>
#include <stdlib.h>
#include "ZComDef.h"
#include "zcl_general.h"
#include "zcl_ota.h"

#define MAX_DATA	256 
#define ZCLTestID 		6
#define ZCL_TEST_ENDPOINT  	8
#define OTA_TEST_ENDPOINT	14
#define TEST_DEVICE_VERSION     0
#define TEST_FLAGS              0

#define TEST_HWVERSION          1
#define TEST_ZCLVERSION         1

/******************************************
 * System variables configuration
 ******************************************/
static char* seedfile = "C:\\\\Users\\\\zfuzzer\\\\zfuzzer\\\\Z-Fuzzer\\\\zstack_iar\\\\seedfile";

const uint16 zclTest_clusterRevision_all = 0x0001; 

const uint8 zclTest_HWRevision = TEST_HWVERSION;
const uint8 zclTest_ZCLVersion = TEST_ZCLVERSION;
const uint8 zclTest_ManufacturerName[] = { 16, 'Z','F','u','z','z','e','r',' ',' ',' ',' ',' ',' ',' ',' ',' ' };
const uint8 zclTest_ModelId[] = { 16, 'U','T','A','C','S','E',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ' };
const uint8 zclTest_DateCode[] = { 16, '2','0','1','9','1','0','3','1',' ',' ',' ',' ',' ',' ',' ',' ' };
const uint8 zclTest_PowerSource = POWER_SOURCE_MAINS_1_PHASE;

uint8 zclTest_LocationDescription[] = { 16, ' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ' };
uint8 zclTest_PhysicalEnvironment = 0;
uint8 zclTest_DeviceEnable = DEVICE_ENABLED;

uint16 zclTest_IdentifyTime;

uint8 zclTestSeq = 1;

#if ZCL_DISCOVER
CONST zclCommandRec_t zclTest_Cmds_Basic[] =
{
  {
    ZCL_CLUSTER_ID_GEN_BASIC,
    COMMAND_BASIC_RESET_FACT_DEFAULT,
    CMD_DIR_SERVER_RECEIVED
  },
  
};
#endif // ZCL_DISCOVER

CONST zclCommandRec_t otaTest_Cmds_Basic[] =
{
  {
    ZCL_CLUSTER_ID_OTA,
	COMMAND_QUERY_NEXT_IMAGE_REQ,
	0x00
  },
  {
    ZCL_CLUSTER_ID_OTA,
	COMMAND_QUERY_NEXT_IMAGE_RSP,
	0x01
  },
  {
    ZCL_CLUSTER_ID_OTA,
	COMMAND_IMAGE_BLOCK_REQ,
	0x00
  },
  {
    ZCL_CLUSTER_ID_OTA,
	COMMAND_IMAGE_BLOCK_RSP,
	0x01
  },
  {
    ZCL_CLUSTER_ID_OTA,
	COMMAND_UPGRADE_END_REQ,
	0x00
  },
  {
    ZCL_CLUSTER_ID_OTA,
	COMMAND_UPGRADE_END_RSP,
	0x01
  },
};

CONST zclAttrRec_t otaTest_Attrs_Basic[] = 
{
  {
    ZCL_CLUSTER_ID_OTA,
    { 
      ATTRID_UPGRADE_SERVER_ID,
      ZCL_DATATYPE_IEEE_ADDR,
      (ACCESS_CONTROL_READ),
      NULL
    }
  },
  {
    ZCL_CLUSTER_ID_OTA,
    { 
      ATTRID_IMAGE_UPGRADE_STATUS,
      ZCL_DATATYPE_ENUM8,
      (ACCESS_CONTROL_READ),
      NULL
    }
  },
};

CONST zclAttrRec_t zclTest_Attrs_All[] =
{
  #ifdef ZCL_IDENTIFY
  // *** Identify Cluster Attribute ***
  {
    ZCL_CLUSTER_ID_GEN_IDENTIFY,
    { // Attribute record
      ATTRID_IDENTIFY_TIME,
      ZCL_DATATYPE_UINT16,
      (ACCESS_CONTROL_READ | ACCESS_CONTROL_WRITE),
      (void *)&zclTest_IdentifyTime
    }
  },
  #endif
  // *** General Basic Cluster Attributes ***
  {
    ZCL_CLUSTER_ID_GEN_BASIC,             
    {  // Attribute record
      ATTRID_BASIC_HW_VERSION,            
      ZCL_DATATYPE_UINT8,                 
      ACCESS_CONTROL_READ,                
      (void *)&zclTest_HWRevision 
    }
  },
  {
    ZCL_CLUSTER_ID_GEN_BASIC,
    { // Attribute record
      ATTRID_BASIC_ZCL_VERSION,
      ZCL_DATATYPE_UINT8,
      ACCESS_CONTROL_READ,
      (void *)&zclTest_ZCLVersion
    }
  },
  {
    ZCL_CLUSTER_ID_GEN_BASIC,
    { // Attribute record
      ATTRID_BASIC_MANUFACTURER_NAME,
      ZCL_DATATYPE_CHAR_STR,
      ACCESS_CONTROL_READ,
      (void *)zclTest_ManufacturerName
    }
  },
  {
    ZCL_CLUSTER_ID_GEN_BASIC,
    { // Attribute record
      ATTRID_BASIC_MODEL_ID,
      ZCL_DATATYPE_CHAR_STR,
      ACCESS_CONTROL_READ,
      (void *)zclTest_ModelId
    }
  },
  {
    ZCL_CLUSTER_ID_GEN_BASIC,
    { // Attribute record
      ATTRID_BASIC_DATE_CODE,
      ZCL_DATATYPE_CHAR_STR,
      ACCESS_CONTROL_AUTH_READ,
      (void *)zclTest_DateCode
    }
  },
  {
    ZCL_CLUSTER_ID_GEN_BASIC,
    { // Attribute record
      ATTRID_BASIC_POWER_SOURCE,
      ZCL_DATATYPE_ENUM8,
      ACCESS_CONTROL_READ,
      (void *)&zclTest_PowerSource
    }
  },
  {
    ZCL_CLUSTER_ID_GEN_BASIC,
    { // Attribute record
      ATTRID_BASIC_LOCATION_DESC,
      ZCL_DATATYPE_CHAR_STR,
      (ACCESS_CONTROL_READ | ACCESS_CONTROL_WRITE),
      NULL
    }
  },
  {
    ZCL_CLUSTER_ID_GEN_BASIC,
    { // Attribute record
      ATTRID_BASIC_PHYSICAL_ENV,
      ZCL_DATATYPE_ENUM8,
      (ACCESS_CONTROL_READ | ACCESS_CONTROL_WRITE),
      (void *)&zclTest_PhysicalEnvironment
    }
  },
  {
    ZCL_CLUSTER_ID_GEN_BASIC,
    { // Attribute record
      ATTRID_BASIC_DEVICE_ENABLED,
      ZCL_DATATYPE_BOOLEAN,
      (ACCESS_CONTROL_READ | ACCESS_CONTROL_WRITE),
      (void *)&zclTest_DeviceEnable
    }
  },
  {
    ZCL_CLUSTER_ID_GEN_BASIC,
    {  // Attribute record
      ATTRID_CLUSTER_REVISION,
      ZCL_DATATYPE_UINT16,
      ACCESS_CONTROL_READ,
      (void *)&zclTest_clusterRevision_all
    }
  },
  {
    ZCL_CLUSTER_ID_GEN_IDENTIFY,
    {  // Attribute record
      ATTRID_CLUSTER_REVISION,
      ZCL_DATATYPE_UINT16,
      ACCESS_CONTROL_READ,
      (void *)&zclTest_clusterRevision_all
    }
  },
};


const cId_t zclTest_InClusterList[] =
{
  ZCL_CLUSTER_ID_GEN_BASIC,
  ZCL_CLUSTER_ID_GEN_IDENTIFY,
  ZCL_CLUSTER_ID_GEN_ON_OFF_SWITCH_CONFIG,
};
#define ZCLTEST_MAX_INCLUSTERS   (sizeof(zclTest_InClusterList) / sizeof(zclTest_InClusterList[0]))


const cId_t zclTest_OutClusterList[] =
{
  ZCL_CLUSTER_ID_GEN_BASIC,
  ZCL_CLUSTER_ID_GEN_ON_OFF_SWITCH_CONFIG,
};
#define ZCLTEST_MAX_OUTCLUSTERS  (sizeof(zclTest_OutClusterList) / sizeof(zclTest_OutClusterList[0]))


#define TEST_MAX_OPTIONS	1
static zclOptionRec_t zclOta_Test_Options[TEST_MAX_OPTIONS] =
{
  {
    ZCL_CLUSTER_ID_OTA,
    ( AF_EN_SECURITY | AF_ACK_REQUEST ),
  },
};

static zclOptionRec_t zclBasic_Test_Options[TEST_MAX_OPTIONS] =
{
  {
    ZCL_CLUSTER_ID_GEN_BASIC,
    (AF_EN_SECURITY | AF_ACK_REQUEST),
  },
}; 

static ZStatus_t zclReadWriteCB( uint16 clusterId, uint16 attrId, uint8 oper, uint8 *pValue, uint16 *pLen );