:: Runs python script for automatized download of Sentinel SLC data
::
@echo off

:: Make sure R:\ (radarski) is mapped
net use r: /delete
net use r: \\iaps-64tera\radarski /persistent:yes

:: PYTHON VIRTUAL ENVIRONMENT USED
set py_env=C:\Users\ncoz\AppData\Local\conda\conda\envs\apiSentinel
set py_path=%py_env%\bin;
set py_path=%py_env%\Scripts;%py_path%
set py_path=%py_env%\Library\bin;%py_path%
set py_path=%py_env%\Library\usr\bin;%py_path%
set py_path=%py_env%\Library\mingw-w64\bin;%py_path%
set py_path=%py_env%;%py_path%

:: Set PATH variable to include pyhton virtual env
set PATH=%py_path%%PATH%

:: LOCATION OF PYTHON SCRIPT
set py_script=D:\nejc\auto_dwn_slc\auto_dwn_slc.py

:: Run python script
python %py_script%

rem pause
