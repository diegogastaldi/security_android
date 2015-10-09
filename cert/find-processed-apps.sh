#!/bin/bash
if [ $# -lt 1 ]; then
    echo "Usage: `basename $0` outdir"
    exit
fi
export outdir=$1

for epicc in $outdir/*.epicc 
do
    epicc=`basename $epicc` 
    base=${epicc%%.epicc} 
    fd=$base.fd.xml 
    manifest=$base.manifest.xml 
    if [ ! -f $outdir/$fd ]; then continue; fi
    if [ ! -f $outdir/$manifest ]; then continue; fi
    echo $manifest $epicc $fd 
done



