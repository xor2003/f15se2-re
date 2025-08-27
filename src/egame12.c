// seg000 debug code (/Zi)
#include "debug.h"
#include "egame.h"
#include "offsets.h"
#include "pointers.h"
#include "slot.h"
#include "const.h"
#include "comm.h"

#include <dos.h>
#include <stdio.h>
#include <string.h>

// ==== seg000:0x3f72 ====
int otherKeyDispatch(void) {
    // Local variables corresponding to the stack frame (sub sp, 3Eh)
    int16 var_3E, var_3C, var_38, var_34, var_32, var_2C, var_2A, var_28,
     var_24, var_22, var_20, var_1A, var_18, var_16, var_14, var_10,
     var_E, var_C;

    // Helper variables for complex calculations
    //register 
    int16 temp_si;
    int16 temp_di;
    int16 temp_ax, temp_bx, temp_cx;
    int32 temp_long_dx_ax;
    int16 temp_1, temp_2, temp_3, temp_4, temp_5;

    if (word_3BECC == 0) {
        word_3AFA6 = 
        word_380E0 = 
        word_3A944 = 
        word_380D0 = 
        word_380CE = 
        word_380CC = 
        word_380CA = 0;

        if (gameData->difficulty == 0) {
            
            word_380C8 = ((word_3BED0 - (waypoints[1].y)) < 0x8000) ? 0 : 0x8000;
        } else {
            word_380C8 = (gameData->theater == 6)
               ? 0  // If true, the result is 0
               : ((gameData->theater & 1) ? 0 : 0x8000); // Else, evaluate the second condition
        }

        if (stru_3AA5E[word_3B148].field_6 & 0x200) {
            *((unsigned char*)&word_380C8 + 1) += 4;
        }

        sub_15411();
        sub_15FDB();
        word_3BECC = 1;
    }

    keyScancode = 0;
    if (_kbhit()) {
        keyScancode = __bios_keybrd(0);
        if (word_336EA == 1) {
            word_3370E = 
            word_336EA = 
            keyValue = 0;
        }
    }

    while (_kbhit()) {
        __bios_keybrd(0); // Flush keyboard buffer
    }

    // Main key dispatch logic
    switch (keyScancode) {
        case 0x0C2D: // Minus
            word_380E0 = sub_1CF64(word_380E0 - 10, 0, 100);
            sub_15FDB();
            goto switch_break;
        case 0x0D3D: // Equal
            word_380E0 = sub_1CF64(word_380E0 + ((word_380E0 < 10) ? 5 : 10), 0, 100);
            sub_15FDB();
            *((unsigned char*)&word_391FE) &= 0xF7; // ~8
            goto switch_break;
        case 0x1E61: // A
            word_380E0 = 0x90;
            sub_15FDB();
            *((unsigned char*)&word_391FE) &= 0xF7; // ~8
            goto switch_break;
        case 0x0D2B: // Shift-Equal
            word_380E0 = 100;
            sub_15FDB();
            *((unsigned char*)&word_391FE) &= 0xF7; // ~8
            goto post_key_B_check;
        case 0x0C5F: // Shift-Minus
            word_380E0 = 0;
            makeSound(0x10, 0);
            sub_15FDB();
            goto switch_break;
        case 0x3062: // B
            *((unsigned char*)&word_391FE) ^= 8;
        post_key_B_check:
            if (!(*((unsigned char*)&word_391FE) & 8) && word_3BEBE != 0 && word_380E0 == 100) {
                word_3A944 = 0x546;
                makeSound(0x1C, 2);
            }
            goto switch_break;
        case 0x2400: // Alt-J
            if (word_380E2 == 0) {
                sub_2265B();
                word_380E2 = 40;
            }
            goto switch_break;
        case 0x1000: // Alt-Q
            sub_11B37(1);
            exitCode = 0;
            goto switch_break;
        case 0x3000: // Alt-B
            if (word_330C2 != 0) {
                gfx_jump_2a(off_38364[0], 0, 0x61, off_38334[0], 0, 0x61, 0x140, 0x67);
            }
            sub_19E44(0);
            sub_19E5D(0, 0, 0x13F, 0xC7);
            TransformAndProjectObject(0, 0, 0x71, 0x37, 0x0C, 7, 0);
            sub_1613B();
            if (word_330C2 != 0) {
                gfx_jump_2a(off_38364[0], 0, 0x61, off_38334[0], 0, 0x61, 0x140, 0x67);
                gfx_jump_2a(off_38364[0], 0, 0x61, off_3834C[0], 0, 0x61, 0x140, 0x67);
                sub_15FDB();
            }
            goto switch_break;
        case 0x1900: // Alt-P
            sub_1613B();
            goto switch_break;
    }

switch_break:
    if (word_380E2 > 0) {
        word_380E2--;
    }

    if (word_380E0 != 0 && word_3AFA6 == 0) {
        makeSound(0x0E, 2);
    }

    if (word_330BE != 0) {
        noJoy80 = 0;
        noJoy80_2 = 0;
    } else {
        if (commData->setupUseJoy != 0) {
            sub_2267E();
        } else {
           
            //temp_si = word_38602 + 1;
            noJoy80 = (unsigned char)(((int)((unsigned char)byte_37F98 - 0x80) * (word_38602 + 1)) / 3) - 0x80;
           
            noJoy80_2 = (unsigned char)(((int)((unsigned char)byte_37F99 - 0x80) * (word_38602 + 1)) / 3) - 0x80;
        }
    }

    word_3C00E = ((uint16)noJoy80 >> 4) - 8;
    if (word_3C00E < 0) word_3C00E++;

    word_3C5A4 = ((uint16)noJoy80_2 >> 4) - 8;
    if (word_3C5A4 < 0) word_3C5A4++;
    
    word_3C00E = -((abs(word_3C00E) + 2) * word_3C00E) * 2;
    word_3C5A4 *= 6;
    if (word_3C5A4 < 0) {
        word_3C5A4 /= 2;
    }
    
    if (word_3BEBE == word_380CE && word_3C5A4 < 0 && word_380CA <= 0) {
        word_3C5A4 = 0;
    }

    if (word_3AA5A > 0x15E && !(*((unsigned char*)&word_391FE) & 1) && word_336EC != 0) {
        word_336EC = 0;
        *((unsigned char*)&word_391FE) |= 1;
        tempStrcpy("Landing gear raised");
        makeSound(0x20, 2);
    }
    
    if (word_3BEBE == word_380CE && word_380E0 == 0 && !(*((unsigned char*)&word_391FE) & 8)) {
        *((unsigned char*)&word_391FE) |= 8;
        tempStrcpy("Brakes on");
    }

    if (word_3C00E != 0 || word_3C5A4 != 0) {
        word_330B6 = 0;
    }
    
    if (word_330B6 != 0) {
        var_2C = (word_336EA != 0) ? 
                 (int16)((word_38FE0 & 0xF) << 8) - 0x800
                 : 0;
        
        var_2C = forceRange(var_2C - word_380C8 + word_3BE92, 0xEC00, 0x1400) * 2;
        
        word_3C00E = -sub_1CF64((var_2C - word_380CC) >> 6, -24, 24);
        
        var_14 = forceRange(((word_330B6 - word_380CE) << 4) - word_38FC4, 0xEC00, 0xC00);
        
        word_3C5A4 = sub_1CF64((var_14 - word_380CA) >> 7, -8, 8);
    }
    
    if (waypointIndex == 3) {
        var_3E = word_3AFA8;
        var_10 = word_3B15A;
        

        var_2A = stru_3AA5E[var_10].field_0 - word_3BEC0;
        var_34 = stru_3AA5E[var_10].field_2 - word_3BED0;

        if (!(stru_3AA5E[var_10].field_6 & 0x200)) {
            var_3E = -abs_word(var_34);
        }

        var_34 += ((stru_3AA5E[var_10].field_6 & 0x200) ? 0x1E : 0x40) * var_3E;
        
        var_2C = abs(word_380C8);
        if (var_3E == -1) {
            var_2A = -var_2A;
            var_34 = -var_34;
            var_2C = abs(word_380C8 - 0x8000);
        }

        var_14 = sub_1CF64((abs(var_2A) + abs(var_34)) * 2 + var_2C / 32, 50, 0x1000);
        if (var_14 < 0x1000) {
            sub_1DB9C();
        }

        if (stru_3AA5E[var_10].field_6 & 0x200) {
            var_14 += 100;
        }

        if (word_33702 != 0 && abs(var_2C) < 0x200) {
            var_14 = -20;
        }

        var_34 = stru_3AA5E[var_10].field_2 + (((stru_3AA5E[var_10].field_6 & 0x200) ? 0x1C : 0x38) * var_3E);

        var_34 += sub_1CF64((abs(var_2A) * 4) + (var_2C / 16), 0, 0xC00) * var_3E;
        
        *((unsigned char*)&word_391FE) &= 0xF7;
        
        if (var_2C > 0x4000) {
            var_2A = stru_3AA5E[var_10].field_0;
            var_14 = 0x1000;
        } else {
            var_2A = stru_3AA5E[var_10].field_0 + (var_2A * var_3E * 2);
            if (word_380E0 * 80 < word_3AA5A) {
                 *((unsigned char*)&word_391FE) |= 8;
            }
        }
        
        var_E = ARCTAN(var_2A - word_3BEC0, word_3BED0 - var_34);
        var_3C = (int16)word_3AA5A / 16;

        var_2C = forceRange(var_E - word_380C8, (-var_3C) << 8, var_3C << 8) * 2;

        if (word_33702 != 0) {
            var_2C = 0;
        }
        
        word_3C00E = -sub_1CF64((var_2C - word_380CC) >> 6, -32, 32);

        word_380E0 = sub_1CF64((var_14 / 64) + (abs(var_2C) / 128), 35, 80);
        sub_15FDB();
        
        var_14 = forceRange(((var_14 - word_380CE) >> 3) + (word_38FC4 >> 7), -24, 24);
        
        word_3C5A4 = sub_1CF64(var_14 - (word_380CA >> 7), -16, 16);
        
        if (word_3AA5A < 0x15E) {
            *((unsigned char*)&word_391FE) &= 0xFE;
        }

        if (word_3BEBE == word_380CE) {
            word_380E0 = 0;
            word_3C00E = 0;
            word_391FE |= 8;
            word_3C5A4 = 0;
        }
    }
    
    if (gameData->unk4 != 0) {
        var_24 = ((int32)word_3AA5A * (1000 - word_380CE)) >> 15;
    } else {
        var_24 = 0;
    }
    
    if (!((word_391FE) & 1)) {
        var_24 += sub_1CF64((word_3AA5A - 200) >> 5, 0, 32);
    }
    
    if (var_24 > 0 && ((uint16)word_3BEBE) < ((uint16)word_380CE)) {
        word_3C00E += randlmul(var_24) - (var_24 >> 1);
        word_3C5A4 += (randlmul(var_24) - (var_24 >> 1)) >> 1;
    }
    
    if ((word_391FE & 1) && word_3C5A4 <= 0 && ((uint16)word_3A944) < ((uint16)word_3A8FE) && gameData->unk4 < 2 && abs(word_380CC) < 0x3000 && word_38FE8 == 0) {
        var_14 = ((((word_38FC4) - (word_380CA)) >> 2) - word_380CE + 300) >> 2;
        if (var_14 > 0) {
            word_3C5A4 = sub_1CF64(var_14, 0, 32);
        }
    }
    
    if (word_3BE3C != 0) {
        //int16 pitch_input_modifier;
        //int16 stall_decay_effect;
        int16 bailout_index;

        word_3C00E = 0x40;

        word_3C5A4 = (abs(word_380CC) > 0x4000) ? 0x10 : -8; // pitch_input_modifier
        
        //word_3BE3C++;
        word_3C040 += sub_1CF64(
            - (++word_3BE3C - 0x20),
            (int16)0xFF00 / word_330C4,
            (int16)0x80 / word_330C4
        );
        //word_3C040 += stall_decay_effect;

        if (word_3C040 < 0) {
            word_3C040 = 0;
            if ((word_38FE0 & 7) == 0) {
                sub_11B37(0);
            }
        }

        if (word_380CE == 0 && word_336F6 == -1) {
            word_336F6 = 0;
            stru_3AA5E[0].field_0 = word_3BEC0;
            stru_3AA5E[0].field_2 = word_3BED0;
            word_3BEBC = word_3BEC0;
            word_3BEC8 = word_3BED0;
            word_3BECE = 0;
            word_39606 = -8;
            makeSound(2, 2);
            word_380E0 = 
            word_3A944 = 0;
        }

        if ((word_3BE3C & 0xFFFC) == 0x10 && (word_336E8 & 3) == 1) {
            word_336F6 = -1;

            bailout_index = ((uint16)word_336E8 / 2) & 7;

            stru_33402[bailout_index].field_0 = word_3BEC0;
            stru_33402[bailout_index].field_2 = word_3BED0;
            stru_33402[bailout_index].field_4 = word_380CE;

            stru_33402[bailout_index].field_6 = randlmul(0x20) << 11;

            word_33442 = bailout_index;
            word_3BEBC = word_3BEC0;
            word_3BEC8 = word_3BED0;
            word_3BECE = word_380CE;
            word_39606 = -8;
            makeSound(0, 2);

            word_380CA = -0x4000;
            byte_380DD = 1;
        }
    }
    
    if (word_3BF90 != 0) {
        if (word_380E0 > -((word_3BF90 * 4) - 0x90)) {
            word_380E0 = -((word_3BF90 * 4) - 0x90);
            if (word_380E0 < 0)
                word_380E0 = 0;
            sub_15FDB();
        }
    }
    
    word_3AFA6 += ((word_380E0 - word_3AFA6) / 4) / ((int16)word_330C4);
    if (word_380E0 > word_3AFA6) word_3AFA6++;
    if (word_380E0 < word_3AFA6) word_3AFA6 = word_380E0;

    if ((((uint16)word_336E8) % ((uint16)(word_330C4 << 1))) == 0 && word_380E0 != 0 && word_336EA == 0) {
        word_33098 -= ((word_380E0 * word_380E0) / 750) + 2;
        sub_1606C();
    }
    
    if (word_33098 <= 0) {
        word_3AFA6 = 0;
        word_33098 = 0;
    }

    word_38FDA = byte_37FEC[(abs(word_380CC) >> 8) & 0x7f];
    if (((uint16)word_3BEBE) < ((uint16)word_380CE)) {
        word_38FDA += word_3C5A4 / 2;
    }
    
    if (word_38FDA > 0x80) {
        word_38FDA = 0x80;
        word_3C5A4 = sub_1CF64(0x80 - byte_37FEC[(abs(word_380CC) >> 8) & 0x7f], 0, word_3C5A4);
    }
    
    
    _strcpy(unk_38FD0, _itoa(word_38FDA / 16, strBuf, 10));
    _strcat(unk_38FD0, ".");
    
    _strcat(unk_38FD0, _itoa((abs(word_38FDA) & 0xF) >> 1, strBuf, 10));
    _strcat(unk_38FD0, "G");

    var_32 = (((int32)(word_3AFA6 - sub_1D178(word_380CA, 80))) * ((int32)800)) / ((int32)100);
    
    word_3C5A6 = 100;
    var_32 = (( ((uint32)(((uint16)word_380CE >> 7) + 0x0400)) * ((int32)(var_32)) ) >> 10);
     
    word_3C5A6 = (uint32)((int32)100 * (int32)((word_380D0 >> 6) + 0x0400)) >> 10;
    
    var_32 = ((int32)var_32) * ((int32)(-((word_33098 >> 9) - 100))) / (int32)90;
    
    var_32 = (((int32)var_32) * ((int32)(128 - word_38FDA))) >> 7;
    
    word_3C5A6 = ((int32)sub_15557(word_38FDA * 4) * (int32)word_3C5A6) >> 8;
    word_3C5A6 = abs(word_3C5A6);

    if (!(*((unsigned char*)&word_391FE) & 1)) {
        var_32 -= var_32 >> 3;
    }
    
    word_3A8FE = word_3C5A6 * 27;
    var_1A = sub_1CF64(var_32, 0, 900) * 27;
    
    word_3A944 += ((((int32)var_1A - word_3A944) / 16) / (int32)word_330C4);
    
    word_3B4DA = ((int32)word_3A8FE * 3072) / (abs(word_3A944) + 1);
    if ((uint16)word_3B4DA > 0x2000) word_3B4DA = 0x2000;
    
    word_38FC4 = sub_1D190(word_380CC, word_3B4DA - 0x300);
    
    if (*((unsigned char*)&word_391FE) & 8) {
        if (word_3BEBE == word_380CE) {
            word_3A944 -= (-((gameData->unk4 * 8) - 32) * 27) / word_330C4;
            if (word_3BEBE != 0 && (uint16)word_3A944 < 0x1B0) {
                 word_3A944 = 0;
            }
        } else {
             word_3A944 -= ((uint16)word_3A944 >> 4) / word_330C4;
        }
    }
    
    if ((uint16)word_3A944 > 0xfc18) word_3A944 = 0;
    
    var_22 = sub_1D190(word_380CA, word_3A944);
    word_3AA5A = (uint16)word_3A944 / 27;
    
    audio_jump_6a(word_3AA5A, word_3AFA6);
    
    var_18 = (((int32)sub_1D178(word_380CC, word_38FDA << 4)) << 7) / ((int32)((int16)((uint16)word_3A944 >> 9) + 0x20));

    var_18 = sub_1D190(word_380CA, var_18);
    
    if (word_3BEBE == word_380CE) {
        var_18 = (word_3C00E * -1) << 6;
        word_3C00E = 0;
        if (word_3AA5A < word_3C5A6) {
            word_3C5A4 = 0;
        }
    }
    
    if (word_38FDE != 0) {
        word_3C5A4 = -2000 - word_380CA;
        word_3A944 = 
        word_380E0 = 0;
    }
    
    var_28 = (((int32)word_3C00E) << 7) / ((int32)word_330C4);
    if (var_28 != 0) {
        word_380AC = word_380A4 = sub_13B86(var_28);
        word_380A6 = sub_13B96(var_28);
        word_380AA = -word_380A6;
        sub_151F9(unk_3806E, word_380A4);
    }
    
    var_20 = (int16)((int32)word_3C5A4 << 7) / word_330C4;
    if (var_20 != 0) {
        word_380A2 = word_3809A = sub_13B86(var_20);
        word_380A0 = sub_13B96(var_20);
        word_3809C = -word_380A0;
        sub_151F9(unk_3806E, unk_38092);
    }
    
    var_16 = (int16)var_18 / word_330C4;
    if (var_16 != 0) {
        word_38090 = word_38080 = sub_13B86(var_16);
        word_38084 = sub_13B96(var_16);
        word_3808C = -word_38084;
        sub_151F9(word_38080, unk_3806E);
    }
    
    sub_15237();

    if (word_3A944 > word_3A8FE && word_3BEBE < word_380CE) {
        temp_cx = (gameData->unk4 == 2 || word_3BF90 > 8) ? 1 : 2;
        word_380CA -= (word_3A8FE - word_3A944) >> temp_cx;
        byte_380DD = 1;
        if (word_380CA < 0 && word_380CE < 200) {
            makeSound(0x14, 1);
        }
    }

    if (word_3BEBE == word_380CE) {
        if (word_380CC != 0) {
            word_380CC = 0;
            byte_380DD = 1;
        }
        if (word_380CA > 0 && word_3AA5A < word_3C5A6) {
            if (word_38FDE == 0) {
                word_380CA = 0;
            }
            byte_380DD = 1;
        }
    }
    
    word_38FDE = 0;

    temp_ax = abs(word_380CC) >> 1;
    temp_si = abs(word_380CA);
    byte_3C6A0 = (temp_si - temp_ax > 0x1000) ? 1 : 0;
    
    if (byte_380DD) {
        sub_15411();
    }
    
    var_C = word_380D0;
    temp_ax = sub_13B96(word_380CA - word_38FC4);
    word_3C8B6 = sub_13B2F((word_3A944 / 10), temp_ax);

    if (word_33712 == 0) {
        word_380D0 += (word_3C8B6 / word_330C4);
        
        temp_ax = sub_13B96(word_380C8);
        temp_ax = sub_13B2F(var_22, temp_ax);
        temp_long_dx_ax = (int32)(temp_ax / 10) / word_330C4;
        dword_3B7DA += temp_long_dx_ax;

        temp_ax = sub_13B86(word_380C8);
        temp_ax = sub_13B2F(var_22, temp_ax);
        temp_long_dx_ax = (int32)(temp_ax / 10) / word_330C4;
        dword_3B7F8 += temp_long_dx_ax;
    }
    
    if (word_380D0 > word_3BEBE || word_380D0 < -4000) {
        word_380D0 = word_3BEBE;
    }
    if (word_380D0 > 0xEA60) word_380D0 = 0xEA60;
    
    if (word_380D0 < 0x2000) {
        word_380CE = word_380D0;
    } else if (word_380D0 < 0x4000) {
        word_380CE = ((word_380D0 - 0x2000) >> 1) + 0x2000;
    } else {
        word_380CE = ((word_380D0 - 0x4000) >> 2) + 0x3000;
    }

    if (word_3BEBE == word_380CE) {
        if (var_C > word_3BEBE && word_33702 != 0) {
            makeSound(0xC, 2);
            temp_bx = word_3C16A << 4;
            temp_cx = (stru_3AA5E[temp_bx].field_6 & 0x200) ? 0x100 : 0x80;

            temp_ax = -word_3C8B6 * word_330B8;
            temp_ax = (int16)temp_ax >> 1;

            if (temp_cx < temp_ax) {
                if (gameData->unk4 != 0 && !(*((unsigned char*)&word_391FE) & 1)) {
                    temp_ax = abs(word_380CC);
                    temp_cx = (int16)((30 * word_330B8) + 1);
                    if ((int16)temp_ax > (int16)(30 / temp_cx)) {
                        makeSound(0, 2);
                        sub_12278(0x3C);
                        sub_11B37(5);
                    }
                }
            }
        }
        word_3C8B6 = 0;
    }
    
    temp_ax = word_336E8 & 0xF;
    var_38 = temp_ax;
    temp_si = temp_ax << 4;
    stru_3A95A[temp_si].field_A = word_380C8;
    stru_3A95A[temp_si].field_C = word_380CA;
    stru_3A95A[temp_si].field_E = word_380CC;
    *(int32*)&stru_3A95A[temp_si].field_0 = dword_3B7DA;
    *(int32*)&stru_3A95A[temp_si].field_4 = dword_3B7F8;
    stru_3A95A[temp_si].field_8 = word_380CE;

    if (word_3C45C == 1) {
        if (word_336F2 >= 0) {
            temp_si = word_336F2 * 0x24;
            
            temp_ax = xydist(word_3BEC0 - word_3B204[temp_si], word_3BED0 - word_3B206[temp_si]);
            temp_ax = (temp_ax * word_330C4) >> 8;
            var_38 = sub_1CF64(temp_ax, 0, 12);

        } else {
            var_38 = word_330C4 - 1;
        }

        var_38 = (word_336E8 - var_38) & 0xF;
        
        temp_si = var_38 << 4;

        var_2C = word_380C8 - stru_3A95A[temp_si].field_A;
        var_14 = word_380CA - stru_3A95A[temp_si].field_C;

        temp_di = sub_1D178(word_380CC, (var_14 >> 2));
        temp_ax = sub_1D190(word_380CC, -(var_2C >> 2));
        word_3C6A4 = temp_di + temp_ax;

        temp_di = sub_1D190(word_380CC, (var_14 >> 1));
        temp_ax = sub_1D178(word_380CC, (var_2C >> 2));
        word_3C6AC = temp_di + temp_ax;
    }

    return 0; 
} // 51f9

