#include <dos.h>

/* Function pointer for interrupt handler */
typedef void (interrupt far *INTHANDLER)();
INTHANDLER oldCBreakHandler;

/**
 * Custom CTRL-Break handler
 * 
 * Simply returns without passing control to DOS
 */
void interrupt far newHandler() {
    /* Acknowledge interrupt without passing to DOS */
    return;
}

/**
 * Installs custom CTRL-Break handler
 * 
 * Replaces the default DOS CTRL-Break handler with a custom
 * function that prevents program termination. This allows the
 * game to handle break signals gracefully.
 * 
 * Compiler notes:
 * - Uses _dos_getvect and _dos_setvect for interrupt handling
 * - Uses standard C syntax without advanced function pointers
 * - /Ot optimization for compact code
 */
void installCBreakHandler(void) {
    /* Get current CTRL-Break handler (INT 0x1B) */
    oldCBreakHandler = _dos_getvect(0x1B);
    
    /* Set new handler */
    _dos_setvect(0x1B, newHandler);
}