/* Random number utilities */
#include "strand.h"
#include "shared/common.h"

#include <dos.h>

void seedRandom() {
    srand(getTimeOfDay());
}

int randMul(uint16 arg) {
    /* DOS rand() is 15-bit; mask host rand() so native builds keep the same
     * scaling range and bit pattern. */
    return ((rand() & 0x7fff) * (long)arg) >> 0xf;
}
