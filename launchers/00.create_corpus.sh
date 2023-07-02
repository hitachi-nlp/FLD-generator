#!/bin/bash

launch-qsub\
  "./launchers/run_create_corpus.py 1>log.run_create_corpus.txt 2>&1"\
  ABCI\
  rt_C.small\
  -l "h_rt=24:00:00"
