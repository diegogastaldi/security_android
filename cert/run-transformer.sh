#!/bin/bash
if [ $# -lt 2 ]; then
    echo "Usage: `basename $0` outdir apk"
    exit
fi
export outdir=$1 # parametros
export apk_file=$2 # parametros
export outdir=`readlink -m $outdir` # genera el path completo

apk_base=`basename $apk_file` 
apk_base=${apk_base%%.apk} # apk_base tiene el nombre sin extension
apk_norm=`readlink -m $apk_file` # apk_norm tiene el pah completo

ulimit -v $max_mem -t $max_time # setea los limites de la ejecucion en cuanto a tiempo y memoria

export script_path=`dirname $0` 

sootOutApk="$outdir/sootOutput/`basename $apk_norm`"
if [ -f "$sootOutApk" ]; then
    rm $sootOutApk
fi

if [ "$soot_paths" == "" ]; then
    echo "Missing soot_paths env var!  Try 'source $script_path/paths.local.sh'."
    exit 1
fi


export CLASSPATH=$cert_apk_transform_dir/bin:$soot_paths:$android_jar:$rt_jar # cert_apk_transform_dir=$didfail/cert/transformApk definido en paths.distrib.sh
																			  # soot_paths definido en paths..
																			  # android_jar=$sdk_platforms/android-16/android.jar 
																			  # rt_jar -> java
orig_wd=`pwd`
cd $outdir
echo Transforming $apk_file
java $jvm_flags -cp $CLASSPATH TransformAPKs_IntentSinks -android-jars $sdk_platforms -process-dir $apk_norm -cp $CLASSPATH &> $outdir/log/$apk_base.xform.log
# TransformAPKs_IntentSinks -> clase a compilar y ejecutar -> como parametro le pasa apk_norm
err=$?; if [ $err -ne 0 ]; then echo "Failure!"; exit $err; fi
cd $orig_wd
mv $sootOutApk $outdir/$apk_base.apk # reemplaza vieja app por la transformada
$script_path/extract-manifest.sh $apk_file > $outdir/$apk_base.manifest.xml # extrae el manifest
