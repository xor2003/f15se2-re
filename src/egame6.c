#include <dos.h>

extern unsigned char byte_34197;
extern unsigned short word_330BC;
extern unsigned char dacValues1[];
extern unsigned char dacValues[];
extern unsigned char otherDacValues[];
extern unsigned char byte_37116[];
extern unsigned char byte_36D86[];

void setupDac()
{
    /* All variables must be declared at start of block for pre-C89 compatibility */
    union REGS inregs, outregs;
    int i;                  /* Loop counter */
    unsigned char* dacPtr;  /* DAC register pointer */
    
    /* Set first block of DAC registers (0x10-0x5F) */
    inregs.h.ah = 0x10;
    inregs.h.al = 0x12;
    inregs.x.bx = 0x10;
    inregs.x.cx = 0x50;
    inregs.x.dx = (unsigned short)dacValues1;  // Symbol without underscore
    int86(0x10, &inregs, &outregs);

    /* Special handling for certain video modes */
    if (byte_34197 != 2) {
        /* Copy palette data (48 bytes) */
        for (i = 0; i < 0x30; i++) {
            byte_36D86[i] = byte_37116[i];  // Symbols without underscores
        }
    }

    /* Set second block of DAC registers (0x60-0xFF) */
    dacPtr = dacValues;
    if (word_330BC != 0) {
        dacPtr = otherDacValues;  /* Use alternate DAC values if flag set */
    }

    inregs.h.ah = 0x10;
    inregs.h.al = 0x12;
    inregs.x.bx = 0x60;
    inregs.x.cx = 0xA0;
    inregs.x.dx = (unsigned short)dacPtr;  // Pointer to unmangled symbol
    int86(0x10, &inregs, &outregs);
}