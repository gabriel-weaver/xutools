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
import ConfigParser
from pyparsing import *
import pprint
from xutools.distances import ZhangShashaTreeDist as TD
from xutools.tools import XUDiff, XUGrep, XUWc
import unittest

## @package test
#    This module contains methods to test our XUTools


#  We want to be more careful to think about the kinds of bugs and 
#   exceptions that this utility may throw when it computes a result
#   set.
class TestXUGrep( unittest.TestCase ):

    tei_data_path1 = None
    tei_data_path2 = None
    nvd_data_path1 = None
    ios_data_path1 = None
    c_data_path1 = None

    tei_data1 = None
    tei_data2 = None
    nvd_data1 = None
    ios_data1 = None
    c_data1 = None

    # I may want to do something very similar to XML
    tei_xupath1 = "//tei:section"
    tei_xupath2 = "//tei:section/tei:subsection/tei:subsubsection[ re:testsubtree('Globus','gi')]"

    nvd_xupath1 = "//nvd:entry[ re:testsubtree('Windows\s7','gi')]"
    nvd_xupath2 = "//nvd:entry[ re:testsubtree('Windows\s7','gi')]/nvd:score"

    # I may want to grab all interfaces within a document
    ios_xupath1 = "//ios:interface"
    ios_xupath2 = "//ios:interface[ re:testsubtree('access-group','gi') ]"
    ios_xupath3 = "//ios:interface[ re:testsubtree('access-group','gi') ]/ios:line"
    ios_xupath4 = "//ios:interface/ios:line[ re:testsubtree('access-group','gi') ]"
    ios_xupath5 = "//ios:line"

    # I may want to be able to grab all C functions in a document
    c_xupath1 = "//cspec:function"
    c_xupath2 = "//cspec:function[ re:testsubtree('putchar','gi') ]"
    c_xupath3 = "//cspec:function/cspec:line[ re:testsubtree('putchar','gi') ]"    

    def setUp(self):

        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')

        self.tei_data_path1 = config.get('xutools.test.test_tools', 'TEIDataPath1')
        self.tei_data_path2 = config.get('xutools.test.test_tools', 'TEIDataPath2')
        self.nvd_data_path1 = config.get('xutools.test.test_tools', 'NVDDataPath1')
        self.ios_data_path1 = config.get('xutools.test.test_tools', 'IOSDataPath1')
        self.c_data_path1 = config.get('xutools.test.test_tools', 'CDataPath1' )

        fp = open( self.tei_data_path1, 'r' )
        self.tei_data1 = fp.read()
        fp.close()

        fp = open( self.tei_data_path2, 'r' )
        self.tei_data2 = fp.read()
        fp.close()
        
        fp = open( self.nvd_data_path1, 'r' )
        self.nvd_data1 = fp.read()
        fp.close()

        fp = open( self.ios_data_path1, 'r' )
        self.ios_data1 = fp.read()
        fp.close()

        fp = open( self.c_data_path1, 'r' )
        self.c_data1 = fp.read()
        fp.close()
                         
    def test_process_cf_match(self):
        # TEI
        cf_match = ["tei:section"]
        report = {}
        report['result_forest'] = [ self.tei_data1 ]
        report['tree_ids'] = []
        report['tree_types'] = []

        xugrep = XUGrep()
        report = xugrep.process_cf_match( cf_match, "", report )
        self.assertEqual( len( report['result_forest'] ), 2 )
        self.assertEqual( report['tree_ids'][0], "1" )
        self.assertEqual( report['tree_ids'][1], "9" )
        self.assertEqual( len( report['tree_ids'] ), 2 )
        self.assertEqual( report['tree_types'][0], "tei:section" )
        self.assertEqual( len( report['tree_types'] ), 1 )

        # NVD
        cf_match = ["nvd:entry"]
        report = {}
        report['result_forest'] = [ self.nvd_data1 ]
        report['tree_ids'] = []
        report['tree_types'] = []

        xugrep = XUGrep()
        report = xugrep.process_cf_match( cf_match, "", report )
        self.assertEqual( len( report['result_forest'] ), 2 )
        self.assertEqual( report['tree_ids'][0], "CVE-2012-0001" )
        self.assertEqual( report['tree_ids'][1], "CVE-2012-0002" )
        self.assertEqual( len( report['tree_ids'] ), 2 )
        self.assertEqual( report['tree_types'][0], "nvd:entry" )
        self.assertEqual( len( report['tree_types'] ), 1 )

        # IOS
        cf_match = ["ios:interface"]
        report = {}
        report['result_forest'] = [ self.ios_data1 ]
        report['tree_ids'] = []
        report['tree_types'] = []

        xugrep = XUGrep()
        report = xugrep.process_cf_match( cf_match, "", report )
        self.assertEqual( len( report['result_forest'] ), 2 )
        self.assertEqual( report['tree_ids'][0], "Loopback0" )
        self.assertEqual( report['tree_ids'][1], "GigabitEthernet4/2" )
        self.assertEqual( len( report['tree_ids'] ), 2 )
        self.assertEqual( report['tree_types'][0], "ios:interface" )
        self.assertEqual( len( report['tree_types'] ), 1 )

        # C Code
        cf_match = ["cspec:function"]
        report = {}
        report['result_forest'] = [ self.c_data1 ]
        report['tree_ids'] = []
        report['tree_types'] = []

        xugrep = XUGrep()
        report = xugrep.process_cf_match( cf_match, "", report )
        self.assertEqual( len( report['result_forest'] ), 5 )
        self.assertEqual( report['tree_ids'][0], "putstr" )
        self.assertEqual( report['tree_ids'][1], "fac" )
        self.assertEqual( report['tree_ids'][2], "putn" )
        self.assertEqual( report['tree_ids'][3], "facpr" )
        self.assertEqual( report['tree_ids'][4], "main" )
        self.assertEqual( len( report['tree_ids'] ), 5 )
        self.assertEqual( report['tree_types'][0], "cspec:function" )
        self.assertEqual( len( report['tree_types'] ), 1 )

    def test_process_re_match(self):

        # TEI
        report = {}
        report['result_forest'] = [ self.tei_data1 ]
        report['tree_ids'] = [ "AIST" ]
        report['tree_types'] = [ "file" ]

        re_match = ["Globus"]
        xugrep = XUGrep()
        report = xugrep.process_re_match( re_match, "", report )
        self.assertEqual( len( report['result_forest'] ), 1 ) 
        self.assertEqual( report['tree_ids'][0], "AIST" )
        self.assertEqual( len( report['tree_ids'] ), 1 )
        self.assertEqual( len(report['re_matches'][0]), 2 )
        self.assertEqual( len(report['re_matches']), 1 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( len( report['tree_types'] ), 1 )

        # NVD 
        report = {}
        report['result_forest'] = [ self.nvd_data1 ]
        report['tree_ids'] = [ "CVE2012" ]
        report['tree_types'] = [ "file" ]

        re_match = ["Windows 7"]
        xugrep = XUGrep()
        report = xugrep.process_re_match( re_match, "", report )
        self.assertEqual( len( report['result_forest'] ), 1 )
        self.assertEqual( report['tree_ids'][0], "CVE2012" )
        self.assertEqual( len( report['tree_ids'] ), 1 )
        self.assertEqual( len( report['re_matches'][0]), 2 )
        self.assertEqual( len( report['re_matches'] ), 1 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( len( report['tree_types'] ), 1 )

        # IOS
        report = {}
        report['result_forest'] = [ self.ios_data1 ]
        report['tree_ids'] = [ "Router" ]
        report['tree_types'] = [ "file" ]

        re_match = ["access-group"]
        xugrep = XUGrep()
        report = xugrep.process_re_match( re_match, "", report )
        self.assertEqual( len( report['result_forest'] ), 1 )
        self.assertEqual( report['tree_ids'][0], "Router" )
        self.assertEqual( len( report['tree_ids'] ), 1 )
        self.assertEqual( len( report['re_matches'][0] ), 2 )
        self.assertEqual( len( report['re_matches'] ), 1 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( len( report['tree_types'] ), 1 )

        # C
        report = {}
        report['result_forest'] = [ self.c_data1 ]
        report['tree_ids'] = ["Example"]
        report['tree_types'] = [ "file" ]

        re_match = ["putchar"]
        xugrep = XUGrep()
        report = xugrep.process_re_match( re_match, "", report )
        self.assertEqual( len( report['result_forest'] ), 1 )
        self.assertEqual( report['tree_ids'][0], "Example" )
        self.assertEqual( len( report['tree_ids'] ), 1 )
        self.assertEqual( len( report['re_matches'][0] ), 2 )
        self.assertEqual( len( report['re_matches'] ), 1 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( len( report['tree_types'] ), 1 )
        
    def test_xugrep(self):
        # a result_forest is a list of text pieces
        report = {}
        report['result_forest'] = [ self.tei_data1 ]
        report['tree_ids'] = ["AIST"]
        report['tree_types'] = [ "file" ]
        report['re_matches'] = []
        xugrep = XUGrep()

        report = xugrep.xugrep( self.tei_xupath1, report )
        self.assertEqual( len( report['result_forest'] ), 2 )
        self.assertEqual( report['tree_ids'][0], "AIST.1" )
        self.assertEqual( report['tree_ids'][1], "AIST.9" )
        self.assertEqual( len( report['tree_ids'] ), 2 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( report['tree_types'][1], "tei:section" )
        self.assertEqual( len( report['tree_types'] ), 2 )

        report = {}
        report['result_forest'] = [ self.tei_data2 ]
        report['tree_ids'] = [ "AIST" ]
        report['tree_types'] = [ "file" ]

        report = xugrep.xugrep( self.tei_xupath2, report )
        self.assertEqual( len( report['result_forest'] ), 1 )
        self.assertEqual( report['tree_ids'][0], "AIST.1.1.1" )
        self.assertEqual( len( report['tree_ids'] ), 1 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( report['tree_types'][1], "tei:section")
        self.assertEqual( report['tree_types'][2], "tei:subsection")
        self.assertEqual( report['tree_types'][3], "tei:subsubsection")
        self.assertEqual( len( report['tree_types'] ), 4 )
        self.assertEqual( len(report['re_matches'][0]), 1 )
        self.assertEqual( len(report['re_matches']), 1 )

        ## NVD
        report = {}
        report['result_forest'] = [ self.nvd_data1 ]
        report['tree_ids'] = [ "CVE2012" ]
        report['tree_types'] = [ "file" ]
        report['re_matches'] = []

        report = xugrep.xugrep( self.nvd_xupath1, report )
        self.assertEqual( len( report['result_forest'] ), 2 )
        self.assertEqual( report['tree_ids'][0], "CVE2012.CVE-2012-0001" )
        self.assertEqual( report['tree_ids'][1], "CVE2012.CVE-2012-0002" )
        self.assertEqual( len( report['tree_ids'] ), 2 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( report['tree_types'][1], "nvd:entry" )
        self.assertEqual( len( report['tree_types'] ), 2 )
        self.assertEqual( len( report['re_matches'][0] ), 1 )
        self.assertEqual( len( report['re_matches'][1] ), 1 )
        self.assertEqual( len( report['re_matches'] ), 2 )
        
        report = {}
        report['result_forest'] = [ self.nvd_data1 ]
        report['tree_ids'] = [ "CVE2012" ]
        report['tree_types'] = [ "file" ]
        report['re_matches'] = []

        report = xugrep.xugrep( self.nvd_xupath2, report )
        self.assertEqual( len( report['result_forest'] ), 2 )
        self.assertEqual( report['tree_ids'][0], "CVE2012.CVE-2012-0001.1" )
        self.assertEqual( report['tree_ids'][1], "CVE2012.CVE-2012-0002.1" )
        self.assertEqual( len( report['tree_ids'] ), 2 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( report['tree_types'][1], "nvd:entry" )
        self.assertEqual( report['tree_types'][2], "nvd:score" )
        self.assertEqual( len( report['tree_types'] ), 3 )
        # undefined:  self.assertEqual( len( report['re_matches'] ), 

        ## Cisco IOS
        report = {}
        report['result_forest'] = [ self.ios_data1 ]
        report['tree_ids'] = [ "Router" ]
        report['tree_types'] = [ "file" ]
        report['re_matches'] = []

        report = xugrep.xugrep( self.ios_xupath1, report )
        self.assertEqual( len( report['result_forest'] ), 2 )
        self.assertEqual( report['tree_ids'][0], "Router.Loopback0" )
        self.assertEqual( report['tree_ids'][1], "Router.GigabitEthernet4/2" )
        self.assertEqual( len( report['tree_ids'] ), 2 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( report['tree_types'][1], "ios:interface" )
        self.assertEqual( len( report['tree_types'] ), 2 )
        self.assertEqual( len( report['re_matches'] ), 0 )

        report = {}
        report['result_forest'] = [ self.ios_data1 ]
        report['tree_ids'] = [ "Router" ]
        report['tree_types'] = [ "file" ]
        report['re_matches'] = []

        report = xugrep.xugrep( self.ios_xupath2, report )
        self.assertEqual( len( report['result_forest'] ), 1 )
        self.assertEqual( report['tree_ids'][0], "Router.GigabitEthernet4/2" )
        self.assertEqual( len( report['tree_ids'] ), 1 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( report['tree_types'][1], "ios:interface" )
        self.assertEqual( len( report['tree_types'] ), 2 )
        self.assertEqual( len(report['re_matches'][0]), 2 )
        self.assertEqual( len(report['re_matches']), 1 )

        report = {}
        report['result_forest'] = [ self.ios_data1 ]
        report['tree_ids'] = [ "Router" ]
        report['tree_types'] = [ "file" ]
        report['re_matches'] = []

        report = xugrep.xugrep( self.ios_xupath3, report )
        self.assertEqual( len( report['result_forest'] ), 9 )
        self.assertEqual( report['tree_ids'][0], "Router.GigabitEthernet4/2.1" )
        self.assertEqual( report['tree_ids'][1], "Router.GigabitEthernet4/2.2" )
        self.assertEqual( len( report['tree_ids'] ), 9 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( report['tree_types'][1], "ios:interface" )
        self.assertEqual( report['tree_types'][2], "ios:line" )
        self.assertEqual( len( report['tree_types'] ), 3 )

        report = {}
        report['result_forest'] = [ self.ios_data1 ]
        report['tree_ids'] = [ "Router" ]
        report['tree_types'] = [ "file" ]
        report['re_matches'] = []

        report = xugrep.xugrep( self.ios_xupath4, report )
        self.assertEqual( len( report['result_forest'] ), 2 )
        self.assertEqual( report['tree_ids'][0], "Router.GigabitEthernet4/2.4" )
        self.assertEqual( report['tree_ids'][1], "Router.GigabitEthernet4/2.5" )
        self.assertEqual( len( report['tree_ids'] ), 2 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( report['tree_types'][1], "ios:interface" )
        self.assertEqual( report['tree_types'][2], "ios:line" )
        self.assertEqual( len( report['tree_types'] ), 3 )
        self.assertEqual( len( report['re_matches'][0] ), 1 )
        self.assertEqual( len( report['re_matches'][1] ), 1 )
        self.assertEqual( len( report['re_matches'] ), 2 )

        report = {}
        report['result_forest'] = [ self.ios_data1 ]
        report['tree_ids'] = [ "Router" ]
        report['tree_types'] = [ "file" ]
        report['re_matches'] = []

        report = xugrep.xugrep( self.ios_xupath5, report )
        self.assertEqual( len( report['result_forest'] ), 16 )
        self.assertEqual( report['tree_ids'][0], "Router.1" )
        self.assertEqual( report['tree_ids'][1], "Router.2" )
        self.assertEqual( len( report['tree_ids'] ), 16 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( report['tree_types'][1], "ios:line" )
        self.assertEqual( len( report['tree_types'] ), 2 )
        
        ## C Functions
        report = {}
        report['result_forest'] = [ self.c_data1 ]
        report['tree_ids'] = [ "Example" ]
        report['tree_types'] = [ "file" ]
        report['re_matches'] = []

        report = xugrep.xugrep( self.c_xupath1, report )
        self.assertEqual( len( report['result_forest'] ), 5 )
        self.assertEqual( report['tree_ids'][0], "Example.putstr" )
        self.assertEqual( report['tree_ids'][1], "Example.fac" )
        self.assertEqual( report['tree_ids'][2], "Example.putn" )
        self.assertEqual( len( report['tree_ids'] ), 5 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( report['tree_types'][1], "cspec:function" )
        self.assertEqual( len( report['tree_types'] ), 2 )

        report = {}
        report['result_forest'] = [ self.c_data1 ]
        report['tree_ids'] = [ "Example" ]
        report['tree_types'] = [ "file" ]
        report['re_matches'] = []

        report = xugrep.xugrep( self.c_xupath2, report )
        self.assertEqual( len( report['result_forest'] ), 2 )
        self.assertEqual( report['tree_ids'][0], "Example.putstr" )
        self.assertEqual( report['tree_ids'][1], "Example.putn" )
        self.assertEqual( len( report['tree_ids'] ), 2 )
        self.assertEqual( report['tree_types'][0], "file" )
        self.assertEqual( report['tree_types'][1], "cspec:function" )
        self.assertEqual( len( report['tree_types'] ), 2 )
        
## Methods to test xuwc
#
#  We want to be more careful to think about the kinds of bugs and
#    exceptions that this utility may throw when it computes a
#    report.
class TestXUWc( unittest.TestCase ):
    
    tei_data_path1 = None
    tei_data_path2 = None
    nvd_data_path1 = None
    ios_data_path1 = None
    c_data_path1 = None

    tei_data1 = None
    tei_data2 = None
    nvd_data1 = None
    ios_data1 = None
    c_data1 = None
    
    # I may want to do something very similar to XML
    tei_xupath1 = "//tei:section"
    tei_xupath2 = "//tei:section/tei:subsection/tei:subsubsection[ re:testsubtree('Globus','gi')]"

    nvd_xupath1 = "//nvd:entry[ re:testsubtree('Windows\s7','gi')]"
    nvd_xupath2 = "//nvd:entry[ re:testsubtree('Windows\s7','gi')]/nvd:score"
    #pattern = re.compile("cpe:.*?a:redhat")    SLASHES BAD IN RE/XPATHCOMBOS

    # I may want to grab all interfaces within a document
    ios_xupath1 = "//ios:interface"
    ios_xupath2 = "//ios:interface[ re:testsubtree('access-group','gi') ]"
    ios_path3 = "//ios:interface[ re:testsubtree('access-group','gi') ]/ios:line"
    ios_xupath4 = "//ios:interface/ios:line[ re:testsubtree('access-group','gi') ]"
    ios_xupath5 = "//ios:line"

    # I may want to be able to grab all C functions in a document
    c_xupath1 = "//cspec:function"
    c_xupath2 = "//cspec:function[ re:testsubtree('putchar','gi') ]"
    c_xupath3 = "//cspec:function/cspec:line[ re:testsubtree('putchar','gi') ]"    

    ## Method run prior to every test
    def setUp(self):
        
        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')

        self.tei_data_path1 = config.get('xutools.test.test_tools', 'TEIDataPath1')
        self.tei_data_path2 = config.get('xutools.test.test_tools', 'TEIDataPath2')
        self.nvd_data_path1 = config.get('xutools.test.test_tools', 'NVDDataPath1')
        self.ios_data_path1 = config.get('xutools.test.test_tools', 'IOSDataPath1')
        self.c_data_path1 = config.get('xutools.test.test_tools', 'CDataPath1')

        fp = open( self.tei_data_path1, 'r' )
        self.tei_data1 = fp.read()
        fp.close()

        fp = open( self.tei_data_path2, 'r' )
        self.tei_data2 = fp.read()
        fp.close()

        fp = open( self.nvd_data_path1, 'r' )
        self.nvd_data1 = fp.read()
        fp.close()

        fp = open( self.ios_data_path1, 'r' )
        self.ios_data1 = fp.read()
        fp.close()

        fp = open( self.c_data_path1, 'r' )
        self.c_data1 = fp.read()
        fp.close()

    def test_get_id_for_idx(self):
        xuwc = XUWc()
        region_id = "file1.1.4"
        self.assertEqual( "file1", xuwc.get_id_for_idx( 0, region_id) )
        self.assertEqual( "file1.1", xuwc.get_id_for_idx(1, region_id))
        self.assertEqual( "file1.1.4", xuwc.get_id_for_idx(2, region_id))
        # not sure if this behavior is most useful
        self.assertEqual( None, xuwc.get_id_for_idx( 3, region_id))

    def test_get_ids_for_idx(self):
        xuwc = XUWc()
        region_ids = [ "file1.1.4", "file1.2.3", "file2.1.1" ]
        new_ids = xuwc.get_ids_for_idx( 0, region_ids )
        self.assertEqual( len(new_ids), 2 )
        self.assertEqual( new_ids[0], "file1" )
        self.assertEqual( new_ids[1], "file2" )
        
        new_ids = xuwc.get_ids_for_idx( 1, region_ids )
        self.assertEqual( len(new_ids), 3 )
        self.assertEqual( new_ids[0], "file1.1" )
        self.assertEqual( new_ids[1], "file1.2" )
        self.assertEqual( new_ids[2], "file2.1" )

        new_ids = xuwc.get_ids_for_idx( 2, region_ids )
        self.assertEqual( len(new_ids), 3 )
        for i in range(0, len(region_ids)):
            self.assertEqual( region_ids[i], new_ids[i] )
        # not sure if this behavior is most useful
        new_ids = xuwc.get_ids_for_idx( 3, region_ids )
        self.assertEqual( len(new_ids), 0 )

    def test_xuwc(self):
        
        # M 1.1:  First test out the some queries when I specify no options
        xpath = "//tei:section"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = None
        wc_params['count_regexp'] = None
        wc_params['context_type'] = None
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len(wc_reports.keys()), 1 )
        self.assertEqual( wc_reports.keys()[0], self.tei_data_path1 )
        wc_report = wc_reports[ self.tei_data_path1 ]

        num_context_regions = len(wc_report.keys())
        self.assertEqual( num_context_regions, 1 )
        self.assertEqual( wc_params['context_type'], "file_path" )
        context_region_id = wc_report.keys()[0]
        self.assertEqual( wc_report[context_region_id], 2 )
        self.assertEqual( wc_params['count_type'], "tei:section" )
        
        # M 1.2
        xpath = "//tei:section/tei:subsection/tei:subsubsection[re:testsubtree('Globus','gi')]"
        file_paths = [ self.tei_data_path1, self.tei_data_path2 ]
        wc_params = {}
        wc_params['count_type'] = None
        wc_params['count_regexp'] = None
        wc_params['context_type'] = None
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len(wc_reports.keys()), 2 )
        self.assertEqual( wc_reports.keys()[0], self.tei_data_path1 )
        self.assertEqual( wc_reports.keys()[1], self.tei_data_path2 )

        wc_report = wc_reports[ self.tei_data_path1 ]
        num_context_regions = len( wc_report.keys() )
        self.assertEqual( num_context_regions, 1 )
        self.assertEqual( wc_params['context_type'], "file_path" )
        context_region_id = wc_report.keys()[0]
        self.assertEqual( wc_report[context_region_id], 1 )
        self.assertEqual( wc_params['count_type'], "tei:subsubsection")

        wc_report = wc_reports[ self.tei_data_path2 ]
        num_context_regions = len( wc_report.keys() )
        self.assertEqual( num_context_regions, 1 )
        self.assertEqual( wc_params['context_type'], "file_path" )
        context_region_id = wc_report.keys()[0]
        self.assertEqual( wc_report[context_region_id], 1 )
        self.assertEqual( wc_params['count_type'], "tei:subsubsection")

        # M 2.1  Override count
        xpath = "//ios:interface"
        file_paths = [ self.ios_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = "builtin:byte"
        wc_params['count_regexp'] = None
        wc_params['context_type'] = "ios:interface"
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len(wc_reports.keys()), 1 )
        self.assertEqual( wc_reports.keys()[0], self.ios_data_path1 )

        wc_report = wc_reports[ self.ios_data_path1 ]
        num_context_regions = len( wc_report.keys() )
        self.assertEqual( num_context_regions, 2 )
        self.assertEqual( wc_params['context_type'], "ios:interface" )
        key_prefix = self.ios_data_path1.replace('.','_')
        context_region1_id = key_prefix + ".Loopback0"
        context_region2_id = key_prefix + ".GigabitEthernet4/2"
        self.assertEqual( wc_report[context_region1_id], 186 )
        self.assertEqual( wc_report[context_region2_id], 232 )
        self.assertEqual( wc_params['count_type'], "builtin:byte" )

        # M 2.3 
        file_paths = [ self.ios_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = "builtin:word"
        wc_params['count_regexp'] = None
        wc_params['context_type'] = "ios:interface"
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len(wc_reports.keys()), 1 )
        self.assertEqual( wc_reports.keys()[0], self.ios_data_path1 )

        wc_report = wc_reports[ self.ios_data_path1 ]
        num_context_regions = len( wc_report.keys() )
        self.assertEqual( num_context_regions, 2 )
        self.assertEqual( wc_params['context_type'], "ios:interface" )

        key_prefix = self.ios_data_path1.replace('.','_')
        context_region1_id = key_prefix + ".Loopback0"
        context_region2_id = key_prefix + ".GigabitEthernet4/2"
        self.assertEqual( wc_report[context_region1_id], 23 )
        self.assertEqual( wc_report[context_region2_id], 27 )
        self.assertEqual( wc_params['count_type'], "builtin:word" )

        # M 2.4
        file_paths = [ self.ios_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = "builtin:character"
        wc_params['count_regexp'] = None
        wc_params['context_type'] = "ios:interface"
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len(wc_reports.keys()), 1 )
        self.assertEqual( wc_reports.keys()[0], self.ios_data_path1 )

        wc_report = wc_reports[ self.ios_data_path1 ]
        num_context_regions = len( wc_report.keys() )
        self.assertEqual( num_context_regions, 2 )
        self.assertEqual( wc_params['context_type'], "ios:interface" )
        key_prefix = self.ios_data_path1.replace('.','_')
        context_region1_id = key_prefix + ".Loopback0"
        context_region2_id = key_prefix + ".GigabitEthernet4/2"
        self.assertEqual( wc_report[context_region1_id], 186 )
        self.assertEqual( wc_report[context_region2_id], 232 )
        self.assertEqual( wc_params['count_type'], "builtin:character" )

        # M 2.5
        # This one should generate an error
        xpath = "//tei:section"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = "tei:subsection"
        wc_params['count_regexp'] = None
        wc_params['context_type'] = None
        wc_params['context_regexp'] = None
        #wc_reports = HWc.hwc_main( xpath, file_paths, wc_params )
        
        # M 2.6
        xpath = "//tei:section/tei:subsection/tei:subsubsection"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = "tei:subsection"
        wc_params['count_regexp'] = None
        wc_params['context_type'] = None
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len(wc_reports.keys()), 1 )
        self.assertEqual( wc_reports.keys()[0], self.tei_data_path1 )

        wc_report = wc_reports[ self.tei_data_path1 ]
        num_context_regions = len( wc_report.keys() )
        self.assertEqual( num_context_regions, 1 )
        self.assertEqual( wc_params['context_type'], "file_path" )
        context_region_id = wc_report.keys()[0]
        self.assertEqual( wc_report[context_region_id], 1 )
        self.assertEqual( wc_params['count_type'], "tei:subsection" )

        # M 3.1
        xpath = "//tei:section"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = None
        wc_params['count_regexp'] = "\w+"
        wc_params['context_type'] = "tei:section"
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len(wc_reports.keys()), 1 )
        self.assertEqual( wc_reports.keys()[0], self.tei_data_path1 )
        wc_report = wc_reports[ self.tei_data_path1 ]

        num_context_regions = len(wc_report.keys())
        self.assertEqual( num_context_regions, 2 )
        self.assertEqual( wc_params['context_type'], "tei:section" )
        key_prefix = self.tei_data_path1.replace('.','_')
        context_region1_id = key_prefix + ".1"
        context_region2_id = key_prefix + ".9"
        self.assertEqual( wc_report[context_region1_id], 357 )
        self.assertEqual( wc_report[context_region2_id], 45 )
        self.assertEqual( wc_params['count_regexp'], "\w+" )

        # M 4.1  context override
        xpath = "//tei:section/tei:p"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = None
        wc_params['count_regexp'] = None
        wc_params['context_type'] = "tei:section"
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len(wc_reports.keys()), 1 )
        self.assertEqual( wc_reports.keys()[0], self.tei_data_path1 )
        wc_report = wc_reports[ self.tei_data_path1 ]

        num_context_regions = len(wc_report.keys())
        self.assertEqual( num_context_regions, 2 )
        self.assertEqual( wc_params['context_type'], "tei:section" )
        section1_context_region_id = wc_report.keys()[0]
        section2_context_region_id = wc_report.keys()[1]
        self.assertEqual( wc_report[ section1_context_region_id ], 5 )
        self.assertEqual( wc_report[ section2_context_region_id ], 1 )
        self.assertEqual( wc_params['count_type'], "tei:p" )

        # M 4.2 should generate an error
        xpath = "//tei:section/tei:p"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = None
        wc_params['count_regexp'] = None
        wc_params['context_type'] = "tei:subsection"
        wc_params['context_regexp'] = None
        #wc_reports = HWc.hwc_main( xpath, file_paths, wc_params )
        
        # M 4.3 should generate an error
        xpath = "//tei:section/tei:subsection"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = None
        wc_params['count_regexp'] = None
        wc_params['context_type'] = "tei:subsubsection"
        wc_params['context_regexp'] = None
        #wc_reports = HWc.hwc_main( xpath, file_paths, wc_params )

        # M 4.4 
        xpath = "//tei:section/tei:p"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = None
        wc_params['count_regexp'] = None
        wc_params['context_type'] = "tei:p"
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len(wc_reports.keys()), 1 )
        self.assertEqual( wc_reports.keys()[0], self.tei_data_path1 )
        wc_report = wc_reports[ self.tei_data_path1 ]

        num_context_regions = len(wc_report.keys())
        self.assertEqual( num_context_regions, 6 )
        self.assertEqual( wc_params['context_type'], "tei:p" )
        for context_region_id in wc_report.keys():
            self.assertEqual( wc_report[context_region_id], 1 )
        self.assertEqual( wc_params['count_type'], "tei:p" )
        
        # M 4.5
        xpath = "//tei:section/tei:subsection/tei:p"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = None
        wc_params['count_regexp'] = None
        wc_params['context_type'] = "tei:subsection"
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len(wc_reports.keys()), 1 )
        self.assertEqual( wc_reports.keys()[0], self.tei_data_path1 )
        wc_report = wc_reports[ self.tei_data_path1 ]

        num_context_regions = len( wc_report.keys() )
        self.assertEqual( num_context_regions, 1 )
        self.assertEqual( wc_params['context_type'], "tei:subsection")
        section1_context_region_id = wc_report.keys()[0]
        self.assertEqual( wc_report[ section1_context_region_id ], 4 )
        self.assertEqual( wc_params['count_type'], "tei:p" )

        # M 4.6
        xpath = "//tei:section/tei:subsection/tei:p"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = None
        wc_params['count_regexp'] = None
        wc_params['context_type'] = "tei:section"
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len(wc_reports.keys()), 1 )
        self.assertEqual( wc_reports.keys()[0], self.tei_data_path1 )
        wc_report = wc_reports[ self.tei_data_path1 ]

        num_context_regions = len( wc_report.keys() )
        self.assertEqual( num_context_regions, 1 )
        self.assertEqual( wc_params['context_type'], "tei:section")
        section1_context_region_id = wc_report.keys()[0]
        self.assertEqual( wc_report[ section1_context_region_id ], 4 )
        self.assertEqual( wc_params['count_type'], "tei:p" )

        # M 4.7
        xpath = "//tei:section/tei:p"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = None
        wc_params['count_regexp'] = None
        wc_params['context_type'] = "tei:section"
        wc_params['context_regexp'] = None
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )
        self.assertEqual( len( wc_reports.keys() ), 1 )
        self.assertEqual( wc_reports.keys()[0], self.tei_data_path1 )
        wc_report = wc_reports[ self.tei_data_path1 ]

        num_context_regions = len( wc_report.keys() )
        self.assertEqual( num_context_regions, 2 )
        self.assertEqual( wc_params['context_type'], "tei:section")
        section1_context_region_id = wc_report.keys()[0]
        section9_context_region_id = wc_report.keys()[1]
        self.assertEqual( wc_report[ section1_context_region_id ], 5 )
        self.assertEqual( wc_report[ section9_context_region_id ], 1 )
        self.assertEqual( wc_params['count_type'], "tei:p" )

        # M 4.8 - should explode
        xpath = "//tei:section/tei:p"
        file_paths = [ self.tei_data_path1 ]
        wc_params = {}
        wc_params['count_type'] = None
        wc_params['count_regexp'] = None
        wc_params['context_type'] = None
        wc_params['context_regexp'] = "builtin:line"
        wc_reports = XUWc.xuwc_main( xpath, file_paths, wc_params )        


## Methods to test xudiff.
#
#  We want to be more careful to think about the kinds of bugs and exceptions 
#   that this utility may throw when it computes an edit script.
class TestXUDiff( unittest.TestCase ):

    tei_data_path1 = None
    tei_data_path2 = None
    nvd_data_path1 = None
    ios_data_path1 = None
    c_data_path1 = None

    tei_data1 = None
    tei_data2 = None
    nvd_data1 = None
    ios_data1 = None
    c_data1 = None
    
    # Example 4 T1 in Zhang Shasha paper
    a1 = TD.create_node( None, "a", "line", [] )
    b1 = TD.create_node( None, "b", "line", [] )
    c1 = TD.create_node( None, "c", "paragraph", [ b1 ] )
    d1 = TD.create_node( None, "d", "section", [ a1, c1 ] )
    e1 = TD.create_node( None, "e", "section", [] )
    f1 = TD.create_node( None, "f", "text", [ d1, e1 ] )
    t1 = f1

    ## Method run prior to every test
    def setUp(self):
        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')

        self.tei_data_path1 = config.get('xutools.test.test_tools', 'TEIDataPath1')
        self.tei_data_path2 = config.get('xutools.test.test_tools', 'TEIDataPath2')
        self.nvd_data_path1 = config.get('xutools.test.test_tools', 'NVDDataPath1')
        self.ios_data_path1 = config.get('xutools.test.test_tools', 'IOSDataPath1')
        self.c_data_path1 = config.get('xutools.test.test_tools', 'CDataPath1')

        fp = open( self.tei_data_path1, 'r' )
        self.tei_data1 = fp.read()
        fp.close()

        fp = open( self.tei_data_path2, 'r' )
        self.tei_data2 = fp.read()
        fp.close()

        fp = open( self.nvd_data_path1, 'r' )
        self.nvd_data1 = fp.read()
        fp.close()

        fp = open( self.ios_data_path1, 'r' )
        self.ios_data1 = fp.read()
        fp.close()

        fp = open( self.c_data_path1, 'r' )
        self.c_data1 = fp.read()
        fp.close()

    def test_compute_type_list( self ):
        params = { 'pos':1, 'pos2type':[] }
        [ t1, params ] = TD.postorder_traverse( self.t1, params, XUDiff.compute_type_list )
        self.assertEqual( len(params['pos2type']), 6 )
        
        expected_types = [ "line", "line", "paragraph", "section", "section", "text" ]
        for i in range(0, len( params['pos2type'] ) ):
            self.assertEqual( params['pos2type'][i], expected_types[i] )
            i = i + 1

    def test_compute_references(self):
        params = { 'pos2ref':[], 'stack':[], 'refKey':'label' }
        [ self.t1, params ] = TD.preorder_traverse( self.t1, params, XUDiff.compute_references )
        [ self.t1, params ] = TD.postorder_traverse( self.t1, params, XUDiff.compute_reference_list )
        
        expected_ref = [ "f.d.a", "f.d.c.b", "f.d.c", "f.d", "f.e", "f" ]
        for i in range(0, len( params['pos2ref']), 6 ):
            self.assertEqual( params['pos2ref'][i], expected_ref[i] )
            i = i + 1
    
    def test_process_cf_match( self ):
        # TEI
        cf_match = ["tei:section"]
        report = {}
        report['result_forest_0'] = [ self.tei_data1 ]
        report['result_parse_tree_0'] = []
        report['pos2types0'] = []
        report['pos2refs0'] = []

        report['result_forest_1'] = [ self.tei_data2 ]
        report['result_parse_tree_1'] = []
        report['pos2types1'] = []
        report['pos2refs1'] = []

        xudiff = XUDiff()
        report = xudiff.process_cf_match( cf_match, "", report )
        self.assertEqual( len( report['result_parse_tree_0'] ), 2 )
        self.assertEqual( len( report['pos2types0'] ), 2 )
        self.assertTrue( len( report['pos2types0'][0] ) > 0 )
        self.assertTrue( len( report['pos2types0'][1] ) > 0 )
        self.assertEqual( len( report['pos2refs0'] ), 2 )
        self.assertTrue( len( report['pos2refs0'][0] ) > 0 )
        self.assertTrue( len( report['pos2refs0'][1] ) > 0 )

        self.assertEqual( len( report['result_parse_tree_1'] ), 2 )
        self.assertEqual( len( report['pos2types1'] ), 2 )
        self.assertTrue( len( report['pos2types1'][0] ) > 0 )
        self.assertTrue( len( report['pos2types1'][1] ) > 0 )
        self.assertEqual( len( report['pos2refs1'] ), 2 )
        self.assertTrue( len( report['pos2refs1'][0] ) > 0 )
        self.assertTrue( len( report['pos2refs1'][1] ) > 0 )

        # IOS
        cf_match = ["ios:config"]
        report = {}
        report['result_forest_0'] = [ self.ios_data1 ]
        report['result_parse_tree_0'] = []
        report['pos2types0'] = []
        report['pos2refs0'] = []

        report['result_forest_1'] = [ self.ios_data1 ]
        report['result_parse_tree_1'] = []
        report['pos2types1'] = []
        report['pos2refs1'] = []

        xudiff = XUDiff()
        report = xudiff.process_cf_match( cf_match, "", report )
        self.assertEqual( len( report['result_parse_tree_0'] ), 1 )
        self.assertEqual( len( report['pos2types0'] ), 1 )
        self.assertTrue( len( report['pos2types0'][0] ) > 0 )
        self.assertEqual( len( report['pos2refs0'] ), 1 )
        self.assertTrue( len( report['pos2refs0'][0] ) > 0 )

        self.assertEqual( len( report['result_parse_tree_1'] ), 1 )
        self.assertEqual( len( report['pos2types1'] ), 1 )
        self.assertTrue( len( report['pos2types1'][0] ) > 0 )        
        self.assertEqual( len( report['pos2refs1'] ), 1 )
        self.assertTrue( len( report['pos2refs1'][0] ) > 0 )
