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
from xutools.tools import XUWc
import optparse
import xutools.parsers
import sys

p = optparse.OptionParser()
p.add_option("-a", "--count", dest="count_type")
p.add_option("-b", "--re_count", dest="count_regexp")
p.add_option("-c", "--context", dest="context_type")
p.add_option("-d", "--re_context", dest="context_regexp")
(options, args) = p.parse_args()

if ( len(args) < 2 ):
    print "Usage xuwc [ --count <count_type> | --re_count <count_regexp> ] [ --context <context_type> | --re_context <context_regexp> ] <xpath> <files>+"
    sys.exit(0)

xpath = args[0]
file_paths = args[1:]

wc_params = {}
wc_params['count_type'] = options.count_type
wc_params['count_regexp'] = options.count_regexp
wc_params['context_type'] = options.context_type
wc_params['context_regexp'] = options.context_regexp

if wc_params['count_type'] != None and wc_params['count_regexp'] != None:
    print "Cannot specify both a count and re_count option."
    sys.exit(-1)
if wc_params['context_type'] != None and wc_params['context_regexp'] != None:
    print "Cannot specify both a context and re_context option."
    sys.exit(-1)

wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
XUWc.output_reports( wc_reports, wc_params )
