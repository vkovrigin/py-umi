#!/bin/sh
wget https://lnd.im/umi -O /tmp/umi.zip
tar -xvf /tmp/umi.zip
UMI_dir=$(tar -tzf /tmp/umi.zip | head -1 | cut -f1 -d"/")
ln -s "$UMI_dir"/bin/umi "$UMI_dir"/
export PATH=$PATH:$PWD/$UMI_dir/
