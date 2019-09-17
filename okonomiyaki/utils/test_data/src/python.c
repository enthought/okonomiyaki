#include <windows.h>
#ifndef PYTHON_VERSION
#error PYTHON_VERSION macro needs to be defined
#endif

extern "C" size_t strlen(const char *f)
{
  INT i=0;
  while(*f++) i++;
  return i;
}
void printf(char * fmtstr, ...)
{
  DWORD dwRet;
  CHAR buffer[256];
  va_list v1;
  va_start(v1,fmtstr);
  wvsprintf(buffer,fmtstr,v1);
  WriteConsole(GetStdHandle(STD_OUTPUT_HANDLE), buffer, strlen(buffer), &dwRet, 0);
  va_end(v1);
}
int main()
{
  printf("%s\n", PYTHON_VERSION);
  return 0;
}
