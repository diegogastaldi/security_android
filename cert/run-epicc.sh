#!/bin/bash
if [ $# -lt 2 ]; then
    echo "Usage: `basename $0` outdir apk"
    exit
fi
export outdir=$1
export apk_file=$2
export outdir=`readlink -m $outdir` # path completo

apk_base=`basename $apk_file` # solo el nombre
apk_base=${apk_base%%.apk} # sin extension
apk_xform=$outdir/$apk_base.apk # ~/didfail/toyapps/out/

ulimit -v $max_mem -t $max_time 

if [ ! -d "$outdir/dare" ]; then mkdir $outdir/dare; fi

echo Running DARE on $apk_file
$dare -d $outdir/dare/$apk_base $apk_xform &> $outdir/log/$apk_base.dare.log
err=$?; if [ $err -ne 0 ]; then echo "Failure!"; exit $err; fi
echo Running EPICC on $apk_file
java $jvm_flags -jar $epicc_dir/epicc-0.1.jar -apk $apk_xform -android-directory $outdir/dare/$apk_base/retargeted/* -cp $epicc_dir/android.jar > $outdir/$apk_base.epicc
