"""
copyright (c) 2010-2012, Gabriel A. Weaver, Department of Computer
Science at Dartmouth College. <gabriel.a.l.weaver@gmail.com>

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
import os
from pyparsing import *
import pprint
from xutools.corpus import CorpusElement
from xutools.grammar.pyparsing.BuiltinGrammar import BuiltinGrammar
from xutools.grammar.pyparsing.CiscoIOSGrammar import CiscoIOSGrammar
from xutools.grammar.pyparsing.TEIXMLGrammar import TEIXMLGrammar
from xutools.tools import XUGrep, XUWc
import unittest

## @package test
#    This module contains methods to test our XUTools


#  We want to be more careful to think about the kinds of bugs and 
#   exceptions that this utility may throw when it computes a result
#   set.
class TestXUGrep( unittest.TestCase ):

    tei_data_path1 = None
    tei_data_path2 = None
    tei_data_path3 = None

    ios_data_path1 = None


    tei_data1 = None
    tei_data2 = None
    tei_data3 = None

    ios_data1 = None

    # I may want to do something very similar to XML
    tei_xupath1 = "//tei:section"
    tei_xupath2 = "//tei:section/tei:subsection/tei:subsubsection[ re:testsubtree('Globus','gi')]"

    # I may want to grab all interfaces within a document
    ios_xupath1 = "//ios:interface"
    ios_xupath2 = "//ios:interface[ re:testsubtree('access-group','gi') ]"
    ios_xupath3 = "//ios:interface[ re:testsubtree('access-group','gi') ]/ios:line"
    ios_xupath4 = "//ios:interface/ios:line[ re:testsubtree('access-group','gi') ]"
    ios_xupath5 = "//ios:line"

    def setUp(self):

        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')

        self.tei_data_path1 = config.get('xutools.test.test_tools', 'TEIDataPath1')
        self.tei_data_path2 = config.get('xutools.test.test_tools', 'TEIDataPath2')
        self.tei_data_path3 = config.get('xutools.test.test_tools', 'TEIDataPath3')
        self.ios_data_path1 = config.get('xutools.test.test_tools', 'IOSDataPath1')

        fp = open( self.tei_data_path1, 'r' )
        self.tei_data1 = fp.read()
        fp.close()

        fp = open( self.tei_data_path2, 'r' )
        self.tei_data2 = fp.read()
        fp.close()
        
        fp = open( self.tei_data_path3, 'r' )
        self.tei_data3 = fp.read()
        fp.close()

        fp = open( self.ios_data_path1, 'r' )
        self.ios_data1 = fp.read()
        fp.close()
        
    def test_xugrep(self):
        file_paths = [ self.tei_data_path1, self.tei_data_path2 ]
        element_equality_fields = [ CorpusElement.LABEL_PATH,\
                                        CorpusElement.LANGUAGE_NAME_PATH,\
                                        CorpusElement.TEXT ]
        xugrep = XUGrep.create(self.tei_xupath1, file_paths, element_equality_fields)
        self.assertEqual( len( xugrep.corpus ), 4 )
        
        xugrep = XUGrep.create(self.tei_xupath2, file_paths, element_equality_fields)
        self.assertEqual( len( xugrep.corpus ),  2 )
        attribute_names = [ CorpusElement.LABEL_PATH,\
                                CorpusElement.LANGUAGE_NAME_PATH,\
                                CorpusElement.TEXT ]
        results = xugrep.corpus.output( attribute_names, tabulate=True )
        print "\n"
        print "\n".join(results)

class TestXUWc( unittest.TestCase ):
    
    tei_data_path1 = None
    tei_data_path2 = None
    tei_data_path3 = None
    ios_data_path1 = None

    tei_data1 = None
    tei_data2 = None
    ios_data1 = None

    tei_xupath1 = "//tei:section"
    tei_xupath2 = "//tei:section/tei:subsection/tei:subsubsection[ re:testsubtree('Globus','gi')]"

    ios_xupath1 = "//ios:interface"
    ios_xupath2 = "//ios:interface[ re:testsubtree('access-group','gi') ]"
    ios_xupath4 = "//ios:interface/ios:line[ re:testsubtree('access-group','gi') ]"

    def setUp(self):
        
        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')

        self.tei_data_path1 = config.get('xutools.test.test_tools', 'TEIDataPath1')
        self.tei_data_path2 = config.get('xutools.test.test_tools', 'TEIDataPath2')
        self.tei_data_path3 = config.get('xutools.test.test_tools', 'TEIDataPath3')
        self.ios_data_path1 = config.get('xutools.test.test_tools', 'IOSDataPath1')

        fp = open( self.tei_data_path1, 'r' )
        self.tei_data1 = fp.read()
        fp.close()

        fp = open( self.tei_data_path2, 'r' )
        self.tei_data2 = fp.read()
        fp.close()
        
        fp = open( self.tei_data_path3, 'r' )
        self.tei_data3 = fp.read()
        fp.close()

        fp = open( self.ios_data_path1, 'r' )
        self.ios_data1 = fp.read()
        fp.close()

    def test_xuwc(self):
        
        # M 1.1:  First test out some queries where I specify no options
        xupath = self.tei_xupath1
        file_paths = [ self.tei_data_path1 ]
        count_unit = TEIXMLGrammar.SECTION
        container_unit = BuiltinGrammar.FILE
        label_path_delimiter = ":"
        element_equality_fields = [ CorpusElement.LABEL_PATH,\
                                        CorpusElement.LANGUAGE_NAME_PATH,\
                                        CorpusElement.TEXT ]

        xuwc = XUWc.create(xupath, file_paths, element_equality_fields, count_unit, container_unit, label_path_delimiter)
        self.assertEqual( xuwc.get_container_unit(), BuiltinGrammar.FILE )
        #container_corpus = xuwc.get_container_corpus()
        #self.assertEqual( len(container_corpus), 1)
        #container_idx = 0
        #self.assertEqual( container_corpus[container_idx].get_file_path(), self.tei_data_path1 )
        
        self.assertEqual( xuwc.get_count_unit(), TEIXMLGrammar.SECTION )
        counts = xuwc.get_counts()
        key = os.path.basename(self.tei_data_path1)
        self.assertEqual( counts[key], 2 )
        
        # M 1.2
        xupath = self.tei_xupath2
        file_paths = [ self.tei_data_path1, self.tei_data_path2 ]
        count_unit = TEIXMLGrammar.SUBSUBSECTION
        container_unit = BuiltinGrammar.FILE
        label_path_delimiter = ":" 

        xuwc = XUWc.create(xupath, file_paths, element_equality_fields, count_unit, container_unit, label_path_delimiter)
        self.assertEqual( xuwc.get_container_unit(), BuiltinGrammar.FILE )
        self.assertEqual( xuwc.get_count_unit(), TEIXMLGrammar.SUBSUBSECTION )
        counts = xuwc.get_counts()
        # There is only one subsubsection with 'Globus' in it and its in v1
        self.assertEqual( len(counts.keys()), 2 )
        key = os.path.basename(self.tei_data_path1)
        self.assertEqual( counts[key], 1 )
        
        # M 2.1 Override count
        xupath = self.ios_xupath1
        file_paths = [ self.ios_data_path1 ]
        count_unit = BuiltinGrammar.BYTE
        container_unit = CiscoIOSGrammar.INTERFACE
        label_path_delimiter = ":"

        xuwc = XUWc.create(xupath, file_paths, element_equality_fields, count_unit, container_unit, label_path_delimiter)
        self.assertEqual( xuwc.get_container_unit(), CiscoIOSGrammar.INTERFACE )
        self.assertEqual( xuwc.get_count_unit(), BuiltinGrammar.BYTE )
        counts = xuwc.get_counts()
        self.assertEqual( len(counts.keys()), 2 )
        key1 = label_path_delimiter.join(["router.v1.example", "Loopback0"])
        key2 = label_path_delimiter.join(["router.v1.example", "GigabitEthernet4/2"])
        
        self.assertEqual( counts[key1], 186 )
        self.assertEqual( counts[key2], 232 )
        
        # M 2.3
        xupath = self.ios_xupath1
        file_paths = [ self.ios_data_path1 ] 
        count_unit = BuiltinGrammar.WORD
        container_unit = CiscoIOSGrammar.INTERFACE
        label_path_delimiter = ":"
        
        xuwc = XUWc.create(xupath, file_paths, element_equality_fields, count_unit, container_unit, label_path_delimiter)
        self.assertEqual( xuwc.get_container_unit(), CiscoIOSGrammar.INTERFACE )
        self.assertEqual( xuwc.get_count_unit(), BuiltinGrammar.WORD )
        counts = xuwc.get_counts()
        key1 = label_path_delimiter.join(["router.v1.example", "Loopback0"])
        key2 = label_path_delimiter.join(["router.v1.example", "GigabitEthernet4/2"])
        
        self.assertEqual( counts[key1], 23 )
        self.assertEqual( counts[key2], 27 )

        # M 2.4
        xupath = self.ios_xupath1
        file_paths = [ self.ios_data_path1 ]
        count_unit = BuiltinGrammar.CHARACTER
        container_unit = CiscoIOSGrammar.INTERFACE
        label_path_delimiter = ":"
        
        xuwc = XUWc.create(xupath, file_paths, element_equality_fields, count_unit, container_unit, label_path_delimiter)
        self.assertEqual( xuwc.get_container_unit(), CiscoIOSGrammar.INTERFACE )
        self.assertEqual( xuwc.get_count_unit(), BuiltinGrammar.CHARACTER )
        counts = xuwc.get_counts()
        key1 = label_path_delimiter.join(["router.v1.example", "Loopback0"])
        key2 = label_path_delimiter.join(["router.v1.example", "GigabitEthernet4/2"])

        self.assertEqual( counts[key1], 186 )
        self.assertEqual( counts[key2], 232 )

        """
        # M 2.6
        #   This is a case that we don't yet implement AND
        #     to query number of subsections that satisfy, we need a predicate
        xupath = "/".join( [ TEIXMLGrammar.SECTION, TEIXMLGrammar.SUBSECTION, TEIXMLGrammar.SUBSUBSECTION ] )
        file_paths = [ self.tei_data_path1 ]
        count_unit = TEIXMLGrammar.SUBSECTION
        container_unit = BuiltinGrammar.FILE
        label_path_delimiter = ":"
        
        xuwc = XUWc.create(xupath, file_paths, count_unit, container_unit, label_path_delimiter)
        self.assertEqual( xuwc.get_container_unit(), BuiltinGrammar.FILE )
        self.assertEqual( xuwc.get_count_unit(), TEIXMLGrammar.SUBSECTION )
        counts = xuwc.get_counts()
        label_path_keys = counts.keys()
        self.assertEqual( len(label_path_keys), 1 )
        key = label_path_keys[0]
        self.assertEqual( counts[key], 1 )
        """
        
        # M 4.1
        xupath = "/".join( [ TEIXMLGrammar.SECTION, TEIXMLGrammar.PARAGRAPH ] )
        file_paths = [ self.tei_data_path1 ]
        count_unit = TEIXMLGrammar.PARAGRAPH
        container_unit = TEIXMLGrammar.SECTION
        label_path_delimiter = ":"
        
        xuwc = XUWc.create(xupath, file_paths, element_equality_fields, count_unit, container_unit, label_path_delimiter)
        self.assertEqual( xuwc.get_container_unit(), TEIXMLGrammar.SECTION )
        self.assertEqual( xuwc.get_count_unit(), TEIXMLGrammar.PARAGRAPH )
        counts = xuwc.get_counts()
        ## There are two sections
        self.assertEqual( len(counts.keys()), 2 )
        key1 = label_path_delimiter.join(["section.tei.v1.xml", "1 INTRODUCTION"])
        key2 = label_path_delimiter.join(["section.tei.v1.xml", "9. Glossary"])

        # should be 4 and not 5 since the paragraphs in subsubsection2 are the same
        #   under our base equality function
        self.assertEqual( counts[key1], 4)
        self.assertEqual( counts[key2], 1)        
        
        """
        # M 4.4 I'm not sure what this test even means
        xupath = "/".join([ TEIXMLGrammar.SECTION, TEIXMLGrammar.PARAGRAPH ] )
        file_paths = [ self.tei_data_path1 ]
        count_unit = TEIXMLGrammar.PARAGRAPH
        container_unit = TEIXMLGrammar.PARAGRAPH
        label_path_delimiter = ":"
        
        xuwc = XUWc.create(xupath, file_paths, count_unit, container_unit, label_path_delimiter)
        self.assertEqual( xuwc.get_container_unit(), TEIXMLGrammar.PARAGRAPH )
        self.assertEqual( xuwc.get_count_unit(), TEIXMLGrammar.PARAGRAPH )
        counts = xuwc.get_counts()
        print counts.keys()
        self.assertEqual( len(counts.keys()), 6 )
        """

        # M 4.5
        xupath = "/".join([ TEIXMLGrammar.SECTION, TEIXMLGrammar.SUBSECTION, TEIXMLGrammar.PARAGRAPH] )
        file_paths = [ self.tei_data_path1 ]
        count_unit = TEIXMLGrammar.PARAGRAPH
        container_unit = TEIXMLGrammar.SUBSECTION
        label_path_delimiter = ":"

        xuwc = XUWc.create(xupath, file_paths, element_equality_fields, count_unit, container_unit, label_path_delimiter)
        self.assertEqual( xuwc.get_container_unit(), TEIXMLGrammar.SUBSECTION )
        self.assertEqual( xuwc.get_count_unit(), TEIXMLGrammar.PARAGRAPH )
        counts = xuwc.get_counts()
        self.assertEqual( len(counts.keys()), 1)
        key = counts.keys()[0]
        self.assertEqual( counts[key], 3 )
        
        # M 4.6
        xupath = "/".join([ TEIXMLGrammar.SECTION, TEIXMLGrammar.SUBSECTION, TEIXMLGrammar.PARAGRAPH] )
        file_paths = [ self.tei_data_path1 ]
        count_unit = TEIXMLGrammar.PARAGRAPH
        container_unit = TEIXMLGrammar.SECTION
        label_path_delimiter = ":"
        
        xuwc = XUWc.create(xupath, file_paths, element_equality_fields, count_unit, container_unit, label_path_delimiter)
        self.assertEqual( xuwc.get_container_unit(), TEIXMLGrammar.SECTION )
        self.assertEqual( xuwc.get_count_unit(), TEIXMLGrammar.PARAGRAPH )
        counts = xuwc.get_counts()
        # There is only 1 section that contains a subsection
        self.assertEqual( len(counts.keys()), 1)
        key = counts.keys()[0]
        # There are 3 paragraphs contained within the subsection
        self.assertEqual( counts[key], 3 )
        
        # M 4.7
        xupath = "/".join([ TEIXMLGrammar.SECTION, TEIXMLGrammar.PARAGRAPH ] )
        file_paths = [ self.tei_data_path1 ]
        count_unit = TEIXMLGrammar.PARAGRAPH
        container_unit = TEIXMLGrammar.SECTION
        label_path_delimiter = ":"
        
        xuwc = XUWc.create(xupath, file_paths, element_equality_fields, count_unit, container_unit, label_path_delimiter)
        self.assertEqual( xuwc.get_container_unit(), TEIXMLGrammar.SECTION )
        self.assertEqual( xuwc.get_count_unit(), TEIXMLGrammar.PARAGRAPH )
        counts = xuwc.get_counts()
        self.assertEqual( len(counts.keys()), 2)
        key1 = label_path_delimiter.join( ["section.tei.v1.xml","1 INTRODUCTION"] )
        key2 = label_path_delimiter.join( ["section.tei.v1.xml","9. Glossary"] )
        self.assertEqual( counts[key1], 4)
        self.assertEqual( counts[key2], 1)
        
        # M 4.8
        xupath = "/".join([ TEIXMLGrammar.SECTION, TEIXMLGrammar.PARAGRAPH, BuiltinGrammar.LINE ] )
        file_paths = [ self.tei_data_path1 ]
        count_unit = TEIXMLGrammar.PARAGRAPH
        container_unit = BuiltinGrammar.LINE
        label_path_delimiter = ":"

        with self.assertRaises(IndexError):
            xuwc = XUWc.create(xupath, file_paths, element_equality_fields, count_unit, container_unit, label_path_delimiter)
