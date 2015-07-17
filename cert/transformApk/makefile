SHELL=/bin/bash

ifndef soot_base
    $(error soot_base is undefined.  It is needed by classpath.sh)
endif

default: src/TransformAPKs_IntentSinks.java classpath.sh bin
	source classpath.sh; javac src/TransformAPKs_IntentSinks.java -d bin

bin:
	mkdir bin
