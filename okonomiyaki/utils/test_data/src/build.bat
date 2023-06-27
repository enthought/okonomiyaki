rem %1 should be 64bit or 32bit dependening on the python bitness we are building for

cl -nologo -EHsc -GR -Zc:forScope -Zc:wchar_t /D PYTHON_VERSION=\"2.7.9\" /D PYTHON_ARCH=\"%1\" /Fopython_279.obj python.cpp
call python_279.exe
cl -nologo -EHsc -GR -Zc:forScope -Zc:wchar_t /D PYTHON_VERSION=\"2.7.10\" /D PYTHON_ARCH=\"%1\" /Fopython_2710.obj python.cpp
call python_2710.exe
cl -nologo -EHsc -GR -Zc:forScope -Zc:wchar_t /D PYTHON_VERSION=\"3.4.1\" /D PYTHON_ARCH=\"%1\" /Fopython_341.obj python.cpp
call python_341.exe
cl -nologo -EHsc -GR -Zc:forScope -Zc:wchar_t /D PYTHON_VERSION=\"3.5.1\" /D PYTHON_ARCH=\"%1\" /Fopython_351.obj python.cpp
call python_351.exe
cl -nologo -EHsc -GR -Zc:forScope -Zc:wchar_t /D PYTHON_VERSION=\"3.6.5\" /D PYTHON_ARCH=\"%1\" /Fopython_365.obj python.cpp
call python_365.exe
cl -nologo -EHsc -GR -Zc:forScope -Zc:wchar_t /D PYTHON_VERSION=\"3.8.8\" /D PYTHON_ARCH=\"%1\" /Fopython_388.obj python.cpp
call python_388.exe
cl -nologo -EHsc -GR -Zc:forScope -Zc:wchar_t /D PYTHON_VERSION=\"3.11.2\" /D PYTHON_ARCH=\"%1\" /Fopython_3112.obj python.cpp
call python_3112.exe
