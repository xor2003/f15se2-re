#include <dos.h>
#define MK_FP(seg, ofs) ((void far *)(((unsigned long)(seg) << 16) | (ofs)))

/* Global variables */
unsigned char ovlInsaneFlag;  /* Flag for alternate execution path */
unsigned char _gfx_jump_0_alloc[256]; /* Jump table for overlay functions */

/* Constants from the assembly */
#define OVL_HDR_FIRSTIDX 0x1C
#define OVL_HDR_SLOTCOUNT 0x22
#define OVL_HDR_FIRSTPTR 0x24
#define OVL_HDR_CODESEG  0x18

/**
 * Sets up overlay slots by initializing function pointers
 * 
 * @param segment Segment address of the overlay header
 * 
 * Compiler notes:
 * - Uses direct memory access via MK_FP
 * - Matches original assembly logic
 */
void setupOverlaySlots(unsigned int segment) {
    unsigned int i;
    unsigned int firstIdx, slotCount, codeSeg;
    unsigned int *slotPtr;
    unsigned char *jumpEntry;
    
    ovlInsaneFlag = 0;   /* Default to normal path */
    
    /* Access the overlay header via far pointer */
    firstIdx = *((unsigned int far *)MK_FP(segment, OVL_HDR_FIRSTIDX));
    slotCount = *((unsigned int far *)MK_FP(segment, OVL_HDR_SLOTCOUNT));
    codeSeg = *((unsigned int far *)MK_FP(segment, OVL_HDR_CODESEG));
    slotPtr = (unsigned int far *)MK_FP(segment, OVL_HDR_FIRSTPTR);
    
    /* Calculate the starting position in the jump table */
    jumpEntry = &_gfx_jump_0_alloc[firstIdx * 5];
    
    for (i = 0; i < slotCount; i++) {
        /* Each jump table entry is 5 bytes: 
         *   [0] = opcode (0xEA for jmp far)
         *   [1-2] = offset
         *   [3-4] = segment
         */
        jumpEntry[0] = 0xEA;   /* jmp far opcode */
        *((unsigned int far *)(jumpEntry+1)) = *slotPtr;  /* offset */
        *((unsigned int far *)(jumpEntry+3)) = codeSeg;   /* segment */
        
        slotPtr++;        /* Next slot pointer (each is 2 bytes) */
        jumpEntry += 5;   /* Next jump table entry */
    }
    
    if (ovlInsaneFlag) {
        /* The assembly has a retn here for the alternate path, but in C we just return */
        return;
    }
}