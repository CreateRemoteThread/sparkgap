#include <stdio.h>

/* ************************************************** */
/* Please modify this value to suit your application */
#define MAXBITS 64
/* Remove the following line to use a pure C version*/
#define ANSIC
/* ************************************************** */

typedef unsigned char DIGIT_T ;

/*
"Contains BIGDIGITS multiple-precision arithmetic code originally
written by David Ireland, copyright (c) 2001-6 by D.I. Management
Services Pty Limited <www.di-mgt.com.au>, and is used with
permission."
*/

/* RSA Library Optimized for PIC18 by Alfredo Ortega ortegaalfredo@gmail.com */

/* Useful macros */

#define MAXDIGITS MAXBITS/8

#define ISODD(x) ((x) & 0x1)
#define ISEVEN(x) (!ISODD(x))
#define mpISODD(x, n) (x[0] & 0x1)
#define mpISEVEN(x, n) (!(x[0] & 0x1))
#define mpNEXTBITMASK(mask, n) do{if(mask==1){mask=HIBITMASK;n--;}else{mask>>=1;}}while(0)

/* Sizes to match */
#define MAX_DIGIT 0xFF
#define MAX_HALF_DIGIT 0x0f	/* NB 'L' */

#define BITS_PER_DIGIT 8
#define BITS_PER_HALF_DIGIT 4
#define HIBITMASK 0x80

#define LOHALF(x) ((DIGIT_T)((x) & MAX_HALF_DIGIT))
#define HIHALF(x) ((DIGIT_T)((x) >> BITS_PER_HALF_DIGIT & MAX_HALF_DIGIT))
#define TOHIGH(x) ((DIGIT_T)((x) << BITS_PER_HALF_DIGIT))

void mpSetZero(DIGIT_T a[], size_t ndigits);

void mpSetEqual(DIGIT_T a[], const DIGIT_T b[], size_t ndigits);

int spMultiply(DIGIT_T p[2], DIGIT_T x, DIGIT_T y);

DIGIT_T spDivide(DIGIT_T *q, DIGIT_T *r, const DIGIT_T u[2], DIGIT_T v);

int mpModExp(DIGIT_T yout[], const DIGIT_T x[],
			const DIGIT_T e[], const DIGIT_T m[], size_t ndigits);

char *copyright_notice(void);
