@echo off 
set _cspybat="C:\Program Files (x86)\IAR Systems\Embedded Workbench 8.3\common\bin\cspybat"
set _zstack_dir=F:\Workspace\zstack_iar_zf\
set _cov="%_zstack_dir%Coverage\coverage.txt"
set _debug_config="%_zstack_dir%settings\zstack.Debug.general.xcl"
set _debug_file="%_zstack_dir%Debug\Exe\zstack.out"
set _driver="%_zstack_dir%settings\zstack.Debug.driver.xcl"

@echo on 

%_cspybat% --silent -f %_debug_config% --debug_file %_debug_file%  --code_coverage_file %_cov% --backend -f %_driver% 

@echo off 
