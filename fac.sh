#!/bin/bash

set -x 

factorial()
{
  if [ $1 -le 1 ]
  then
    echo 1
  else
    result=$(factorial $[$1-1])
    echo $((result*$1))
  fi
}

factorial 5
