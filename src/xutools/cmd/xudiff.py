#!/usr/bin/python
"""
copyright (c) 2010-2012, Gabriel A. Weaver, Department of Computer
Science at Dartmouth College. <Gabriel.A.Weaver@Dartmouth.edu>

This file is part of XUTools, Python Distribution.

This code is free software:  you can redistribute                
it and/or modify it under the terms of the GNU General Public                   
License as published by the Free Software Foundation, either version            
3 of the License, or (at your option) any later version.                        
                                                                                
XUTools is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.
                                                                                
You should have received a copy of the GNU General Public License               
along with this program.  If not, see http://www.gnu.org/licenses/
"""
import codecs
from pyparsing import *
from xutools.parsers import TEILiteParser, CiscoIOSParser
from xutools.distances import ZhangShashaTreeDist as TD
from xutools.tools import XUDiff as XUD
import optparse
import pprint
import sys

p = optparse.OptionParser()
p.add_option("-c", "--count", dest="count_type" )
(options, args) = p.parse_args()

if ( len(args) < 3 ):
    print "Usage:  xudiff [ --count <count_type> ] <xpath> <file1> <file2>"
    sys.exit(-1)

xpath = args[0]
file_paths = args[1:]
report = XUD.xudiff_main( xpath, file_paths, options.count_type )

# the position of start nodes in T1, T2
i = len(report['l0'])
j = len(report['l1'])
edit_script = XUD.output_edit_script( i, j, 1, 1, report )
if options.count_type == None:
    unit = ""
else:
    unit = options.count_type

sys.stdout.write("\n" + "Distance: " + str( report['forest_dist'][i,j] ) + " " + unit + "\n" )
sys.stdout.write("\n".join( edit_script ) + "\n" )


