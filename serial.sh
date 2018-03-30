#!/bin/bash

set -e

FILE=$1

function usage {
    cat - <<EOF
serial.sh <filename>

increment serial number stored in a file
EOF
    exit 1
}

if [[ -z "$FILE" ]]; then
    usage
fi

SERIAL=1

if [[ -e "$FILE" ]]; then
    SERIAL=$(cat ${FILE})
fi
# increment
(( SERIAL++ ))

echo $SERIAL > ${FILE}
echo $SERIAL
