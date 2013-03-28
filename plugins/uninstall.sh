 #!/bin/bash
  
PREFIX=`dirname "$0"`
 
cd $PREFIX
for i in `ls -1`; do
	if [ -d "$PREFIX/$i" ]; then
		if [ -d "$HOME/.synfig/plugins/$i" ]; then
			rm -rf "$HOME/.synfig/plugins/$i"
		fi
	fi
done
