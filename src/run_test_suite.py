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
import unittest
import xutools.test.distances as test_distances
import xutools.test.parsers as test_parsers
import xutools.test.tools as test_tools

editDistanceSuite = unittest.TestLoader().loadTestsFromTestCase( test_distances.TestEditDistance )
zhangShashaSuite = unittest.TestLoader().loadTestsFromTestCase( test_distances.TestZhangShashaTreeDist )
distances_suite = [ editDistanceSuite, zhangShashaSuite ]

ciscoIOSSuite = unittest.TestLoader().loadTestsFromTestCase( test_parsers.TestCiscoIOSParser )
teiLiteSuite = unittest.TestLoader().loadTestsFromTestCase( test_parsers.TestTEILiteParser )
nvdSuite = unittest.TestLoader().loadTestsFromTestCase( test_parsers.TestNVDParser )
subsetCSuite = unittest.TestLoader().loadTestsFromTestCase( test_parsers.TestSubsetCParser )
xpathSuite = unittest.TestLoader().loadTestsFromTestCase( test_parsers.TestXPathParser )
parsers_suite = [ ciscoIOSSuite, teiLiteSuite, nvdSuite, subsetCSuite, xpathSuite ]

xugrepSuite = unittest.TestLoader().loadTestsFromTestCase( test_tools.TestXUGrep )
xuwcSuite = unittest.TestLoader().loadTestsFromTestCase( test_tools.TestXUWc )
xudiffSuite = unittest.TestLoader().loadTestsFromTestCase( test_tools.TestXUDiff )
tools_suite = [ xugrepSuite, xuwcSuite, xudiffSuite ]

alltests = unittest.TestSuite( distances_suite + parsers_suite + tools_suite )

unittest.TextTestRunner(verbosity=2).run(alltests)
