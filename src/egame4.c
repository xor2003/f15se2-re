#include <dos.h>
#define MK_FP(seg, ofs) ((void far *)(((unsigned long)(seg) << 16) | (ofs)))

/* External function declaration for graphics overlay */
extern unsigned int far gfx_jump_32(void);

/**
 * Loads F15DGTL.BIN cockpit file into memory
 * 
 * This function performs:
 * 1. Calls graphics routine to determine buffer size
 * 2. Allocates DOS memory (via INT 21h/48h)
 * 3. Stores buffer segment in BIOS data area (0:0x4FE)
 * 4. Reads file contents into allocated memory
 * 5. Returns bytes read or closes file on error
 * 
 * Compiler notes:
 * - Uses direct call to graphics overlay function
 * - Uses int86() for DOS interrupts
 * - Uses union REGS for register access
 * - /Ot optimization for compact code
 */
unsigned int loadF15DgtlBin(void) {
    /* Declare all variables at function start */
    union REGS inregs, outregs;
    struct SREGS segregs;
    unsigned int allocSize;
    unsigned int f15dgtlAddr;
    unsigned int bytesRead = 0;
    unsigned int handle;
    unsigned int bytesToRead;
    char *filename = "F15DGTL.BIN";
    unsigned int far *biosPtr;
    
    /* Direct call to graphics overlay function */
    allocSize = gfx_jump_32();  /* Returns buffer size hint in AX */
    
    /* Adjust requested size */
    allocSize -= 2;
    if (allocSize > 0xFFF) {
        allocSize = 0xFFF; /* Cap at 4095 paragraphs */
    }
    
    /* DOS memory allocation (INT 21h/48h) */
    inregs.h.ah = 0x48;
    inregs.x.bx = allocSize;
    int86(0x21, &inregs, &outregs);
    if (outregs.x.cflag) return 0; /* Allocation failed */
    f15dgtlAddr = outregs.x.ax;
    
    /* Store segment in BIOS data area (0:0x4FE) */
    biosPtr = (unsigned int far *)MK_FP(0, 0x4FE);
    *biosPtr = f15dgtlAddr;
    
    /* Open file (INT 21h/3Dh) */
    inregs.h.ah = 0x3D;
    inregs.h.al = 0; /* Read-only mode */
    inregs.x.dx = (unsigned int)filename;
    segregs.ds = segregs.es; /* Set DS to data segment */
    int86x(0x21, &inregs, &outregs, &segregs);
    if (outregs.x.cflag) return 0; /* File open failed */
    handle = outregs.x.ax;
    
    /* Calculate bytes to read (paragraphs * 16) */
    bytesToRead = allocSize << 4;
    
    /* Read file contents (INT 21h/3Fh) */
    inregs.h.ah = 0x3F;
    inregs.x.bx = handle;
    inregs.x.cx = bytesToRead;
    inregs.x.dx = 0; /* Offset 0 in segment */
    segregs.ds = f15dgtlAddr; /* Set DS to buffer segment */
    int86x(0x21, &inregs, &outregs, &segregs);
    if (outregs.x.cflag) goto close_file; /* Read error */
    bytesRead = outregs.x.ax;
    
close_file:
    /* Close file (INT 21h/3Eh) */
    inregs.h.ah = 0x3E;
    inregs.x.bx = handle;
    int86(0x21, &inregs, &outregs);
    
    return bytesRead;
}