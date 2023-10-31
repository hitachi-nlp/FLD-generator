#!/bin/bash

output_dir=./res/knowledge_banks/
if [ ! -e "${output_dir}" ]; then
  mkdir -p ${output_dir}
fi

# [allenai/commonsense-kg-completion](https://github.com/allenai/commonsense-kg-completion)
google_drive_id="1dpSK-eV_USdQ9XvqBuj2rjvtgz_97P0E"
output_filename="commonsense-kg-completion"
./download_scripts/wget_google_drive.sh ${google_drive_id} ${output_filename}.zip
mv ${output_filename}.zip ${output_dir}
unzip ${output_dir}/${output_filename}.zip -d ${output_dir}/${output_filename}

# [LIANGKE23/Awesome-Knowledge-Graph-Reasoning](https://github.com/LIANGKE23/Awesome-Knowledge-Graph-Reasoning#datasets-)
google_drive_id="1wKSjDQjB5E2g8De22NzdQOzIX2IZARW0"
output_filename="DBpedia500"
./download_scripts/wget_google_drive.sh ${google_drive_id} ${output_filename}.zip
mv ${output_filename}.zip ${output_dir}
unzip ${output_dir}/${output_filename}.zip -d ${output_dir}/
for split in "train1" "train2" "valid" "test"; do
  unzip ${output_dir}/${output_filename}/${split}.zip -d ${output_dir}/${output_filename}
done

# [LIANGKE23/Awesome-Knowledge-Graph-Reasoning](https://github.com/LIANGKE23/Awesome-Knowledge-Graph-Reasoning#datasets-)
google_drive_id="1Nrz7cg543w7CrdFrpxXwZF5UNw9HMs0t"
output_filename="yago37"
./download_scripts/wget_google_drive.sh ${google_drive_id} ${output_filename}.zip
mv ${output_filename}.zip ${output_dir}
unzip ${output_dir}/${output_filename}.zip -d ${output_dir}/
