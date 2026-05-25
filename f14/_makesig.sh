#!/usr/bin/bash
#rm f14.pat
ls *.obj | while read name; do /home/xor/ida77/flair77/bin/linux/plb -S -a $name f14.pat;done
/home/xor/ida77/flair77/bin/linux/sigmake ./f14.pat f14.sig
