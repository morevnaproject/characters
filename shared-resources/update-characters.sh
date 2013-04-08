#!/bin/bash


# ================= FUNCTIONS =======================
copy_if_changed(){
	if ( ! diff <(md5sum "$1" | awk '{print $1}') <(md5sum "$2" | awk '{print $1}') >/dev/null ); then
		cp "$1" "$2"
		echo "Updating $2..."
	fi
}

# =================== MAIN =========================

PREFIX=`dirname "$0"`

# Get characters list
CHARACTERS=`ls -1d $PREFIX/../character-*`

# Get elements to propagate
pushd "$PREFIX" >/dev/null
ELEMENTS=`ls -1 *.sif`
popd >/dev/null

for CHARACTER in $CHARACTERS; do
	if [ -e "$CHARACTER/resources" ]; then
		echo "found character in $CHARACTER "
		# Copy the common elements
		for ELEMENT in $ELEMENTS; do
			ELEMENT=`basename "$ELEMENT" .sif`
			copy_if_changed "$PREFIX/${ELEMENT}.sif" "$CHARACTER/resources/${ELEMENT}.sif"
		done
		# Get the character breed
		BREED=${CHARACTER##*.}
		# Copy the breed-specific elements
		if [ ! -z "$BREED" ]; then
			if [ -d "$PREFIX/$BREED" ]; then
				pushd "$PREFIX/$BREED" >/dev/null
				BREED_ELEMENTS=`ls -1 *.sif`
				popd >/dev/null
				for ELEMENT in $BREED_ELEMENTS; do
					ELEMENT=`basename "$ELEMENT" .sif`
					copy_if_changed "$PREFIX/$BREED/${ELEMENT}.sif" "$CHARACTER/resources/${ELEMENT}.sif"
				done
			fi
		fi
	fi
	bash "$CHARACTER/resources/update-lib.sh"
done
