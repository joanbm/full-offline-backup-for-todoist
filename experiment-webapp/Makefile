PYVERSION=3.5.2
PYMINOR=$(basename $(PYVERSION))

CC=emcc
OPTFLAGS=-O2
CFLAGS=-std=gnu99 $(OPTFLAGS) -g -I cpython-emscripten/installs/python-$(PYVERSION)/include/python$(PYMINOR)/ -Wno-warn-absolute-paths
LDFLAGS=$(OPTFLAGS) cpython-emscripten/installs/python-$(PYVERSION)/lib/libpython$(PYMINOR).a \
  -s TOTAL_MEMORY=268435456 \
  -s ASSERTIONS=2 \
  -s EMULATE_FUNCTION_POINTER_CASTS=1 \
  -s -s EXPORTED_FUNCTIONS='["_main","_PyRun_SimpleString"]' \
  --memory-init-file 0


all: cpython-emscripten.zip python.asm.js app.zip

cpython-emscripten.zip:
	wget -O cpython-emscripten.zip https://github.com/dgym/cpython-emscripten/archive/685d43a5b9011d229077e31bf9e9b7f70e6c85ca.zip
	unzip cpython-emscripten.zip
	mv cpython-emscripten-* cpython-emscripten
	echo "_csv _csv.c" >> cpython-emscripten/3.5.2/Setup.local

python.asm.js: main.bc js.bc root
	$(CC) -o $@ $(filter %.bc,$^) $(LDFLAGS) \
		$(foreach d,$(wildcard root/*),--preload-file $d@/$(notdir $d))


app.zip: app
	cp -R ../todoist_full_offline_backup app/todoist_full_offline_backup
	if [ -e $@ ]; then rm $@; fi
	zip -r $@ $<


serve: python.asm.js app.zip
	@echo "Serving on port 8062"
	python -m SimpleHTTPServer 8062


clean:
	-rm -fr root
	-rm python.asm.js python.asm.data
	-rm *.bc


%.bc: %.c cpython-emscripten/installs/python-$(PYVERSION)/lib/python$(PYMINOR)
	$(CC) -o $@ $< $(CFLAGS)


%.c: %.pyx
	cython $<

root: cpython-emscripten/installs/python-$(PYVERSION)/lib/python$(PYMINOR)
	mkdir -p root/lib
	cp -a cpython-emscripten/installs/python-$(PYVERSION)/lib/python$(PYMINOR)/ root/lib
	# Clean up unused modules
	( \
		cd root/lib/python$(PYMINOR); \
		rm -fr test distutils ensurepip idlelib __pycache__ tkinter; \
	)

cpython-emscripten/installs/python-$(PYVERSION)/lib/python$(PYMINOR):
	make -C cpython-emscripten/$(PYVERSION)
