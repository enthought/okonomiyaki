#include <stdio.h>

#ifndef PYTHON_VERSION
#error PYTHON_VERSION macro needs to be defined
#endif

int main(void)
{
	printf("%s\n", PYTHON_VERSION);
	return 0;
}
