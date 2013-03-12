#!/bin/bash

PREFIX=`dirname "$0"`

for ELEMENT in \
	foot-male-01 \
	hand-male-01 \
	foot-female-01 \
	hand-female-01
do
	if [ -e $PREFIX/${ELEMENT}.sif ]; then
		if ( ! diff <(md5sum $PREFIX/${ELEMENT}.sif | awk '{print $1}') <(md5sum $PREFIX/${ELEMENT}-c.sif | awk '{print $1}') >/dev/null ); then
			cp $PREFIX/${ELEMENT}.sif $PREFIX/${ELEMENT}-c.sif
			echo "Updating $PREFIX/${ELEMENT}-c.sif ..."
		fi
	fi
done
