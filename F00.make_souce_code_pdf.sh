#!/bin/bash

OUTPUT_DIR=./F00.source_code_pdf

find ./FLNL -type f | grep "\.py$" > ${OUTPUT_DIR}/source_code.txt
enscript -p ${OUTPUT_DIR}/source_code.ps ${OUTPUT_DIR}/source_code.txt
ps2pdf ${OUTPUT_DIR}/source_code.ps ${OUTPUT_DIR}/source_code.pdf
