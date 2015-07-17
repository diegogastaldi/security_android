#!/bin/bash
if [ $# -lt 2 ]; then
    echo "Before running, enter 'source paths.local.sh' at the bash prompt."
    echo "Usage: `basename $0` outdir apk"
    exit
fi
export outdir=$1
export apk_file=$2
export outdir=`readlink -m $outdir`

apk_base=`basename $apk_file`
apk_base=${apk_base%%.apk}

if [ ! -d "$outdir" ]; then mkdir $outdir; fi
if [ ! -d "$outdir/log" ]; then mkdir $outdir/log; fi
if [ ! -d "$outdir/dare" ]; then mkdir $outdir/dare; fi

echo Running DARE on $apk_file
$dare -d $outdir/dare/$apk_base $apk_file &> $outdir/log/$apk_base.dare.log
echo Running EPICC on $apk_file
java $jvm_flags -jar $epicc_dir/epicc-0.1.jar -apk $apk_file -android-directory $outdir/dare/$apk_base/retargeted/* -cp $epicc_dir/android.jar > $outdir/$apk_base.epicc
