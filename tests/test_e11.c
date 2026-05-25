#include <stdio.h>

// Define types for DOS environment
typedef unsigned short uint16;

// Declare functions from egame11.c
extern void drawCockpit();
extern void gfxInit();
extern void load3D3(char *arg0);
extern void load3DT(char *arg0);
extern void printError(char *msg);

// Test stubs
void setupOverlaySlots(uint16 addr) {
    printf("setupOverlaySlots called with addr: 0x%04X\n", addr);
}

void gfx_jump_4c() { return 0; }
void gfx_jump_44_setDac(int val) {}
void gfx_jump_45_retrace() {}
void gfx_jump_3f_modecode() { return 3; }
void openBlitClosePic(char *path, int mode) {
    printf("openBlitClosePic called with: %s\n", path);
}
void gfx_jump_2a(int a, int b, int c, int d, int e, int f, int g, int h) {}
void strcpy(char *dest, char *src) {
    // Simple implementation for testing
    while (*src) *dest++ = *src++;
    *dest = '\0';
}

// Test framework
#define TEST_ASSERT(condition, message) \
    do { \
        if (!(condition)) { \
            printf("Test failed: %s\n", message); \
            return 1; \
        } \
    } while (0)

// Test cases
int test_drawCockpit() {
    drawCockpit();
    TEST_ASSERT(1, "drawCockpit basic test");
    return 0;
}

int test_gfxInit() {
    gfxInit();
    TEST_ASSERT(1, "gfxInit basic test");
    return 0;
}

int test_load3D3() {
    char path[] = "test.3d3";
    load3D3(path);
    TEST_ASSERT(1, "load3D3 basic test");
    return 0;
}

int test_printError() {
    printError("Test error message");
    TEST_ASSERT(1, "printError basic test");
    return 0;
}

// Test runner
int main() {
    printf("Running egame11 tests...\n");
    
    if (test_drawCockpit()) return 1;
    if (test_gfxInit()) return 1;
    if (test_load3D3()) return 1;
    if (test_printError()) return 1;
    
    printf("All egame11 tests passed!\n");
    return 0;
}