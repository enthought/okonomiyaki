cl /c /TP /MT /O1 /GS- /Oi- python.c /D PYTHON_VERSION=\"2.7.9\" /Fopython_279.obj
link /NODEFAULTLIB /ENTRY:main python_279.obj user32.lib kernel32.lib
call python_279.exe
cl /c /TP /MT /O1 /GS- /Oi- python.c /D PYTHON_VERSION=\"2.7.10\" /Fopython_2710.obj
link /NODEFAULTLIB /ENTRY:main python_2710.obj user32.lib kernel32.lib
call python_2710.exe
cl /c /MT /TP /O1 /GS- /Oi- python.c /D PYTHON_VERSION=\"3.4.1\" /Fopython_341.obj
link /NODEFAULTLIB /ENTRY:main python_341.obj user32.lib kernel32.lib
call python_341.exe
cl /c /MT /TP /O1 /GS- /Oi- python.c /D PYTHON_VERSION=\"3.5.1\" /Fopython_351.obj
link /NODEFAULTLIB /ENTRY:main python_351.obj user32.lib kernel32.lib
call python_351.exe
cl /c /MT /TP /O1 /GS- /Oi- python.c /D PYTHON_VERSION=\"3.6.5\" /Fopython_365.obj
link /NODEFAULTLIB /ENTRY:main python_365.obj user32.lib kernel32.lib
call python_365.exe
