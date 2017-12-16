@echo off
echo Activate pyenv..
call C:\Users\yura\pyvenv\yonchienv\Scripts\activate
call python setup.py build

xcopy logic\drivers build\exe.win32-3.6\drivers\ /e
copy tcl86t.dll build\exe.win32-3.6\
copy tk86t.dll build\exe.win32-3.6\
copy config.ini build\exe.win32-3.6\

rmdir build\exe.win32-3.6\lib\logic\drivers /s /q
del build\exe.win32-3.6\lib\ui\config.ini

echo Building complete!

