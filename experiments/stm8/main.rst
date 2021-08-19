                                      1 ;--------------------------------------------------------
                                      2 ; File Created by SDCC : free open source ANSI-C Compiler
                                      3 ; Version 3.8.0 #10562 (Linux)
                                      4 ;--------------------------------------------------------
                                      5 	.module main
                                      6 	.optsdcc -mstm8
                                      7 	
                                      8 ;--------------------------------------------------------
                                      9 ; Public variables in this module
                                     10 ;--------------------------------------------------------
                                     11 	.globl _main
                                     12 ;--------------------------------------------------------
                                     13 ; ram data
                                     14 ;--------------------------------------------------------
                                     15 	.area DATA
                                     16 ;--------------------------------------------------------
                                     17 ; ram data
                                     18 ;--------------------------------------------------------
                                     19 	.area INITIALIZED
                                     20 ;--------------------------------------------------------
                                     21 ; Stack segment in internal ram 
                                     22 ;--------------------------------------------------------
                                     23 	.area	SSEG
      FFFFFF                         24 __start__stack:
      FFFFFF                         25 	.ds	1
                                     26 
                                     27 ;--------------------------------------------------------
                                     28 ; absolute external ram data
                                     29 ;--------------------------------------------------------
                                     30 	.area DABS (ABS)
                                     31 
                                     32 ; default segment ordering for linker
                                     33 	.area HOME
                                     34 	.area GSINIT
                                     35 	.area GSFINAL
                                     36 	.area CONST
                                     37 	.area INITIALIZER
                                     38 	.area CODE
                                     39 
                                     40 ;--------------------------------------------------------
                                     41 ; interrupt vector 
                                     42 ;--------------------------------------------------------
                                     43 	.area HOME
      008000                         44 __interrupt_vect:
      008000 82 00 80 07             45 	int s_GSINIT ; reset
                                     46 ;--------------------------------------------------------
                                     47 ; global & static initialisations
                                     48 ;--------------------------------------------------------
                                     49 	.area HOME
                                     50 	.area GSINIT
                                     51 	.area GSFINAL
                                     52 	.area GSINIT
      008007                         53 __sdcc_gs_init_startup:
      008007                         54 __sdcc_init_data:
                                     55 ; stm8_genXINIT() start
      008007 AE 00 00         [ 2]   56 	ldw x, #l_DATA
      00800A 27 07            [ 1]   57 	jreq	00002$
      00800C                         58 00001$:
      00800C 72 4F 00 00      [ 1]   59 	clr (s_DATA - 1, x)
      008010 5A               [ 2]   60 	decw x
      008011 26 F9            [ 1]   61 	jrne	00001$
      008013                         62 00002$:
      008013 AE 00 00         [ 2]   63 	ldw	x, #l_INITIALIZER
      008016 27 09            [ 1]   64 	jreq	00004$
      008018                         65 00003$:
      008018 D6 80 23         [ 1]   66 	ld	a, (s_INITIALIZER - 1, x)
      00801B D7 00 00         [ 1]   67 	ld	(s_INITIALIZED - 1, x), a
      00801E 5A               [ 2]   68 	decw	x
      00801F 26 F7            [ 1]   69 	jrne	00003$
      008021                         70 00004$:
                                     71 ; stm8_genXINIT() end
                                     72 	.area GSFINAL
      008021 CC 80 04         [ 2]   73 	jp	__sdcc_program_startup
                                     74 ;--------------------------------------------------------
                                     75 ; Home
                                     76 ;--------------------------------------------------------
                                     77 	.area HOME
                                     78 	.area HOME
      008004                         79 __sdcc_program_startup:
      008004 CC 80 5B         [ 2]   80 	jp	_main
                                     81 ;	return from main will return to caller
                                     82 ;--------------------------------------------------------
                                     83 ; code
                                     84 ;--------------------------------------------------------
                                     85 	.area CODE
                                     86 ;	main.c: 17: static inline void delay_ms(uint16_t ms) {
                                     87 ;	-----------------------------------------
                                     88 ;	 function delay_ms
                                     89 ;	-----------------------------------------
      008024                         90 _delay_ms:
      008024 52 08            [ 2]   91 	sub	sp, #8
                                     92 ;	main.c: 19: for (i = 0; i < ((F_CPU / 18000UL) * ms); i++)
      008026 5F               [ 1]   93 	clrw	x
      008027 1F 07            [ 2]   94 	ldw	(0x07, sp), x
      008029 1F 05            [ 2]   95 	ldw	(0x05, sp), x
      00802B                         96 00103$:
      00802B 1E 0B            [ 2]   97 	ldw	x, (0x0b, sp)
      00802D 89               [ 2]   98 	pushw	x
      00802E 4B 78            [ 1]   99 	push	#0x78
      008030 4B 03            [ 1]  100 	push	#0x03
      008032 CD 80 FD         [ 4]  101 	call	___muluint2ulong
      008035 5B 04            [ 2]  102 	addw	sp, #4
      008037 1F 03            [ 2]  103 	ldw	(0x03, sp), x
      008039 17 01            [ 2]  104 	ldw	(0x01, sp), y
      00803B 1E 07            [ 2]  105 	ldw	x, (0x07, sp)
      00803D 13 03            [ 2]  106 	cpw	x, (0x03, sp)
      00803F 7B 06            [ 1]  107 	ld	a, (0x06, sp)
      008041 12 02            [ 1]  108 	sbc	a, (0x02, sp)
      008043 7B 05            [ 1]  109 	ld	a, (0x05, sp)
      008045 12 01            [ 1]  110 	sbc	a, (0x01, sp)
      008047 24 0F            [ 1]  111 	jrnc	00105$
                                    112 ;	main.c: 20: __asm__("nop");
      008049 9D               [ 1]  113 	nop
                                    114 ;	main.c: 19: for (i = 0; i < ((F_CPU / 18000UL) * ms); i++)
      00804A 1E 07            [ 2]  115 	ldw	x, (0x07, sp)
      00804C 5C               [ 1]  116 	incw	x
      00804D 1F 07            [ 2]  117 	ldw	(0x07, sp), x
      00804F 26 DA            [ 1]  118 	jrne	00103$
      008051 1E 05            [ 2]  119 	ldw	x, (0x05, sp)
      008053 5C               [ 1]  120 	incw	x
      008054 1F 05            [ 2]  121 	ldw	(0x05, sp), x
      008056 20 D3            [ 2]  122 	jra	00103$
      008058                        123 00105$:
                                    124 ;	main.c: 21: }
      008058 5B 08            [ 2]  125 	addw	sp, #8
      00805A 81               [ 4]  126 	ret
                                    127 ;	main.c: 27: void main() 
                                    128 ;	-----------------------------------------
                                    129 ;	 function main
                                    130 ;	-----------------------------------------
      00805B                        131 _main:
      00805B 52 14            [ 2]  132 	sub	sp, #20
                                    133 ;	main.c: 29: PB_DDR |= (1 << PB_CONFIRM);
      00805D 72 1C 50 07      [ 1]  134 	bset	20487, #6
                                    135 ;	main.c: 30: PB_CR1 |= (1 << PB_CONFIRM);
      008061 72 1C 50 08      [ 1]  136 	bset	20488, #6
                                    137 ;	main.c: 31: PC_DDR |= (1 << LED_PIN) | (1 << LED_CONFIRM); // configure PD4 as output
      008065 C6 50 0C         [ 1]  138 	ld	a, 0x500c
      008068 AA 05            [ 1]  139 	or	a, #0x05
      00806A C7 50 0C         [ 1]  140 	ld	0x500c, a
                                    141 ;	main.c: 32: PC_CR1 |= (1 << LED_PIN) | (1 << LED_CONFIRM); // push-pull mode
      00806D C6 50 0D         [ 1]  142 	ld	a, 0x500d
      008070 AA 05            [ 1]  143 	or	a, #0x05
      008072 C7 50 0D         [ 1]  144 	ld	0x500d, a
                                    145 ;	main.c: 38: PB_ODR |= (1 << PB_CONFIRM);
      008075 72 1C 50 05      [ 1]  146 	bset	20485, #6
                                    147 ;	main.c: 39: z = 0;
      008079 5F               [ 1]  148 	clrw	x
      00807A 1F 0B            [ 2]  149 	ldw	(0x0b, sp), x
      00807C 1F 09            [ 2]  150 	ldw	(0x09, sp), x
                                    151 ;	main.c: 40: for(x =0;x < 200;x++)
      00807E 5F               [ 1]  152 	clrw	x
      00807F 1F 13            [ 2]  153 	ldw	(0x13, sp), x
      008081 1F 11            [ 2]  154 	ldw	(0x11, sp), x
      008083                        155 00114$:
                                    156 ;	main.c: 42: for(y = 0;y < 200;y++)
      008083 AE 00 C8         [ 2]  157 	ldw	x, #0x00c8
      008086 1F 0F            [ 2]  158 	ldw	(0x0f, sp), x
      008088 5F               [ 1]  159 	clrw	x
      008089 1F 0D            [ 2]  160 	ldw	(0x0d, sp), x
      00808B 16 0B            [ 2]  161 	ldw	y, (0x0b, sp)
      00808D 17 07            [ 2]  162 	ldw	(0x07, sp), y
      00808F 16 09            [ 2]  163 	ldw	y, (0x09, sp)
      008091 17 05            [ 2]  164 	ldw	(0x05, sp), y
      008093                        165 00113$:
                                    166 ;	main.c: 44: z += 1;
      008093 1E 07            [ 2]  167 	ldw	x, (0x07, sp)
      008095 5C               [ 1]  168 	incw	x
      008096 1F 07            [ 2]  169 	ldw	(0x07, sp), x
      008098 26 05            [ 1]  170 	jrne	00150$
      00809A 1E 05            [ 2]  171 	ldw	x, (0x05, sp)
      00809C 5C               [ 1]  172 	incw	x
      00809D 1F 05            [ 2]  173 	ldw	(0x05, sp), x
      00809F                        174 00150$:
      00809F 1E 0F            [ 2]  175 	ldw	x, (0x0f, sp)
      0080A1 1D 00 01         [ 2]  176 	subw	x, #0x0001
      0080A4 1F 03            [ 2]  177 	ldw	(0x03, sp), x
      0080A6 7B 0E            [ 1]  178 	ld	a, (0x0e, sp)
      0080A8 A2 00            [ 1]  179 	sbc	a, #0x00
      0080AA 6B 02            [ 1]  180 	ld	(0x02, sp), a
      0080AC 7B 0D            [ 1]  181 	ld	a, (0x0d, sp)
      0080AE A2 00            [ 1]  182 	sbc	a, #0x00
      0080B0 6B 01            [ 1]  183 	ld	(0x01, sp), a
      0080B2 16 03            [ 2]  184 	ldw	y, (0x03, sp)
      0080B4 17 0F            [ 2]  185 	ldw	(0x0f, sp), y
      0080B6 16 01            [ 2]  186 	ldw	y, (0x01, sp)
      0080B8 17 0D            [ 2]  187 	ldw	(0x0d, sp), y
                                    188 ;	main.c: 42: for(y = 0;y < 200;y++)
      0080BA 1E 03            [ 2]  189 	ldw	x, (0x03, sp)
      0080BC 26 D5            [ 1]  190 	jrne	00113$
      0080BE 1E 01            [ 2]  191 	ldw	x, (0x01, sp)
      0080C0 26 D1            [ 1]  192 	jrne	00113$
                                    193 ;	main.c: 40: for(x =0;x < 200;x++)
      0080C2 16 07            [ 2]  194 	ldw	y, (0x07, sp)
      0080C4 17 0B            [ 2]  195 	ldw	(0x0b, sp), y
      0080C6 16 05            [ 2]  196 	ldw	y, (0x05, sp)
      0080C8 17 09            [ 2]  197 	ldw	(0x09, sp), y
      0080CA 1E 13            [ 2]  198 	ldw	x, (0x13, sp)
      0080CC 5C               [ 1]  199 	incw	x
      0080CD 1F 13            [ 2]  200 	ldw	(0x13, sp), x
      0080CF 26 05            [ 1]  201 	jrne	00153$
      0080D1 1E 11            [ 2]  202 	ldw	x, (0x11, sp)
      0080D3 5C               [ 1]  203 	incw	x
      0080D4 1F 11            [ 2]  204 	ldw	(0x11, sp), x
      0080D6                        205 00153$:
      0080D6 1E 13            [ 2]  206 	ldw	x, (0x13, sp)
      0080D8 A3 00 C8         [ 2]  207 	cpw	x, #0x00c8
      0080DB 7B 12            [ 1]  208 	ld	a, (0x12, sp)
      0080DD A2 00            [ 1]  209 	sbc	a, #0x00
      0080DF 7B 11            [ 1]  210 	ld	a, (0x11, sp)
      0080E1 A2 00            [ 1]  211 	sbc	a, #0x00
      0080E3 25 9E            [ 1]  212 	jrc	00114$
                                    213 ;	main.c: 47: if(z == 40000)
      0080E5 1E 07            [ 2]  214 	ldw	x, (0x07, sp)
      0080E7 A3 9C 40         [ 2]  215 	cpw	x, #0x9c40
      0080EA 26 08            [ 1]  216 	jrne	00104$
      0080EC 1E 05            [ 2]  217 	ldw	x, (0x05, sp)
      0080EE 26 04            [ 1]  218 	jrne	00104$
                                    219 ;	main.c: 49: PC_ODR ^= (1 << LED_PIN);
      0080F0 90 14 50 0A      [ 1]  220 	bcpl	20490, #2
      0080F4                        221 00104$:
                                    222 ;	main.c: 51: PB_ODR &= ~(1 << PB_CONFIRM);
      0080F4 72 1D 50 05      [ 1]  223 	bres	20485, #6
                                    224 ;	main.c: 52: while(1)
      0080F8                        225 00106$:
      0080F8 20 FE            [ 2]  226 	jra	00106$
                                    227 ;	main.c: 56: }
      0080FA 5B 14            [ 2]  228 	addw	sp, #20
      0080FC 81               [ 4]  229 	ret
                                    230 	.area CODE
                                    231 	.area CONST
                                    232 	.area INITIALIZER
                                    233 	.area CABS (ABS)
