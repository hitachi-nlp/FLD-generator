#!/bin/bash

INPUT_DIR=${1}

if [ "${INPUT_DIR}" = "" ]; then
  echo "Specify input directory"
fi

find ${INPUT_DIR} -type f | sort | grep jsonl$ | grep -v "job-" | xargs wc -l

# find ${INPUT_DIR}/ -type f\
#   | grep "log.*txt\|qsub\.err\|qsub\.out\|zlog\|\.log$"\
#   | sort\
#   | ack -l --files-from=- 'Traceback|Kill|ERROR|Exception'

find ${INPUT_DIR}/ -type f\
  | grep "log.*txt\|qsub\.err\|qsub\.out\|zlog\|\.log$"\
  | sort\
  | while read input_file; do

  # file ends with Traceback
  tmp=$(mktemp)
  tail -n 100 ${input_file} > ${tmp}

  # we use grep instead of ack, which somehow exits the for loop (why??)
  # found=`ack -l 'Traceback|Kill|ERROR|Exception' ${tmp}` 
  found=`grep 'Traceback\|Kill\|ERROR\|Exception' ${tmp}` 
  if [ ! "$found" = "" ]; then
      echo ${input_file}
  fi
done
