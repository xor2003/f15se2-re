#include <stdio.h>
#include <dos.h>

/* --- 1. EXTERNAL TYPE AND VARIABLE DEFINITIONS --- */
/* These simulate the kinds of data structures found in a real game project. */

/* A typical game data structure, byte-aligned. */
#pragma pack(1)
struct SomeGameData {
    int   some_value;
    char  name[10];
    char  status_flag;
};
#pragma pack()

/* A structure containing a 32-bit long and a far pointer. */
struct PlayerState {
    long player_score;
    char far *video_buffer;
};

/* External (global) variables that the function will interact with. */
extern struct SomeGameData g_game_data;
extern struct PlayerState  g_player_state;
extern int                 g_flags;
extern int                 g_result_array[10];

/* Prototype for an external function to test calling conventions. */
void external_function(int index, long value);


/* --- 2. THE TEST SUITE FUNCTION --- */
/*
 * This function takes a variety of parameters and uses every major
 * C language structure to exercise the compiler's code generator.
 */
int compiler_idiom_test_suite(int param_int, char* param_string, long param_long, struct SomeGameData far* param_far_ptr)
{
    /* --- PRE-C89: All variables must be declared at the top of the function --- */
    int i;
    int j;
    int result;
    int temp_val;
    int status_code;
    long local_long;
    struct SomeGameData *local_ptr;
    int loop_counter;

    /* --- Simple Assignments and Arithmetic --- */
    result = param_int * 2;
    temp_val = 10;

    /* --- IF / ELSE IF / ELSE Logic --- */
    if (result > 100) {
        result = 100;
    } else if (result < 0) {
        result = 0;
    } else {
        result++;
    }

    /* --- Complex IF with Boolean Logic and Pointer Checks --- */
    /* Look for short-circuiting behavior with && */
    if ((g_flags & 0x01) && param_far_ptr != NULL) {
        /* Accessing a far pointer. Look for 'les bx, ...' instruction. */
        param_far_ptr->status_flag = 1;
    }

    /* --- Pointer and Struct Access (Near Pointer) --- */
    local_ptr = &g_game_data;
    local_ptr->some_value = result;

    /* --- FOR Loop with Array Access --- */
    /* Note that 'i' is declared at the top of the function. */
    for (i = 0; i < 8; i++) {
        g_game_data.name[i] = param_string[i];
        g_result_array[i] = i * result;
    }

    /* --- WHILE Loop --- */
    loop_counter = 5;
    while (loop_counter > 0) {
        temp_val += loop_counter;
        loop_counter--;
    }

    /* --- DO-WHILE Loop (guaranteed to run at least once) --- */
    j = 0;
    do {
        temp_val++;
        j++;
    } while (j < g_game_data.some_value);


    /* --- SWITCH Statement --- */
    /* This is a key test. /Ot will often create a jump table for this, */
    /* while /Zi will create a long chain of "compare and jump". */
    status_code = g_flags & 0xF0;
    switch (status_code) {
        case 0x10:
            result = 1;
            break;
        case 0x20:
            result = 2;
            break;
        case 0x80:
            result = 8;
            /* Deliberate fall-through */
        case 0x90:
            result += 9;
            break;
        default:
            result = -1;
            break;
    }

    /* --- 32-bit LONG Arithmetic --- */
    /* Look for operations using the dx:ax register pair. */
    /* A 32-bit shift is often implemented as a small loop. */
    local_long = param_long << 4; /* long multiplication */
    local_long += g_player_state.player_score;

    /* --- Function Call --- */
    /* Tests the CDECL calling convention (arguments pushed right-to-left). */
    external_function(result, local_long);

    /* --- GOTO Statement --- */
    if (result == -1) {
        goto error_handler;
    }
    result = 1;
    goto end_of_function;

error_handler:
    result = 0;

end_of_function:
    return result;
}
