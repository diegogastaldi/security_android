#!/bin/bash
if [ $# -lt 2 ]; then
    echo "Usage: `basename $0` outdir apk"
    exit
fi
export outdir=$1
export apk_file=$2
export outdir=`readlink -m $outdir`

apk_base=`basename $apk_file`
apk_base=${apk_base%%.apk}
apk_xform=$outdir/$apk_base.apk

ulimit -v $max_mem -t $max_time

soot_classpath=$(echo "$wkspc/soot-infoflow-android/bin
$wkspc/soot/classes
$wkspc/jasmin/classes
$wkspc/jasmin/libs/java_cup.jar
$wkspc/heros/bin
$wkspc/heros/guava-14.0.1.jar
$wkspc/heros/slf4j-api-1.7.5.jar
$wkspc/heros/slf4j-simple-1.7.5.jar
$wkspc/soot/libs/polyglot.jar
$wkspc/soot/libs/AXMLPrinter2.jar
$wkspc/soot/libs/baksmali-2.0b5.jar
$wkspc/soot/libs/baksmali-1.3.2.jar
$wkspc/soot-infoflow-android/lib/polyglot.jar
$wkspc/soot-infoflow-android/lib/AXMLPrinter2.jar
$wkspc/soot-infoflow/bin
$wkspc/soot-infoflow/lib/cos.jar
$wkspc/soot-infoflow/lib/j2ee.jar
$wkspc/soot-infoflow/lib/slf4j-api-1.7.5.jar
$wkspc/soot-infoflow/lib/slf4j-simple-1.7.5.jar
$wkspc/soot-infoflow-android/lib/axml-1.0.jar" | tr "\n" ":")

export flowdroid="java $jvm_flags -Dfile.encoding=UTF-8 -classpath $soot_classpath soot.jimple.infoflow.android.TestApps.Test"

echo Running FlowDroid on $apk_file
orig_wd=`pwd`
cd $wkspc/soot-infoflow-android
$flowdroid $apk_xform $sdk_platforms --nostatic --aplength 1 --aliasflowins --out $outdir/$apk_base.fd.xml &> $outdir/log/$apk_base.flowdroid.log
err=$?; if [ $err -ne 0 ]; then echo "Failure!"; exit $err; fi
cd $orig_wd
