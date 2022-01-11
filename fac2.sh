#!/bin/bash

set -x 


factorial()
{
    local num=$1
    fact=1
    for ((i=1;i<=num;i++))
    do
        fact=$(($fact*$i))
    done
    echo "$fact"
}

factorial 5
