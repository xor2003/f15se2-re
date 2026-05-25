#include <stdio.h>
#include <stdlib.h>
#include "src/support/support.h"

int main() {
    support_init();
    
    printf("Angle calculation debug:\n");
    printf("uangle(1, 1) = %d (expected ~128)\n", uangle(1, 1));
    printf("uangle(-1, 1) = %d (expected ~384)\n", uangle(-1, 1));
    printf("uangle(1, 0) = %d (expected 0)\n", uangle(1, 0));
    printf("uangle(0, 1) = %d (expected 256)\n", uangle(0, 1));
    
    return 0;
}