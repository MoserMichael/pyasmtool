#!/usr/bin/env bash

set -e
set -x

TOTAL_WORDS=0
WORDS_IN_PAGE=250

make_lesson() {
    local script=$1
    local outfile=$(basename $script .py)".md"
    local tmpfile=$(basename $script .py)".tmp"

    #echo '" Set text width as 72.' >${tmpfile}
    #echo "" >>${tmpfile}
    $script >${tmpfile}
    python3 -m mdpyformat.tocgen ${tmpfile} ${outfile}
    rm ${tmpfile}

    WORDS=$(wc -w "${outfile}" | awk '{ print $1 }')
    echo "${WORDS} words in ${outfile}"
    ((TOTAL_WORDS+=WORDS))
}    

cat <<EOF
Generating tutorial text:

EOF

make_lesson ./bytecode_disasm.py

((NUM_PAGES=TOTAL_WORDS/WORDS_IN_PAGE))

cat <<EOF
===
Total number of words: ${TOTAL_WORDS}

This would make ${NUM_PAGES} pages, given an average number of ${WORDS_IN_PAGE} words per page.

*** all tutorials generated ***"
EOF



