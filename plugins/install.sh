#!/bin/bash
  
PREFIX=`dirname "$0"`
 
[ -d $HOME/.synfig/plugins ] || mkdir -p $HOME/.synfig/plugins

cd $PREFIX
for i in `ls -1`; do
	if [ -d "$PREFIX/$i" ]; then
		cp -rf "$PREFIX/$i" $HOME/.synfig/plugins
	fi
done
