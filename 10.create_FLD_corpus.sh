#!/bin/bash

launch-qsub\
  "./launch_create_FLNL_corpus.py 1>log.launch_create_FLNL_corpus.txt 2>&1"\
  ABCI\
  rt_C.small\
  -l "h_rt=24:00:00"
