export didfail=~/didfail
export epicc_dir=$didfail/epicc
export dare_dir=$didfail/dare-1.1.0-linux
export dare=$dare_dir/dare

export sdk_platforms=$didfail/platforms
export android_jar=$sdk_platforms/android-16/android.jar
export rt_jar=/usr/lib/jvm/java-7-openjdk-amd64/jre/lib/rt.jar

export wkspc=$didfail/workspace       # for FlowDroid
export soot_base=$didfail/workspace   # for the APK transformer
export cert_apk_transform_dir=$didfail/cert/transformApk

export jvm_flags="-Xmx950m -Xss32m"
export max_mem=2250000
export max_time=4200
export python=python2


################################################################################
# Nothing below this line needs to be modified.
################################################################################

export soot_paths=
export soot_paths=$soot_paths:$soot_base/jasmin/classes
export soot_paths=$soot_paths:$soot_base/jasmin/libs/java_cup.jar
export soot_paths=$soot_paths:$soot_base/heros/bin
export soot_paths=$soot_paths:$soot_base/heros/guava-14.0.1.jar
export soot_paths=$soot_paths:$soot_base/heros/slf4j-api-1.7.5.jar
export soot_paths=$soot_paths:$soot_base/heros/slf4j-simple-1.7.5.jar
export soot_paths=$soot_paths:$soot_base/soot/classes
export soot_paths=$soot_paths:$soot_base/soot/libs/polyglot.jar
export soot_paths=$soot_paths:$soot_base/soot/libs/AXMLPrinter2.jar
export soot_paths=$soot_paths:$soot_base/soot/libs/baksmali-2.0b5.jar
export soot_paths=$soot_paths:$soot_base/soot/libs/baksmali-1.3.2.jar

testpaths=$cert_apk_transform_dir/bin:$soot_paths:$android_jar:$rt_jar
testpaths=$testpaths:$epicc_dir:$dare:$sdk_platforms:$wkspc:$soot_base

# Verify that paths don't contain spaces
spaced_paths=`echo $testpaths | egrep -o "[^:]* [^:]*"`
if [ "$spaced_paths" != "" ]; then
    echo "Error: some paths contains spaces!"
    echo $testpaths | egrep -o "[^:]* [^:]*"
fi

# Check existence of jars and directories:
ls -d $(echo $testpaths | tr ':' ' ') > /dev/null

