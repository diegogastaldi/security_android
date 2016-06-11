#!/bin/bash
script_name="$0"
script_name=`readlink -m "$script_name"`  
export script_path=`dirname $script_name` 
paths_local="$script_path/paths.local.sh" 

if [ ! -f $paths_local ]; then
    echo "Before running this script, copy paths.template.sh to paths.local.sh"
    echo "(Or copy paths.distrib.sh instead of paths.template.sh)"
    echo "File not found: $paths_local"
    exit
fi

source $paths_local

if [ $# -lt 2 ]; then
    echo "Usage: `basename $0` outdir apk_1 ... apk_n"
    echo "No spaces are allowed in outdir or apk filenames."
    exit
fi
export outdir="toyapps/out/" 
shift 
export outdir=`readlink -m "$outdir"` 

ulimit -v $max_mem # modified

orig_wd=`pwd`
cd $outdir
$python -t -t $script_path/taintflows.py --check_levels_gui $($script_path/find-processed-apps.sh $outdir) > $outdir/flows.out
cd $orig_wd
