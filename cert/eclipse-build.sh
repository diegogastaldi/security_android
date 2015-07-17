eclipse=$1
workspace=$2
"$eclipse" -nosplash -application org.eclipse.jdt.apt.core.aptBuild -data "$workspace"
