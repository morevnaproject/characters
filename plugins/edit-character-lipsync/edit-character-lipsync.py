#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 by Konstantin Dmitriev <ksee.zelgadis@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os
import sys
import subprocess
import math

# Prestob Blair set (deprecated)
phoneme_conversion = {
	'AI' :5.0,
	'O'  :4.0,
	'E'  :4.5,
	'U'  :4.0,
	'etc':2.0, # this covers Preston Blair's CDGKNRSThYZ mouth shape
	'L':3.0,
	'WQ':4.0,
	'MBP':1.5,  # МПБ
	'FV':2.5,
	'rest':0.0 # not really a phoneme - this is used in-between phrases when the mouth is at rest
}

# Fleming & Dobbs set
phoneme_conversion = {
	'MBP'	:1.5,
	'NLTDR'	:2.0,
	'FV'	:2.5,
	'GK'	:3.0, # this covers Preston Blair's CDGKNRSThYZ mouth shape
	'SH'	:3.5,
	'O'		:4.0,
	'EHSZ'	:4.5,
	'AA'	:5.0,
	'IY'	:5.5,
	'TH'  	:6.0,
	'rest':0.0 # not really a phoneme - this is used in-between phrases when the mouth is at rest
}


def process(filename):
	
	# Read the input file
	inputfile_f = open(filename, 'r')
	inputfile_contents = inputfile_f.readlines()
	inputfile_f.close()
	# Get the length and fps
	fps = 24
	length = 120 
	for line in inputfile_contents:
		if '<canvas version=' in line:
			a = line.split(' ')
			for i in a:
				if i.startswith('fps="'):
					fps=int(i[5:-1].split('.')[0])
					break
			#get the length only after FPS is known
			for i in a:
				if i.startswith('end-time="'):
					length=0
					for j in i[10:-1].split(' '): # "2s 15f"
						if j.endswith('s'):
							length+=int(math.ceil(int(j[:-1])/fps))
						elif j.endswith('f'):
							length+=int(j[:-1])
			break
	
	
	base_filename = os.path.splitext(filename)[0]
	base_filename = os.path.splitext(base_filename)[0] # twice!
	lipsync_filename = base_filename+'.pgo'
	
	if not os.path.exists(lipsync_filename):
		# Create empty Papagayo project	
		lipsync_f = open(lipsync_filename, 'w')
		lipsync_f.write("lipsync version 1\n")
		lipsync_f.write("%s.wav\n" % base_filename)
		lipsync_f.write("%s\n" % fps)
		lipsync_f.write("%s\n" % length)
		lipsync_f.write("1\n") # num voices
		lipsync_f.write("	Voice 1\n")
		lipsync_f.write("	\n") # voice text
		lipsync_f.write("	0\n") # num phrases in text
		lipsync_f.close()
	
	# Pass the project to Papagayo
	subprocess.call(['papagayo', lipsync_filename])
	
	# Read result
	lipsync_f = open(lipsync_filename, 'r')
	lipsync_contents = lipsync_f.readlines()
	lipsync_f.close()
	
	# Now convert results to the same file
	outputfile_f = open(filename, 'w')
	
	mimic_found=False
	for line in inputfile_contents:
		if mimic_found and '</animated>' in line:
			mimic_found=False
		elif mimic_found:
			pass
		elif ' id="(stk)-switch-mimic"' in line:
			if '<animated ' in line:
				mimic_found=True
			# replace the mimic values by the lipsync data
			phonemes={} # frame to phoneme mapping
			phonemes[0]='rest'
			word_end=0 # we need to know where the word ends to set the mouth into the rest position
			for i, l in enumerate(lipsync_contents):
				if l.startswith("\t\t\t\t"):
					a=l.split()
					
					frame=int(a[0].strip())
					phoneme=a[1].strip()
					
					phonemes[frame]=phoneme
					
				elif l.startswith("\t\t\t"):
					word_end=int(l.split(' ')[2].strip()) + 1
					print "Word found, ends on: %s" % word_end
					phonemes[word_end]='rest'
			phonemes[word_end]='rest'
			
			outputfile_f.write('<animated type="real" id="(stk)-switch-mimic">'+"\n")
			for frame in sorted(phonemes.keys()):
				time= "%.8fs" % ( (1.0*int(frame)) / fps )
				
				phoneme=phoneme_conversion[phonemes[frame]]
				phoneme="%.8f" % phoneme
				
				outputfile_f.write("<waypoint time=\"%s\" before=\"constant\" after=\"constant\">\n" % time)
				outputfile_f.write("<real value=\"%s\"/>\n" % phoneme )
				outputfile_f.write("</waypoint>\n")
			outputfile_f.write("</animated>\n")
		else:
			outputfile_f.write(line)
	outputfile_f.close()

if len(sys.argv) < 2:
	sys.exit()
else:
	process(sys.argv[1])
