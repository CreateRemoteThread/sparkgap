all: main.c
	sdcc -lstm8 -mstm8 --out-fmt-ihx --std-sdcc11 main.c

flash:
	./stm8flash -c stlinkv2 -p stm8l001j3m3 -w main.ihx
