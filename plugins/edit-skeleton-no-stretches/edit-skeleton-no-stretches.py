#!/usr/bin/env python

#
# Copyright (c) 2013 by Konstantin Dmitriev <ksee.zelgadis@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os
import sys
import re

def check_substring(data, substring):
	s = "\n".join(data);
	if substring in s:
			return True
	return False

def process(filename):
	
	# Read the input file
	inputfile_f = open(filename, 'r')
	inputfile_contents = inputfile_f.readlines()
	inputfile_f.close()
	
	# Now write results to the same file
	inputfile_f = open(filename, 'w')

	defs_found=False
	exports={}
	link=''
	version=''
	for line in inputfile_contents:
		if "</defs>" in line:
			inputfile_f.write(line)
			defs_found=False
			# Check version here
			if version=='':
				print("ERROR: Provided skeleton is not compatible with this script.")
				sys.exit(1)
			
		elif defs_found:
			inputfile_f.write(line)
			# Read exported values and their types
			if "id=" in line:
				
				el_name=re.findall(r'id="(.*?)"', line)[0]
				el_type=re.findall(r'type="(.*?)"', line)
				if len(el_type)==0:
					el_type=re.findall(r'<(.*?) .*', line)
				el_type=el_type[0]
				exports[el_name]=el_type
				if el_name=='(stk)-version':
					version=re.findall(r'>(.*?)</string>', line)[0]
					print("Skeleton version: %s" % version)
		elif "<defs>" in line:
			inputfile_f.write(line)
			defs_found=True
		
		
		elif link!='' and '</layer>' in line:
			inputfile_f.write(line)
			link=''
		elif link!='':
			pass
		elif '-compensator"' in line:
			match=re.findall(r'desc="(.*?)-compensator"', line)
			if len(match)==0:
				# False alarm, pass
				pass
			else:
				link=match[0]
			inputfile_f.write(line)
			
			# Now rewrite layer contents
			link_type=exports[link]
			if link_type=='vector':
				inputfile_f.write("""
                <param name="amount">
                  <composite type="vector">
                    <x>
                      <reciprocal type="real">
                        <link>
                          <vectorlength type="real" vector=":%s"/>
                        </link>
                        <epsilon>
                          <real value="0.0000010000"/>
                        </epsilon>
                        <infinite>
                          <real value="999999.0000000000"/>
                        </infinite>
                      </reciprocal>
                    </x>
                    <y>
                      <real value="1.0000000000"/>
                    </y>
                  </composite>
                </param>
                <param name="center">
                  <vector>
                    <x>0.0000000000</x>
                    <y>0.0000000000</y>
                  </vector>
                </param>
				""" % link)
			else:
				inputfile_f.write("""
				<param name="amount">
                  <composite type="vector">
                    <x>
                      <reciprocal type="real" link=":%s">
                        <epsilon>
                          <real value="0.0000010000"/>
                        </epsilon>
                        <infinite>
                          <real value="999999.0000000000"/>
                        </infinite>
                      </reciprocal>
                    </x>
                    <y>
                      <real value="1.0000000000"/>
                    </y>
                  </composite>
                </param>
                <param name="center">
                  <vector>
                    <x>0.0000000000</x>
                    <y>0.0000000000</y>
                  </vector>
                </param>
                """ % link)
		else:
			inputfile_f.write(line)

	inputfile_f.close()

if len(sys.argv) < 2:
	sys.exit()
else:
	process(sys.argv[1])
	

