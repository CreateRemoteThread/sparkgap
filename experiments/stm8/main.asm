;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 3.8.0 #10562 (Linux)
;--------------------------------------------------------
	.module main
	.optsdcc -mstm8
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _main
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area DATA
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area INITIALIZED
;--------------------------------------------------------
; Stack segment in internal ram 
;--------------------------------------------------------
	.area	SSEG
__start__stack:
	.ds	1

;--------------------------------------------------------
; absolute external ram data
;--------------------------------------------------------
	.area DABS (ABS)

; default segment ordering for linker
	.area HOME
	.area GSINIT
	.area GSFINAL
	.area CONST
	.area INITIALIZER
	.area CODE

;--------------------------------------------------------
; interrupt vector 
;--------------------------------------------------------
	.area HOME
__interrupt_vect:
	int s_GSINIT ; reset
;--------------------------------------------------------
; global & static initialisations
;--------------------------------------------------------
	.area HOME
	.area GSINIT
	.area GSFINAL
	.area GSINIT
__sdcc_gs_init_startup:
__sdcc_init_data:
; stm8_genXINIT() start
	ldw x, #l_DATA
	jreq	00002$
00001$:
	clr (s_DATA - 1, x)
	decw x
	jrne	00001$
00002$:
	ldw	x, #l_INITIALIZER
	jreq	00004$
00003$:
	ld	a, (s_INITIALIZER - 1, x)
	ld	(s_INITIALIZED - 1, x), a
	decw	x
	jrne	00003$
00004$:
; stm8_genXINIT() end
	.area GSFINAL
	jp	__sdcc_program_startup
;--------------------------------------------------------
; Home
;--------------------------------------------------------
	.area HOME
	.area HOME
__sdcc_program_startup:
	jp	_main
;	return from main will return to caller
;--------------------------------------------------------
; code
;--------------------------------------------------------
	.area CODE
;	main.c: 17: static inline void delay_ms(uint16_t ms) {
;	-----------------------------------------
;	 function delay_ms
;	-----------------------------------------
_delay_ms:
	sub	sp, #8
;	main.c: 19: for (i = 0; i < ((F_CPU / 18000UL) * ms); i++)
	clrw	x
	ldw	(0x07, sp), x
	ldw	(0x05, sp), x
00103$:
	ldw	x, (0x0b, sp)
	pushw	x
	push	#0x78
	push	#0x03
	call	___muluint2ulong
	addw	sp, #4
	ldw	(0x03, sp), x
	ldw	(0x01, sp), y
	ldw	x, (0x07, sp)
	cpw	x, (0x03, sp)
	ld	a, (0x06, sp)
	sbc	a, (0x02, sp)
	ld	a, (0x05, sp)
	sbc	a, (0x01, sp)
	jrnc	00105$
;	main.c: 20: __asm__("nop");
	nop
;	main.c: 19: for (i = 0; i < ((F_CPU / 18000UL) * ms); i++)
	ldw	x, (0x07, sp)
	incw	x
	ldw	(0x07, sp), x
	jrne	00103$
	ldw	x, (0x05, sp)
	incw	x
	ldw	(0x05, sp), x
	jra	00103$
00105$:
;	main.c: 21: }
	addw	sp, #8
	ret
;	main.c: 27: void main() 
;	-----------------------------------------
;	 function main
;	-----------------------------------------
_main:
	sub	sp, #20
;	main.c: 29: PB_DDR |= (1 << PB_CONFIRM);
	bset	20487, #6
;	main.c: 30: PB_CR1 |= (1 << PB_CONFIRM);
	bset	20488, #6
;	main.c: 31: PC_DDR |= (1 << LED_PIN) | (1 << LED_CONFIRM); // configure PD4 as output
	ld	a, 0x500c
	or	a, #0x05
	ld	0x500c, a
;	main.c: 32: PC_CR1 |= (1 << LED_PIN) | (1 << LED_CONFIRM); // push-pull mode
	ld	a, 0x500d
	or	a, #0x05
	ld	0x500d, a
;	main.c: 38: PB_ODR |= (1 << PB_CONFIRM);
	bset	20485, #6
;	main.c: 39: z = 0;
	clrw	x
	ldw	(0x0b, sp), x
	ldw	(0x09, sp), x
;	main.c: 40: for(x =0;x < 200;x++)
	clrw	x
	ldw	(0x13, sp), x
	ldw	(0x11, sp), x
00114$:
;	main.c: 42: for(y = 0;y < 200;y++)
	ldw	x, #0x00c8
	ldw	(0x0f, sp), x
	clrw	x
	ldw	(0x0d, sp), x
	ldw	y, (0x0b, sp)
	ldw	(0x07, sp), y
	ldw	y, (0x09, sp)
	ldw	(0x05, sp), y
00113$:
;	main.c: 44: z += 1;
	ldw	x, (0x07, sp)
	incw	x
	ldw	(0x07, sp), x
	jrne	00150$
	ldw	x, (0x05, sp)
	incw	x
	ldw	(0x05, sp), x
00150$:
	ldw	x, (0x0f, sp)
	subw	x, #0x0001
	ldw	(0x03, sp), x
	ld	a, (0x0e, sp)
	sbc	a, #0x00
	ld	(0x02, sp), a
	ld	a, (0x0d, sp)
	sbc	a, #0x00
	ld	(0x01, sp), a
	ldw	y, (0x03, sp)
	ldw	(0x0f, sp), y
	ldw	y, (0x01, sp)
	ldw	(0x0d, sp), y
;	main.c: 42: for(y = 0;y < 200;y++)
	ldw	x, (0x03, sp)
	jrne	00113$
	ldw	x, (0x01, sp)
	jrne	00113$
;	main.c: 40: for(x =0;x < 200;x++)
	ldw	y, (0x07, sp)
	ldw	(0x0b, sp), y
	ldw	y, (0x05, sp)
	ldw	(0x09, sp), y
	ldw	x, (0x13, sp)
	incw	x
	ldw	(0x13, sp), x
	jrne	00153$
	ldw	x, (0x11, sp)
	incw	x
	ldw	(0x11, sp), x
00153$:
	ldw	x, (0x13, sp)
	cpw	x, #0x00c8
	ld	a, (0x12, sp)
	sbc	a, #0x00
	ld	a, (0x11, sp)
	sbc	a, #0x00
	jrc	00114$
;	main.c: 47: if(z == 40000)
	ldw	x, (0x07, sp)
	cpw	x, #0x9c40
	jrne	00104$
	ldw	x, (0x05, sp)
	jrne	00104$
;	main.c: 49: PC_ODR ^= (1 << LED_PIN);
	bcpl	20490, #2
00104$:
;	main.c: 51: PB_ODR &= ~(1 << PB_CONFIRM);
	bres	20485, #6
;	main.c: 52: while(1)
00106$:
	jra	00106$
;	main.c: 56: }
	addw	sp, #20
	ret
	.area CODE
	.area CONST
	.area INITIALIZER
	.area CABS (ABS)
