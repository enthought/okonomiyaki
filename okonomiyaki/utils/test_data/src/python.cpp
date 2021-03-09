#include <iostream>
#ifndef PYTHON_VERSION
#error PYTHON_VERSION macro needs to be defined
#endif
#ifndef PYTHON_ARCH
#error PYTHON_ARCH macro needs to be defined
#endif

int main()
{
  std::cout << PYTHON_VERSION;
  std::cout << "\n";
  std::cout << PYTHON_ARCH;
  std::cout << "\n";
}
