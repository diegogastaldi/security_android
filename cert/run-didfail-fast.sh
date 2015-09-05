#!/bin/bash
script_name="$0"
script_name=`readlink -m "$script_name"`  # Genera el path completo a la carpeta $0 -> /home/diego/didfail/cert/run-didfail.sh
export script_path=`dirname $script_name` # Genera /home/diego/didfail/cert
paths_local="$script_path/paths.local.sh" # Genera /home/diego/didfail/cert/paths.local.sh

if [ ! -f $paths_local ]; then
    echo "Before running this script, copy paths.template.sh to paths.local.sh"
    echo "(Or copy paths.distrib.sh instead of paths.template.sh)"
    echo "File not found: $paths_local"
    exit
fi

source $paths_local # ejecuta # Genera /home/diego/didfail/cert/paths.local.sh

if [ $# -lt 2 ]; then
    echo "Usage: `basename $0` outdir apk_1 ... apk_n"
    echo "No spaces are allowed in outdir or apk filenames."
    exit
fi
export outdir=$1 # directorio de salida -> ~/didfail/toyapps/out/
shift # ??
export outdir=`readlink -m "$outdir"` # hace los paths absolutos
#if [ -f "$outdir" ]; then
#    if [ ! -d "$outdir" ]; then
#	echo "Not a directory: $outdir"
#	exit 1
#    fi
#fi

#if [ ! -d "$outdir" ]; then mkdir "$outdir"; fi
#if [ ! -d "$outdir/log" ]; then mkdir "$outdir/log"; fi # crea directorios de salida

ulimit -v $max_mem # limite de memoria -> modificado para que ande

#for apk_file in $@ # arreglo de parametros
#do
#    echo Processing $apk_file
#    $script_path/run-transformer.sh $outdir $apk_file # corre el run-tranformer.sh para cada apk
#    if [ $? -ne 0 ]; then continue; fi # ??
#    $script_path/run-epicc.sh $outdir $apk_file # corre el run-epicc.sh para cada apk
#    $script_path/run-flowdroid.sh $outdir $apk_file # corre el run-flowdroid.sh para cada apk
#done

orig_wd=`pwd` # actual directorio
cd $outdir # cambia a directorio de salida
$python -t -t $script_path/taintflows.py --check_levels_gui $($script_path/find-processed-apps.sh $outdir) > $outdir/flows.out # ejecuta el taintflows con salida de epicc y fd  y guarda la salida en flows.out
cd $orig_wd
