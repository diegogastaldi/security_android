# Before sourcing this file, $soot_base should be set.

export soot_paths=
export soot_paths=$soot_paths:$soot_base/jasmin/classes
export soot_paths=$soot_paths:$soot_base/jasmin/libs/java_cup.jar
export soot_paths=$soot_paths:$soot_base/heros/bin
export soot_paths=$soot_paths:$soot_base/heros/guava-14.0.1.jar
export soot_paths=$soot_paths:$soot_base/heros/slf4j-api-1.7.5.jar
export soot_paths=$soot_paths:$soot_base/heros/slf4j-simple-1.7.5.jar
export soot_paths=$soot_paths:$soot_base/soot/classes
export soot_paths=$soot_paths:$soot_base/soot/libs/polyglot.jar
export soot_paths=$soot_paths:$soot_base/soot/libs/AXMLPrinter2.jar
export soot_paths=$soot_paths:$soot_base/soot/libs/baksmali-2.0b5.jar
export soot_paths=$soot_paths:$soot_base/soot/libs/baksmali-1.3.2.jar

export CLASSPATH=$soot_paths

#Check existence of jars and directories:
ls -d $(echo $CLASSPATH | tr ':' ' ') > /dev/null
