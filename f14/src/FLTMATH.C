#include "library.h"
#include "world.h"
#include "sdata.h"
#include "cockpit.h"
#include "f15defs.h"

extern  SWORD   IntDiv();
extern  UWORD   Iasin(),Iacos();

extern  SWORD   FM[3][3];
extern  UWORD   OurHead;
extern  SWORD   OurPitch, OurRoll;




abs (int x); /* {           // REPLACES REGULAR LIBRARY VERSION !!!!!
    if (x==0x8000) {
        return 0x7fff;
    } else if (x<0) {
        return -x;
    } else {
        return (x);
    }
}
*/
/*<f><s> Integer Math Routines*/

/*******************************************
*                                          *
*   This function performs a division      *
*   of two signed 15 bit fractions.   A/B  *
*                                          *
*******************************************/

SWORD   IntDiv (A,B)

SWORD A,B;
{
    SBYTE   S1 = 1,S2 = 1;
    unsigned long LA,LB;

    if (A < 0)  S1 = -1;

    if (B < 0)  S2 = -1;

    LA = (A<0) ? -A : A;
    LB = (B<0) ? -B : B;

    return ((((LA << 16) / LB) >> 1) * S1 * S2);


}

/*************************************************
*                                                *
*   Function returns a 16 bit Word Degree angle  *
*   of the Arc Sin of A.                         *
*                                                *
*************************************************/


extern int TRGTB[];

unsigned Iasin (A)
int A;
{
    int AA,angl,delta,i;

    if (A==-0x8000) return -0x4000;

    AA = abs(A);
    for (i=(AA>>9)+1; i>=0; i--) {
        if (AA>=TRGTB[i]) {
           delta = TRGTB[i+1] - TRGTB[i];
           angl = ((i)<<8) + (long) 256*(AA-TRGTB[i])/delta;
           break;
        }
    }
    if (A<0) angl = -angl;
    return angl;
}

/*************************************************
*                                                *
*   Function returns a 16 bit Word Degree angle  *
*   of the Arc Cos of A.                         *
*                                                *
*************************************************/

unsigned Iacos (A)
int A;
{
    return 0x4000 - Iasin(A);
}

Sqrt (N)
int N;
{   int A,B;

    N = abs(N);
    if (N<4) return 1;
    B = N>>2;
    do {
        A = N/B;
        B = (B+A)>>1;
    } while (abs(B-A)>1);
    return B;
}

