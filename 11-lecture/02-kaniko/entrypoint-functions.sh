riffle_indirect() { # 3-array version takes variable NAMES as arguments
    # Prepare arguments
    local -n host=$1
    local -n user=$2
    local -n pass=$3
    local output=""
    len=${#host[@]}
    for i in ${!host[@]}
    do
        # Riffle here
        output="$output ${!host[i]} ${!user[i]} ${!pass[i]}"
    done
    echo $output
}
generate_auth_string() {
    # Main logic
    echo "{ \"auths\": {"
    while [ $# -gt 0 ]
    do
        nextline="\"$1\":{\"username\":\"$2\",\"password\":\"$3\"}"
        shift; shift; shift;
        if [ $# -gt 0 ] ; then nextline="${nextline}," ; fi
        echo "$nextline"
    done
    echo "} }"
}
