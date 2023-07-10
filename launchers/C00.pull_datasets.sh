#!/bin/bash

source_ABIC_dir=/groups/1/gca50126/honoka/work/projects/FLNL/outputs/10.create_FLD_corpus/20230711.ICML-official-release-v2/dataset_name=20230711.finalize.D3
output_dir=./outputs/C00.pull_datasets.sh/2023-07-13/FLD/FLD.3
mkdir -p ${output_dir} 1>/dev/null 2>&1
for split in "train" "valid" "test"; do
  rsync -av es.abci.ai:${source_ABIC_dir}/${split}/${split}.jsonl ${output_dir}
done

source_ABIC_dir=/groups/1/gca50126/honoka/work/projects/FLNL/outputs/10.create_FLD_corpus/20230711.ICML-official-release-v2/dataset_name=20230711.finalize.D8
output_dir=./outputs/C00.pull_datasets.sh/2023-07-13/FLD/FLD.4
mkdir -p ${output_dir} 1>/dev/null 2>&1
for split in "train" "valid" "test"; do
  rsync -av es.abci.ai:${source_ABIC_dir}/${split}/${split}.jsonl ${output_dir}
done
