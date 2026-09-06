ifeq ($(origin CC),default)
CC := m68k-amigaos-gcc
endif
CC ?= m68k-amigaos-gcc
HOSTCC ?= cc
CFLAGS ?= -O2 -Wall -Wextra -Werror
# Keep the CPU and pre-2.0 runtime selection on compile AND link commands.
AMIGAFLAGS := -m68000 -mcrt=nix13
CPPFLAGS ?= -Isrc

TARGET := AmiGuard
SRC := src/main.c src/scanner.c src/signatures.c src/trackdisk.c
OBJ := $(SRC:.c=.o)

.PHONY: all clean check host-test signatures signature-check
all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) $(AMIGAFLAGS) $(LDFLAGS) -o $@ $(OBJ)

src/%.o: src/%.c
	$(CC) $(CPPFLAGS) $(CFLAGS) $(AMIGAFLAGS) -c -o $@ $<

src/signatures.o: src/signatures_generated.inc

signatures:
	python3 tools/compile_signatures.py --write

signature-check:
	python3 tools/compile_signatures.py --check

host-test: signature-check
	mkdir -p build
	$(HOSTCC) -std=c89 -pedantic -Wall -Wextra -Werror -Isrc tests/test_scanner.c src/scanner.c src/signatures.c -o build/test_scanner
	./build/test_scanner
	$(HOSTCC) -std=c89 -pedantic -Wall -Wextra -Werror -Itests/amiga_stubs -Isrc tests/test_trackdisk.c src/trackdisk.c -o build/test_trackdisk
	./build/test_trackdisk
	python3 -m unittest tests/test_analyze_bootblock.py tests/test_qualify_signature.py tests/test_build_clean_manifest.py tests/test_promote_signature.py

check: host-test

clean:
	rm -f $(OBJ) $(TARGET)
	rm -rf build
