#!/bin/bash
script_name="$0"
script_name=`readlink -m "$script_name"`
export script_path=`dirname $script_name`
paths_local="$script_path/paths.local.sh"

if [ ! -f $paths_local ]; then
    echo "Before running this script, copy paths.distrib.sh to paths.local.sh"
    echo "File not found: $paths_local"
    exit
fi

source $paths_local

if [ $# -lt 2 ]; then
    echo "Usage: `basename $0` outdir apk_1 ... apk_n"
    echo "No spaces are allowed in outdir or apk filenames."
    exit
fi
export outdir=$1
shift
export outdir=`readlink -m "$outdir"`
if [ -f "$outdir" ]; then
    if [ ! -d "$outdir" ]; then
        echo "Not a directory: $outdir"
        exit 1
    fi
fi

if [ ! -d "$outdir" ]; then mkdir "$outdir"; fi
if [ ! -d "$outdir/log" ]; then mkdir "$outdir/log"; fi

ulimit -v $max_mem

for apk_file in $@
do
    echo Processing $apk_file
    $script_path/run-transformer.sh $outdir $apk_file
    if [ $? -ne 0 ]; then continue; fi
    $script_path/run-epicc.sh $outdir $apk_file
    $script_path/run-flowdroid.sh $outdir $apk_file
done

orig_wd=`pwd`
cd $outdir
$python -t -t $script_path/taintflows.py --check_levels_file "js.txt" $($script_path/find-processed-apps.sh $outdir) > $outdir/flows.out
cd $orig_wd
