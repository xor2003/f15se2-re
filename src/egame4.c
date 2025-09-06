#include "egame.h"
#include <stdlib.h> /* For abs() */

/*
Replicates the integer square root function at seg000:5557.
It uses an iterative method to find the root.
- An initial guess is made (n / 4).
- The guess is refined in a loop by averaging the guess and (n / guess).
- The loop terminates when the guess is stable.
*/
int sub_15557(int n) // Sqrt(int n)
{
    int quotient;
    int guess;

    n = abs(n);

    if (n < 4)
    {
        return 1;
    }
    /* Initial guess = n / 4. The assembly uses two signed arithmetic shifts
       to the right, which is equivalent to a signed division by 4. */
    guess = n >> 2;

    /* This do-while loop structure perfectly matches the assembly's
       logic of executing the block once and then checking the condition
       with a 'jg' at the end to jump back to the top. */
    do
    {
        quotient = n / guess;
        guess = (guess + quotient) >> 1; /* (guess + quotient) / 2 */
    } while (abs(guess - quotient) > 1);

    return guess;
}
