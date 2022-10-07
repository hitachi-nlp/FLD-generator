#!/bin/bash

INPUT_DIR=${1}

if [ "${INPUT_DIR}" = "" ]; then
  echo "Specify input directory"
fi

find ${INPUT_DIR} -type f | sort | grep jsonl$ | grep -v "job-" | xargs wc -l

find ${INPUT_DIR}/ -type f\
  | grep "log.*txt\|qsub\.err\|qsub\.out\|zlog\|\.log$"\
  | sort\
  | ack -l --files-from=- 'Traceback|Kill|ERROR|Exception'
