#!/bin/bash
if [ $# -lt 1 ]; then
    echo "Usage: `basename $0` outdir"
    exit
fi
export outdir=$1

for epicc in $outdir/*.epicc # recorre los archivos con extensio epicc
do
    epicc=`basename $epicc` # remueve los directorios del path y deja solo el nombre
    base=${epicc%%.epicc} # elimina el punto epicc
    fd=$base.fd.xml # agrega .fd.xml en fd
    manifest=$base.manifest.xml # agrega .manifest.xml en manifest
    if [ ! -f $outdir/$fd ]; then continue; fi
    if [ ! -f $outdir/$manifest ]; then continue; fi
    echo $manifest $epicc $fd # si pasa los if mustra los archivos
done

# cicla sobre los .epicc y le saca la extension para obtener los otros con el mismo nombre base 
# que ya estan en el directorio
