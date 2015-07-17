apkfile=$1
jarpath=`dirname $0`
jarfile=$jarpath/AXMLPrinter2.jar
ls $jarfile > /dev/null  # Write to stderr if file not found.
temp=`mktemp`
unzip -p $apkfile AndroidManifest.xml > $temp
java -cp $jarfile test.AXMLPrinter $temp
rm $temp
