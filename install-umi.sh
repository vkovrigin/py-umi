#!/bin/sh
wget https://lnd.im/umi -O /tmp/umi.zip
unzip -o /tmp/umi.zip
UMI_dir=$(unzip -l /tmp/umi.zip | awk 'FNR==4 {print $4}' | cut -f1 -d"/")
ln -s "$UMI_dir"/bin/umi "$UMI_dir/umi"/
export PATH=$PATH:$PWD/$UMI_dir
