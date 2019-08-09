declare -a projects=(
    "ambari" 
    "camel" 
    "cloudstack" 
    "cocoon" 
    "hadoop" #works
    "hbase" #works
    "hive" #works
    "ignite"  #works
    "kafka" 
    "maven" 
    "ofbiz" 
    "spark")

for i in "${projects[@]}"
do
    echo "Creating directories for $i"
    mkdir -p artifacts/$i
    mkdir -p cross_issue_data/$i
    mkdir -p datasets/$i
    mkdir -p logs/$i
    mkdir -p plots/$i
done
