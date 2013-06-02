"""
copyright (c) 2013 Gabriel A. Weaver <gabriel.a.l.weaver@gmail.com>

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
from operator import attrgetter
import os
from pyparsing import *
import pprint
from xutools.corpus import Corpus, CorpusElement
from xutools.grammar.pyparsing.BuiltinGrammar import BuiltinGrammar
from xutools.grammar.pyparsing.CiscoIOSGrammar import CiscoIOSGrammar
from xutools.grammar.pyparsing.TEIXMLGrammar import TEIXMLGrammar 
import unittest

## @package test
#    This module contains methods to test our XUTools Corpus

class TestCorpus( unittest.TestCase ):
    tei_data_path1 = None
    tei_data_path2 = None
    tei_data_path3 = None

    tei_data1 = None
    tei_data2 = None
    tei_data3 = None

    element_equality_fields = [ CorpusElement.LABEL_PATH, CorpusElement.LANGUAGE_NAME_PATH, CorpusElement.TEXT ]

    def setUp(self):
        
        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')
        
        self.tei_data_path1 = config.get('xutools.test.test_corpus', 'TEIDataPath1')
        self.tei_data_path2 = config.get('xutools.test.test_corpus', 'TEIDataPath2')
        self.tei_data_path3 = config.get('xutools.test.test_corpus', 'TEIDataPath3') 

    def test_create_from_files(self):
        file_paths = [ self.tei_data_path1, self.tei_data_path2 ]
        result_corpus = Corpus.create_from_files( file_paths, self.element_equality_fields )
        self.assertEqual( len( result_corpus ), 2 )
        # The result should be 1, these have identical label,
        #   language_name, and text fields
        path_field_equality_components = { "label_path":[0] }
        path_field_equality_components_is_whitelist = False
        result_corpus = Corpus.create_from_files( file_paths, self.element_equality_fields,\
                                                  path_field_equality_components,\
                                                  path_field_equality_components_is_whitelist)
        self.assertEqual( len( result_corpus ), 1 )        

        file_paths = [ self.tei_data_path1, self.tei_data_path3 ]
        result_corpus = Corpus.create_from_files( file_paths, self.element_equality_fields )
        self.assertEqual( len( result_corpus ), 2 )

    def test_parse(self):
        file_paths = [ self.tei_data_path1, self.tei_data_path3 ]
        result_corpus = Corpus.create_from_files( file_paths, self.element_equality_fields )

        sections_corpus = result_corpus.parse( TEIXMLGrammar.SECTION )
        self.assertEqual( len( sections_corpus ), 4 )
        result_corpus = Corpus.create_from_files( file_paths, self.element_equality_fields )
        self.assertEqual( len(result_corpus), 2 )

        # We should get three different sections here since v3 is missing
        #  subsubsection 1.1.1.  But both files have section 9 in common.
        path_field_equality_components = { "label_path":[0] }
        path_field_equality_components_is_whitelist = False
        sections_corpus = result_corpus.parse( TEIXMLGrammar.SECTION )
        sections_corpus.apply_path_field_equality_components( path_field_equality_components,\
                                                                  path_field_equality_components_is_whitelist )
        self.assertEqual( len( sections_corpus ), 3 )

        ssections_corpus = sections_corpus.parse( TEIXMLGrammar.SUBSECTION )
        self.assertEqual( len( ssections_corpus ), 2 )
        # We should get two different subsections here.  Each document only
        #  has one subsection but one lacks sssection 1.1.1
        path_field_equality_components = { "label_path":[0] }
        path_field_equality_components_is_whitelist = False
        ssections_corpus.apply_path_field_equality_components( path_field_equality_components,\
                                                                   path_field_equality_components_is_whitelist )
        
        sssections_corpus = ssections_corpus.parse( TEIXMLGrammar.SUBSUBSECTION )
        self.assertEqual( len( sssections_corpus ), 2 )
        # We should get two different subsubsections here.  One is shared by
        #  v1 and v3, the other only appears in v1


        # Now switch over to version 1 and version 2
        file_paths = [ self.tei_data_path1, self.tei_data_path2 ]
        result_corpus = Corpus.create_from_files( file_paths, self.element_equality_fields )
        sections_corpus = result_corpus.parse( TEIXMLGrammar.SECTION )
        self.assertEqual( len( sections_corpus ), 4 )
        # We should get 2 sections here since these are identical modulo file path

    def test_filter(self):
        file_paths = [ self.tei_data_path1, self.tei_data_path3 ]
        result_corpus = Corpus.create_from_files( file_paths, self.element_equality_fields )
        self.assertEqual( len( result_corpus ), 2 )
        result_corpus.filter( lambda x: x.file_path ==\
                                  "./data/test/tei_xml/section.tei.v1.xml")
        self.assertEqual( len( result_corpus ), 1 )
    
    #def test_order(self):
    #    self.assertEqual( 2, 4)

    def test_output(self):
        file_paths = [ self.tei_data_path1, self.tei_data_path3 ]
        result_corpus = Corpus.create_from_files( file_paths, self.element_equality_fields )
        sssections_corpus = result_corpus.parse( TEIXMLGrammar.SUBSUBSECTION )

        attribute_names = [ CorpusElement.LABEL_PATH,\
                                CorpusElement.LANGUAGE_NAME_PATH,\
                                CorpusElement.TEXT ]
        results = sssections_corpus.output( attribute_names, tabulate=True )
        print "\n"
        print "\n".join(results)

class TestCorpusElement( unittest.TestCase ):

    tei_data_path1 = None
    tei_data_path2 = None

    ios_data_path1 = None
    ios_data_path2 = None
    ios_data_path3 = None

    tei_data1 = None
    tei_data2 = None

    ios_data1 = None
    ios_data2 = None
    ios_data3 = None

    def setUp(self):

        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')

        self.tei_data_path1 = config.get('xutools.test.test_corpus', 'TEIDataPath1')
        self.tei_data_path2 = config.get('xutools.test.test_corpus', 'TEIDataPath2')

        self.ios_data_path1 = config.get('xutools.test.test_corpus', 'IOSDataPath1')
        self.ios_data_path2 = config.get('xutools.test.test_corpus', 'IOSDataPath2')
        self.ios_data_path3 = config.get('xutools.test.test_corpus', 'IOSDataPath3')

    def test_create(self):
        #actual_possible_equality_fields = CorpusElement.get_field("possible_equality_fields"()
        #expected_possible_equality_fields = [ "idx_path", "label_path", "language_name_path", "text", "text_ranges", "file_path" ]
        #self.assertEqual( actual_possible_equality_fields, expected_possible_equality_fields )

        idx_path  = [ 5 ]  
        label_path  = [ "section.tei.v1.xml" ]
        language_name_path = [ BuiltinGrammar.FILE ]
        file_path = self.tei_data_path1
        element_equality_fields = [ CorpusElement.LABEL_PATH, CorpusElement.LANGUAGE_NAME_PATH ]
        corpus_element = CorpusElement.create(idx_path, label_path,\
                                                  language_name_path,\
                                                  file_path,\
                                                  element_equality_fields)

        self.assertEqual( len(corpus_element.get_idx_path()), 1 )
        self.assertEqual( corpus_element.get_idx_path(), idx_path )

        self.assertEqual( corpus_element.get_label_path(), label_path )
        self.assertEqual( corpus_element.get_language_name_path(), language_name_path )
        self.assertEqual( corpus_element.get_file_path(), file_path )
        self.assertEqual( corpus_element.get_text_ranges()[0][0], 0 )
        self.assertEqual( corpus_element.get_text_ranges()[0][1], 2763 )

    def test_eq(self):
        idx1_path = [ 5 ]
        label1_path = [ "1. Introduction" ]
        language_name1_path = [ TEIXMLGrammar.SECTION ]
        file_path1 = self.tei_data_path1
        element_equality_fields = [ CorpusElement.LABEL_PATH, CorpusElement.LANGUAGE_NAME_PATH ]
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_path1,\
                                                   element_equality_fields)
        
        idx2_path = [ 5 ]
        label2_path = [ "1. Introduction" ]
        language_name2_path = [ TEIXMLGrammar.SECTION ]
        file_path2 = self.tei_data_path2
        element_equality_fields = [ CorpusElement.LABEL_PATH, CorpusElement.LANGUAGE_NAME_PATH ]
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_path2,\
                                                   element_equality_fields)
        
        idx3_path = [ 5 ]
        label3_path = [ "1. Introduction" ]
        language_name3_path = [ TEIXMLGrammar.SECTION ]
        file_path3 = self.tei_data_path2
        element_equality_fields = [ CorpusElement.LABEL_PATH, CorpusElement.LANGUAGE_NAME_PATH ]
        corpus_element3 = CorpusElement.create(idx3_path, label3_path,\
                                                   language_name3_path,\
                                                   file_path3,\
                                                   element_equality_fields)
        self.assertNotEqual( corpus_element1, corpus_element2 )
        self.assertEqual( corpus_element2, corpus_element3 )

        # When we test equality, the equality fields of the compared elements
        #   should be the same (maybe intersection later on)
        element_equality_fields = [ CorpusElement.LABEL_PATH ]
        corpus_element3.set_field( CorpusElement.ELEMENT_EQUALITY_FIELDS, element_equality_fields )
        with self.assertRaises(RuntimeWarning):
            corpus_element3.__eq__(corpus_element2)
        with self.assertRaises(RuntimeWarning):
            corpus_element2.__eq__(corpus_element3)

        
        ## USE CASES

        #  M 1:  Think about basic interaction between multiple files and equality of
        #          corpus elements
        #
        #  M 1.1
        #   xupath = "/builtin:file/ios:interface"
        #   a.
        #     files = router.v1.example, router.v3.example (identical files)
        #   b. 
        #     files = router.v1.example, router.v2.example (different files)
        # -- M 1.1.a
        idx4_path = [ 4 ]
        label4_path = [ "router.v1.example", "Loopback0" ]
        language_name4_path = [ BuiltinGrammar.FILE, CiscoIOSGrammar.INTERFACE ]
        file_path4 = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        path_field_equality_components = None
        corpus_element4 = CorpusElement.create(idx4_path, label4_path,\
                                                   language_name4_path,\
                                                   file_path4,\
                                                   element_equality_fields)
        corpus_element4.set_field("text", "Loopback0 TEXT")
        
        idx5_path = [ 5 ]
        label5_path = [ "router.v3.example", "Loopback0" ]
        language_name5_path = [ BuiltinGrammar.FILE, CiscoIOSGrammar.INTERFACE ]
        file_path5 = self.ios_data_path3
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element5 = CorpusElement.create(idx5_path, label5_path,\
                                                   language_name5_path,\
                                                   file_path5,\
                                                   element_equality_fields)
        corpus_element5.set_field("text", "Loopback0 TEXT")
        self.assertNotEqual( corpus_element4, corpus_element5 )

        element_equality_fields = [ "language_name_path", "text" ]
        corpus_element4.set_field( "element_equality_fields", element_equality_fields )
        corpus_element5.set_field( "element_equality_fields", element_equality_fields )
        self.assertEqual( corpus_element4, corpus_element5 )

        # -- M 1.1.b
        idx4_path = [ 4 ]
        label4_path = [ "router.v1.example", "Loopback0" ]
        language_name4_path = [ BuiltinGrammar.FILE, CiscoIOSGrammar.INTERFACE ]
        file_path4 = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element4 = CorpusElement.create( idx4_path, label4_path,\
                                                    language_name4_path,\
                                                    file_path4,\
                                                    element_equality_fields )
        corpus_element4.set_field( "text", "Loopback0 TEXT v1" )

        idx5_path = [ 5 ]
        label5_path = [ "router.v2.example", "Loopback0" ]
        language_name5_path = [ BuiltinGrammar.FILE, CiscoIOSGrammar.INTERFACE ]
        file_path5 = self.ios_data_path2
        corpus_element5 = CorpusElement.create( idx5_path, label5_path,\
                                                    language_name5_path,\
                                                    file_path5,\
                                                    element_equality_fields )
        corpus_element5.set_field( "text", "Loopback0 TEXT v2" )
        self.assertNotEqual( corpus_element4, corpus_element5 )
        
        element_equality_fields = [ "language_name_path" ]
        corpus_element4.set_field( "element_equality_fields", element_equality_fields )
        corpus_element5.set_field( "element_equality_fields", element_equality_fields )
        self.assertEqual( corpus_element4, corpus_element5 )

        #  M 1.2
        #    xupath = "//ios:interface"
        #    a. 
        #      files = router.v1.example, router.v3.example (identical interfaces)
        #    b.
        #      files = router.v1.example, router.v2.example (different interfaces)
        # -- M 1.2.a
        idx4_path = [ 4 ]
        label4_path = [ "Loopback0" ]
        language_name4_path = [ CiscoIOSGrammar.INTERFACE ]
        file_path4 = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element4 = CorpusElement.create(idx4_path, label4_path,\
                                                   language_name4_path,\
                                                   file_path4,\
                                                   element_equality_fields)
        corpus_element4.set_field("text", "Loopback0 TEXT")
        
        idx5_path = [ 5 ]
        label5_path = [ "Loopback0" ]
        language_name5_path = [ CiscoIOSGrammar.INTERFACE ]
        file_path5 = self.ios_data_path3
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element5 = CorpusElement.create(idx5_path, label5_path,\
                                                   language_name5_path,\
                                                   file_path5,\
                                                   element_equality_fields)
        corpus_element5.set_field("text", "Loopback0 TEXT")
        self.assertEqual( corpus_element4, corpus_element5 )
        
        # -- M 1.2.b
        idx4_path = [ 4 ]
        label4_path = [ "Loopback0" ]
        language_name4_path = [ CiscoIOSGrammar.INTERFACE ]
        file_path4 = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element4 = CorpusElement.create(idx4_path, label4_path,\
                                                   language_name4_path,\
                                                   file_path4,\
                                                   element_equality_fields)
        corpus_element4.set_field("text", "Loopback0 TEXT v1")
        
        idx5_path = [ 5 ]
        label5_path = [ "Loopback0" ]
        language_name5_path = [ CiscoIOSGrammar.INTERFACE ]
        file_path5 = self.ios_data_path2
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element5 = CorpusElement.create(idx5_path, label5_path,\
                                                   language_name5_path,\
                                                   file_path5,\
                                                   element_equality_fields)
        corpus_element5.set_field("text", "Loopback0 TEXT v2")
        self.assertNotEqual( corpus_element4, corpus_element5 )

        # M 1.3
        #   xupath = "/builtin:file/ios:interface/builtin:line"
        #   a.
        #     files = router.v1.example, router.v3.example (identical lines and line numbers)
        #   b. 
        #     files = router.v1.example, router.v2.example (
        #     i.  identical lines and line nums (same as 1.3.a)
        #     ii. identical lines and difft line nums
        # -- M 1.3.a
        idx4_path = [ 4 ]   
        label4_path = [ "router.v1.example", "Loopback0", "1" ]
        language_name4_path = [ BuiltinGrammar.FILE, CiscoIOSGrammar.INTERFACE,\
                                    BuiltinGrammar.LINE ]
        file_path4 = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element4 = CorpusElement.create(idx4_path, label4_path,\
                                                   language_name4_path,\
                                                   file_path4,\
                                                   element_equality_fields)
        corpus_element4.set_field("text", "Loopback0 TEXT OF LINE 1")

        idx5_path = [ 5 ]
        label5_path = [ "router.v1.example", "Loopback0", "1" ]
        language_name5_path = [ BuiltinGrammar.FILE, CiscoIOSGrammar.INTERFACE,\
                                    BuiltinGrammar.LINE ]
        file_path5 = self.ios_data_path3
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element5 = CorpusElement.create(idx5_path, label5_path,\
                                                   language_name5_path,\
                                                   file_path5,\
                                                   element_equality_fields)
        corpus_element5.set_field("text", "Loopback0 TEXT OF LINE 1")
        self.assertEqual( corpus_element4, corpus_element5 )

        # -- M 1.3.b.ii
        idx4_path = [ 4 ]
        label4_path = [ "router.v1.example", "Loopback0", "1" ]
        language_name4_path = [ BuiltinGrammar.FILE, CiscoIOSGrammar.INTERFACE,\
                                    BuiltinGrammar.LINE ]
        file_path4 = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element4 = CorpusElement.create(idx4_path, label4_path,\
                                                   language_name4_path,\
                                                   file_path4,\
                                                   element_equality_fields)
        corpus_element4.set_field("text", "Loopback0 TEXT OF LINE")
        
        idx5_path = [ 5 ]
        label5_path = [ "router.v1.example", "Loopback0", "2" ]
        language_name5_path = [ BuiltinGrammar.FILE, CiscoIOSGrammar.INTERFACE,\
                                    BuiltinGrammar.LINE ]
        file_path5 = self.ios_data_path2
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element5 = CorpusElement.create(idx5_path, label5_path,\
                                                   language_name5_path,\
                                                   file_path5,\
                                                   element_equality_fields)
        corpus_element5.set_field("text", "Loopback0 TEXT OF LINE")
        self.assertEqual( corpus_element4.path_field_equality_components, None )        
        self.assertEqual( corpus_element5.path_field_equality_components, None )
        self.assertNotEqual( corpus_element4, corpus_element5)

        # TWIDDLE SOME BITS SO WE ARE LINE-NUMBER AGNOSTIC IN EQUALITY OF LABEL PATHS
        path_field_equality_components = { "label_path":[0,1] }
        path_field_equality_components_is_whitelist = True
        corpus_element4.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element4.set_field( "path_field_equality_components_is_whitelist",\
                                       path_field_equality_components_is_whitelist )
        corpus_element5.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element5.set_field( "path_field_equality_components_is_whitelist",\
                                       path_field_equality_components_is_whitelist )
        self.assertEqual( corpus_element4, corpus_element5)

        
        # M 1.4
        #   xupath = "//ios:interface/builtin:line"
        #   b.
        #      files = router.v1.example, router.v2.example
        #      i.  identical lines and line nums 
        #      ii. identical lines and different line nums
        # -- M 1.4.b.i
        idx4_path = [ 4 ]
        label4_path = [ "Loopback0", "1" ]
        language_name4_path = [ CiscoIOSGrammar.INTERFACE, BuiltinGrammar.LINE ]
        file_path4 = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element4 = CorpusElement.create(idx4_path, label4_path,\
                                                   language_name4_path,\
                                                   file_path4,\
                                                   element_equality_fields)
        corpus_element4.set_field("text", "Loopback0 TEXT OF LINE")

        idx5_path = [ 5 ]
        label5_path = [ "Loopback0", "1" ]
        language_name5_path = [ CiscoIOSGrammar.INTERFACE, BuiltinGrammar.LINE ]
        file_path5 = self.ios_data_path2
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element5 = CorpusElement.create(idx5_path, label5_path,\
                                                   language_name5_path,\
                                                   file_path5,\
                                                   element_equality_fields)
        corpus_element5.set_field("text", "Loopback0 TEXT OF LINE")
        self.assertEqual( corpus_element4, corpus_element5 )

        # -- M 1.4.b.ii
        idx4_path = [ 4 ]
        label4_path = [ "Loopback0", "1" ]
        language_name4_path = [ CiscoIOSGrammar.INTERFACE, BuiltinGrammar.LINE ]
        file_path4 = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element4 = CorpusElement.create(idx4_path, label4_path,\
                                                   language_name4_path,\
                                                   file_path4,\
                                                   element_equality_fields)
        corpus_element4.set_field("text", "Loopback0 TEXT OF LINE")

        idx5_path = [ 5 ]
        label5_path = [ "Loopback0", "2" ]
        language_name5_path = [ CiscoIOSGrammar.INTERFACE, BuiltinGrammar.LINE ]
        file_path5 = self.ios_data_path2
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element5 = CorpusElement.create(idx5_path, label5_path,\
                                                   language_name5_path,\
                                                   file_path5,\
                                                   element_equality_fields)
        corpus_element5.set_field("text", "Loopback0 TEXT OF LINE")
        self.assertNotEqual( corpus_element4, corpus_element5 )
        
        # TWIDDLE SOME BITS SO WE ARE LINE-NUMBER AGNOSTIC IN EQUALITY OF LABEL PATHS
        path_field_equality_components = { "label_path":[0] }
        path_field_equality_components_is_whitelist = True
        corpus_element4.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element4.set_field( "path_field_equality_components_is_whitelist",
                                   path_field_equality_components_is_whitelist )
        corpus_element5.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element5.set_field( "path_field_equality_components_is_whitelist",
                                   path_field_equality_components_is_whitelist )
        self.assertEqual( corpus_element4, corpus_element5 )

        # M 1.5
        #   xupath = "/builtin:file/ios:interface/builtin:line[ access-group ]"
        #   b.  
        #      files = router.v1.example, router.v2.example
        #      i.   identical lines and line numbers
        #      ii.  identical lines and different line numbers
        #   THIS CASE IS THE SAME AS M 1.3 EXCEPT WE APPLY A PREDICATE TO LINES
        #     FOR NOW, NO NEED TO WRITE TEST UNTIL CODE FAILS SINCE SUBCASE OF 1.3
        
        # M 1.6
        #   xupath = "/ios:interface/builtin:file[ access-group ]"
        #   b.
        #     files = router.v1.example, router.v2.example
        #     i.  identical lines and line nums
        #     ii. identical lines and different line nums
        #   THIS CASE IS THE SAME AS M 1.4 EXCEPT WE APPLY A PREDICATE TO LINES
        #    FOR NOW, NO NEED TO WRITE TEST UNTIL CODE FAILS SINCE SUBCASE OF 1.4
        

        # M 2:  Think about interaction between filepaths, directories, and 
        #         element equality
        #
        #   M 2.1 xupath = "/builtin:dir",
        #   
        #   i.    identical dir path name, identical dir content    (EQUAL)
        #   ii.   identical dir path name, different dir content    (IMPOSSIBLE CASE)
        #   iii.  different dir path name, identical dir content    
        #         a.  (NOT EQUAL at first)
        #         b.  (EQUAL when not use dir path name to evaluate)
        #   iv.   different dir path, different dir content         (NOT EQUAL)
        # -- M 2.1.i
        idx1_path = [ 4 ] 
        label1_path = [ "/home/user3" ]
        language_name1_path = [ BuiltinGrammar.DIRECTORY ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "DIRECTORY CONTENTS")
        
        idx2_path = [ 4 ]
        label2_path = [ "/home/user3" ]
        language_name2_path = [ BuiltinGrammar.DIRECTORY ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "DIRECTORY CONTENTS")
        self.assertEqual( corpus_element1, corpus_element2 )
        
        # -- M 2.1.ii IMPOSSIBLE CASE
        # -- M 2.1.iii.a
        idx1_path = [ 4 ]
        label1_path = [ "/home/user1" ]
        language_name1_path = [ BuiltinGrammar.DIRECTORY ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "DIRECTORY CONTENTS")

        idx2_path = [ 4 ]
        label2_path = [ "/home/user2/configs" ]
        language_name2_path = [ BuiltinGrammar.DIRECTORY ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "DIRECTORY CONTENTS")
        self.assertNotEqual( corpus_element1, corpus_element2 )

        # -- M 2.1.iii.b
        #  since the label field path is one entry long, we simply
        #  remove the label field path from the element equality fields.
        element_equality_fields = [ "language_name_path", "text" ]
        corpus_element1.set_field( "element_equality_fields", element_equality_fields )
        corpus_element2.set_field( "element_equality_fields", element_equality_fields )
        self.assertEqual( corpus_element1, corpus_element2 )

        # -- M 2.1.iv
        idx1_path = [ 4 ]
        label1_path = [ "/home/user1" ]
        language_name1_path = [ BuiltinGrammar.DIRECTORY ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "DIRECTORY CONTENTS V1 V2")
        
        idx2_path = [ 4 ]
        label2_path = [ "/home/user3" ]
        language_name2_path = [ BuiltinGrammar.DIRECTORY ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "DIRECTORY CONTENTS V1 V2 V3")
        self.assertNotEqual( corpus_element1, corpus_element2 )

        #
        #   M 2.2 xupath = "/builtin:file",
        #   
        #   i.    identical file name, identical file content  (EQUAL)
        #   ii.   identical file name, different file content  
        #         a.  NOT EQUAL at first
        #         b.  EQUAL when eliminate "text" as an element equality field
        #   iii.  different file name, identical file content  
        #         a.  (NOT EQUAL at first)
        #         b.  (EQUAL when eliminate "label_path" as an element equality field
        #   iv.   different file name, different file content  (NOT EQUAL)
        #
        # -- M 2.2.i
        idx1_path = [ 4 ]
        label1_path = [ "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.FILE ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS")
        
        idx2_path = [ 4 ]
        label2_path = [ "router.v1.config" ]
        language_name2_path = [ BuiltinGrammar.FILE ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS")
        self.assertEqual(corpus_element1, corpus_element2)

        # -- M 2.2.ii.a
        idx1_path = [ 4 ]
        label1_path = [ "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.FILE ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS v1")

        idx2_path = [ 5 ]
        label2_path = [ "router.v1.config" ]
        language_name2_path = [ BuiltinGrammar.FILE ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS v1*")
        self.assertNotEqual(corpus_element1, corpus_element2)
        
        # -- M 2.2.ii.b
        element_equality_fields = [ "label_path", "language_name_path" ]
        corpus_element1.set_field("element_equality_fields", element_equality_fields)
        corpus_element2.set_field("element_equality_fields", element_equality_fields)

        # -- M 2.2.iii.a
        idx1_path = [ 4 ]
        label1_path = [ "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.FILE ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS")

        idx2_path = [ 5 ]
        label2_path = [ "router.v2.config" ]
        language_name2_path = [ BuiltinGrammar.FILE ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS")
        self.assertNotEqual( corpus_element1, corpus_element2 )

        # -- M 2.2.iii.b
        element_equality_fields = [ "language_name_path", "text" ]
        corpus_element1.set_field("element_equality_fields", element_equality_fields)
        corpus_element2.set_field("element_equality_fields", element_equality_fields)
        self.assertEqual( corpus_element1, corpus_element2 )
        
        # -- M 2.2.iv
        idx1_path = [ 4 ]
        label1_path = [ "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.FILE ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS v1")
        
        idx2_path = [ 5 ]
        label2_path = [ "router.v2.config" ]
        language_name2_path = [ BuiltinGrammar.FILE ]
        file_path = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_path,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS v2")
        self.assertNotEqual( corpus_element1, corpus_element2 )

        #
        #   M 2.3 xupath = "/builtin:dir/builtin:file",  (fspath as dirpath)
        #
        #   i.    identical dir path name, identical file name, identical file content  (EQUAL)
        #   ii.   identical dir path name, identical file name, different file content  (IMPOSSIBLE)
        #         a. NOT EQUAL at first
        #         b. EQUAL when eliminate "text" as an element equality field
        #   iii.  identical dir path name, different file name, identical file content
        #         a.  NOT EQUAL
        #         b.  EQUAL when override path_field_equality components on file name
        #             BUT file only has one component so CASE NOT APPLY
        #   iv.   identical dir path name, different file name, different file content  
        #         a.  NOT EQUAL
        #         b.  EQUAL when remove "text" from equality elements and file name from the
        #                 path field equality components but then just "builtin:dir"
        #   v.    different dir path name, identical file name, identical file content  (EQUAL)
        #         a.  NOT EQUAL
        #         b.  EQUAL when override path_field_equality components on dir path name
        #   vi.   different dir path name, identical file name, different file content  
        #         a.  NOT EQUAL
        #         b.  EQUAL when override path_field_equality components on dir path name and
        #                remove "text" from equality components but then just a pointer comparison on "builtin:file"
        #   vii.  different dir path name, different file name, identical file content
        #         a.  NOT EQUAL
        #         b.  EQUAL when override path field equality components on dir path name, file name,
        #                equivalent to a content comparison on "builtin:file"
        #   viii. different dir path name, different file name, different file content  (NOT EQUAL)
        #
        # -- M 2.3.i
        idx1_path = [ 4 ]
        label1_path = [ "/home/user1", "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS")
        
        idx2_path = [ 5 ]
        label2_path = [ "/home/user1", "router.v1.config" ]
        language_name2_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS")
        self.assertEqual( corpus_element1, corpus_element2 )
        
        # -- M 2.3.ii.a
        idx1_path = [ 4 ]
        label1_path = [ "/home/user1", "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS")
        
        idx2_path = [ 5 ]
        label2_path = [ "/home/user1", "router.v1.config" ]
        language_name2_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS DIFFERENT")
        self.assertNotEqual( corpus_element1, corpus_element2 )
        
        # -- M 2.3.ii.b
        element_equality_fields = [ "label_path", "language_name_path" ]
        corpus_element1.set_field("element_equality_fields", element_equality_fields)
        corpus_element2.set_field("element_equality_fields", element_equality_fields)
        self.assertEqual( corpus_element1, corpus_element2 )

        # -- M 2.3.iii.a
        idx1_path = [ 4 ]
        label1_path = [ "/home/user1", "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS")
        
        idx2_path = [ 5 ]
        label2_path = [ "/home/user1", "router.v2.config" ]
        language_name2_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS")
        self.assertNotEqual( corpus_element1, corpus_element2 )
        
        # -- M 2.3.iii.b
        path_field_equality_components = { "label_path":[0] }
        path_field_equality_components_is_whitelist = True
        corpus_element1.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element1.set_field( "path_field_equality_components_is_whitelist",\
                                       path_field_equality_components_is_whitelist )
        corpus_element2.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element2.set_field( "path_field_equality_components_is_whitelist",\
                                       path_field_equality_components_is_whitelist )
        self.assertEqual( corpus_element1, corpus_element2 )

        # -- M 2.3.iv.a
        idx1_path = [ 4 ]
        label1_path = [ "/home/user1", "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS")
        
        idx2_path = [ 5 ]
        label2_path = [ "/home/user1", "router.v2.config" ]
        language_name2_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS DIFFERENT")
        self.assertNotEqual( corpus_element1, corpus_element2 )
        
        # -- M 2.3.iv.b
        element_equality_fields = [ "label_path", "language_name_path" ]
        path_field_equality_components = { "label_path":[0] }
        path_field_equality_components_is_whitelist = True
        corpus_element1.set_field( "element_equality_fields", element_equality_fields )
        corpus_element1.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element1.set_field( "path_field_equality_components_is_whitelist",\
                                       path_field_equality_components_is_whitelist )
        corpus_element2.set_field( "element_equality_fields", element_equality_fields )
        corpus_element2.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element2.set_field( "path_field_equality_components_is_whitelist",\
                                       path_field_equality_components_is_whitelist )
        self.assertEqual( corpus_element1, corpus_element2 )

        # -- M 2.3.v.a
        idx1_path = [ 4 ]
        label1_path = [ "/home/user1", "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS")
        
        idx2_path = [ 5 ]
        label2_path = [ "/home/user2/configs", "router.v1.config" ]
        language_name2_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS")
        self.assertNotEqual( corpus_element1, corpus_element2 )
        
        # -- M 2.3.v.b
        path_field_equality_components = { "label_path":[1] }
        path_field_equality_components_is_whitelist = True
        corpus_element1.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element1.set_field( "path_field_equality_components_is_whitelist",\
                                       path_field_equality_components_is_whitelist )
        corpus_element2.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element2.set_field( "path_field_equality_components_is_whitelist",\
                                       path_field_equality_components_is_whitelist )
        self.assertEqual( corpus_element1, corpus_element2 )

        # -- M 2.3.vi.a
        idx1_path = [ 4 ]
        label1_path = [ "/home/user1", "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS V1")
        
        idx2_path = [ 5 ]
        label2_path = [ "/home/user4", "router.v1.config" ]
        language_name2_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS V1*")
        self.assertNotEqual( corpus_element1, corpus_element2 )
        
        # -- M 2.3.vi.b
        element_equality_fields = [ "label_path", "language_name_path" ]
        path_field_equality_components = { "label_path":[1] }
        path_field_equality_components_is_whitelist = True

        corpus_element1.set_field( "element_equality_fields", element_equality_fields )
        corpus_element1.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element1.set_field( "path_field_equality_components_is_whitelist",\
                                       path_field_equality_components_is_whitelist )
        corpus_element2.set_field( "element_equality_fields", element_equality_fields )
        corpus_element2.set_field( "path_field_equality_components",\
                                       path_field_equality_components )
        corpus_element2.set_field( "path_field_equality_components_is_whitelist",\
                                       path_field_equality_components_is_whitelist )
        self.assertEqual( corpus_element1, corpus_element2 )

        # -- M 2.3.vii.a
        idx1_path = [ 4 ]
        label1_path = [ "/home/user3", "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS")
        
        idx2_path = [ 5 ]
        label2_path = [ "/home/user4", "router.v2.config" ]
        language_name2_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS")
        self.assertNotEqual( corpus_element1, corpus_element2 )
        
        # -- M 2.3.vii.b
        element_equality_fields = [ "language_name_path", "text" ]
        corpus_element1.set_field( "element_equality_fields", element_equality_fields )
        corpus_element2.set_field( "element_equality_fields", element_equality_fields )
        self.assertEqual( corpus_element1, corpus_element2 )

        # -- M 2.3.viii
        idx1_path = [ 4 ]
        label1_path = [ "/home/user1", "router.v1.config" ]
        language_name1_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element1 = CorpusElement.create(idx1_path, label1_path,\
                                                   language_name1_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element1.set_field("text", "FILE CONTENTS V1")
        
        idx2_path = [ 5 ]
        label2_path = [ "/home/user2/configs", "router.v2.config" ]
        language_name2_path = [ BuiltinGrammar.DIRECTORY, BuiltinGrammar.FILE ]
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        file_name = self.ios_data_path1
        corpus_element2 = CorpusElement.create(idx2_path, label2_path,\
                                                   language_name2_path,\
                                                   file_name,\
                                                   element_equality_fields)
        corpus_element2.set_field("text", "FILE CONTENTS V2")
        self.assertNotEqual( corpus_element1, corpus_element2 )
        

        idx6_path = [ 6 ]
        label6_path = [ "router.v1.example" ]
        language_name6_path = [ BuiltinGrammar.FILE ]
        file_path6 = self.ios_data_path1
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element6 = CorpusElement.create(idx6_path, label6_path,\
                                                   language_name6_path,\
                                                   file_path6,\
                                                   element_equality_fields)
        corpus_element6.set_field("text", "CONTENTS OF FILE")
        
        idx7_path = [ 7 ]
        label7_path = [ "router.v3.example" ]
        language_name7_path = [ BuiltinGrammar.FILE ]
        file_path7 = self.ios_data_path3
        element_equality_fields = [ "label_path", "language_name_path", "text" ]
        corpus_element7 = CorpusElement.create(idx7_path, label7_path,\
                                                   language_name7_path,\
                                                   file_path7,\
                                                   element_equality_fields)
        corpus_element7.set_field("text", "CONTENTS OF FILE")
        self.assertNotEqual( corpus_element6, corpus_element7 )
        
        element_equality_fields = [ "language_name_path", "text" ]
        corpus_element6.set_field( "element_equality_fields", element_equality_fields )
        corpus_element7.set_field( "element_equality_fields", element_equality_fields )
        self.assertEqual( corpus_element6, corpus_element7 )


        # Also, we want to add in directories
        # Lets think of examples with a full on directory                                             
        # Lets also think of examples with our CSVFiles


    def test_parse_tei(self):

        # Now create the corpus element with an index
        idx_path = [ 1 ]
        file_path = self.tei_data_path1   
        basename = os.path.basename(file_path)
        label_path = [ basename ]
        language_name_path = [ BuiltinGrammar.FILE ]
        element_equality_fields = [ CorpusElement.LABEL_PATH, CorpusElement.LANGUAGE_NAME_PATH, CorpusElement.TEXT ]
        corpus_element = CorpusElement.create(idx_path, label_path, language_name_path, file_path, element_equality_fields )

        # Parse the Sections from the Security Policy File (FILE)
        section_elements = corpus_element.parse( TEIXMLGrammar.SECTION )
        self.assertEqual( len(section_elements), 2 )
        section_elements_list = list(section_elements)
        section_elements_list.sort(key=attrgetter('label_path'))

        section1_element = section_elements_list[0]
        #self.assertEqual( len(section1_element.get_idx_path()), 2 )
        self.assertEqual( section1_element.get_label_path(), [ "section.tei.v1.xml", "1 INTRODUCTION" ] )
        self.assertEqual( section1_element.get_language_name_path(), [ BuiltinGrammar.FILE, TEIXMLGrammar.SECTION ] )
        self.assertEqual( section1_element.get_file_path(), self.tei_data_path1 )
        self.assertEqual( section1_element.get_text_ranges()[0], [0, 2763] )
        self.assertEqual( section1_element.get_text_ranges()[1], [364, 2502] )

        section9_element = section_elements_list[1]
        self.assertEqual( len(section9_element.get_idx_path()), 2 )
        self.assertEqual( section9_element.get_label_path(), [ "section.tei.v1.xml", "9. Glossary" ] )
        self.assertEqual( section9_element.get_language_name_path(), [ BuiltinGrammar.FILE, TEIXMLGrammar.SECTION ] )
        self.assertEqual( section9_element.get_file_path(), self.tei_data_path1 )
        self.assertEqual( section9_element.get_text_ranges()[0], [0, 2763] )
        self.assertEqual( section9_element.get_text_ranges()[1], [2509, 2740] )

        # Parse the Subsections from the Security Policy File 
        ssection_elements = corpus_element.parse( TEIXMLGrammar.SUBSECTION )
        self.assertEqual( len(ssection_elements), 1 )
        ssection1_element = list(ssection_elements)[0]
        self.assertEqual( len(ssection1_element.get_idx_path()), 2 )
        self.assertEqual( ssection1_element.get_label_path(), [ "section.tei.v1.xml", "1.1 OverView"] )
        self.assertEqual( ssection1_element.get_language_name_path(), [ BuiltinGrammar.FILE, TEIXMLGrammar.SUBSECTION ] )
        self.assertEqual( ssection1_element.get_file_path(), self.tei_data_path1 )
        self.assertEqual( ssection1_element.get_text_ranges()[0], [0, 2763] )
        self.assertEqual( ssection1_element.get_text_ranges()[1], [947, 2489] )

        # Parse the Subsections from the Sections
        # -- section1
        ssection_elements = section1_element.parse( TEIXMLGrammar.SUBSECTION )
        self.assertEqual( len(ssection_elements), 1 )
        ssection1_element = list(ssection_elements)[0]
        self.assertEqual( len(ssection1_element.get_idx_path()), 3 )
        self.assertEqual( ssection1_element.get_label_path(), [ "section.tei.v1.xml", "1 INTRODUCTION", "1.1 OverView" ] )
        self.assertEqual( ssection1_element.get_language_name_path(), [ BuiltinGrammar.FILE, TEIXMLGrammar.SECTION, TEIXMLGrammar.SUBSECTION ] )
        self.assertEqual( ssection1_element.get_file_path(), self.tei_data_path1 )
        self.assertEqual( ssection1_element.get_text_ranges()[0], [0, 2763] )
        self.assertEqual( ssection1_element.get_text_ranges()[1], [364, 2502] )
        self.assertEqual( ssection1_element.get_text_ranges()[2], [583, 2125] )

        # -- section9
        ssection_elements = section9_element.parse( TEIXMLGrammar.SUBSECTION )
        self.assertEqual( len(ssection_elements), 0 )

        # Parse the subsubsections from the file
        sssection_elements = corpus_element.parse( TEIXMLGrammar.SUBSUBSECTION )
        self.assertEqual( len(sssection_elements), 2 )
        sssection_elements_list = list(sssection_elements)
        sssection_elements_list.sort(key=attrgetter('label_path'))

        sssection1_element = sssection_elements_list[0]
        self.assertEqual( len(sssection1_element.get_idx_path()), 2 )
        self.assertEqual( sssection1_element.get_label_path(), ["section.tei.v1.xml", "1.1.1 Type of Certifiacates"] )
        self.assertEqual( sssection1_element.get_language_name_path(), [ BuiltinGrammar.FILE, TEIXMLGrammar.SUBSUBSECTION ] )
        self.assertEqual( sssection1_element.get_file_path(), self.tei_data_path1 )
        self.assertEqual( sssection1_element.get_text_ranges()[0], [0, 2763] )
        self.assertEqual( sssection1_element.get_text_ranges()[1], [1682, 2085] )

        sssection2_element = sssection_elements_list[1]
        self.assertEqual( len(sssection2_element.get_idx_path()), 2 )
        self.assertEqual( sssection2_element.get_label_path(), ["section.tei.v1.xml", "1.1.2 Related specification"] )
        self.assertEqual( sssection2_element.get_language_name_path(), [ BuiltinGrammar.FILE, TEIXMLGrammar.SUBSUBSECTION ] )
        self.assertEqual( sssection2_element.get_file_path(), self.tei_data_path1 )
        self.assertEqual( sssection2_element.get_text_ranges()[0], [0, 2763] )
        self.assertEqual( sssection2_element.get_text_ranges()[1], [2096, 2474] )

        # Parse the subsubsections from the sections
        # -- section1
        sssection_elements = section1_element.parse( TEIXMLGrammar.SUBSUBSECTION )
        self.assertEqual( len(sssection_elements), 2 )
        sssection_elements_list = list(sssection_elements)
        sssection_elements_list.sort(key=attrgetter('label_path'))

        # --- these may differ depending upon the ordering (we need to write an order method)
        sssection1_element = sssection_elements_list[0]
        self.assertEqual( len(sssection1_element.get_idx_path()), 3 )
        self.assertEqual( sssection1_element.get_label_path(), ["section.tei.v1.xml", "1 INTRODUCTION", "1.1.1 Type of Certifiacates"] )
        self.assertEqual( sssection1_element.get_language_name_path(), [ BuiltinGrammar.FILE, TEIXMLGrammar.SECTION, TEIXMLGrammar.SUBSUBSECTION ] )
        self.assertEqual( sssection1_element.get_file_path(), self.tei_data_path1 )
        self.assertEqual( sssection1_element.get_text_ranges()[0], [0, 2763] )
        self.assertEqual( sssection1_element.get_text_ranges()[1], [364, 2502] )

        # -- section9
        sssection_elements = section9_element.parse( TEIXMLGrammar.SUBSUBSECTION )
        self.assertEqual( len(sssection_elements), 0 )

        # Parse the subsubsections from the subsections
        sssection_elements = ssection1_element.parse( TEIXMLGrammar.SUBSUBSECTION )
        self.assertEqual( len(sssection_elements), 2 )
        sssection_elements_list = list(sssection_elements)
        sssection_elements_list.sort(key=attrgetter('label_path'))

        sssection1_element = sssection_elements_list[0]
        self.assertEqual( len(sssection1_element.get_idx_path()), 4)
        self.assertEqual( sssection1_element.get_label_path(), ["section.tei.v1.xml", "1 INTRODUCTION", "1.1 OverView", "1.1.1 Type of Certifiacates"] )
        self.assertEqual( sssection1_element.get_language_name_path(), [ BuiltinGrammar.FILE, TEIXMLGrammar.SECTION, TEIXMLGrammar.SUBSECTION, TEIXMLGrammar.SUBSUBSECTION ] )
        self.assertEqual( sssection1_element.get_file_path(), self.tei_data_path1 )
        self.assertEqual( sssection1_element.get_text_ranges()[0], [0, 2763] )
        self.assertEqual( sssection1_element.get_text_ranges()[1], [364, 2502] )

    def test_parse_ios(self):
        
        idx_path = [ 1 ]
        file_path = self.ios_data_path1
        basename = os.path.basename(file_path)
        label_path = [ basename ]
        language_name_path = [ BuiltinGrammar.FILE ]
        element_equality_fields = [ CorpusElement.LABEL_PATH, CorpusElement.LANGUAGE_NAME_PATH, CorpusElement.TEXT ]
        corpus_element = CorpusElement.create(idx_path, label_path, language_name_path, file_path, element_equality_fields)

        # Parse the interfaces from the Security Policy File (FILE)
        interface_elements = corpus_element.parse( CiscoIOSGrammar.INTERFACE )
        self.assertEqual( len(interface_elements), 2 )
        
        interface_elements_list = list(interface_elements)
        interface_elements_list.sort(key=attrgetter('label_path'))

        interface_element1 = interface_elements_list[1]
        self.assertEqual( interface_element1.get_label_path(), ["router.v1.example", "Loopback0"] )
        self.assertEqual( interface_element1.get_language_name_path(), [BuiltinGrammar.FILE, CiscoIOSGrammar.INTERFACE ] )
        self.assertEqual( interface_element1.get_file_path(), self.ios_data_path1 )
        self.assertEqual( interface_element1.get_text_ranges()[0], [0, 419] )
        self.assertEqual( interface_element1.get_text_ranges()[1], [0, 187] )

        interface_element2 = interface_elements_list[0]
        self.assertEqual( interface_element2.get_label_path(), ["router.v1.example", "GigabitEthernet4/2"])
        self.assertEqual( interface_element2.get_language_name_path(), [BuiltinGrammar.FILE, CiscoIOSGrammar.INTERFACE ] )
        self.assertEqual( interface_element2.get_file_path(), self.ios_data_path1 )
        self.assertEqual( interface_element2.get_text_ranges()[0], [0, 419] )
        self.assertEqual( interface_element2.get_text_ranges()[1], [187, 420] )


class TestCSVCorpusElement( unittest.TestCase ):
    
    csv_data_path1 = None
    csv_data1 = None

    def setUp(self):
        
        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')
        
        self.csv_data_path1 = config.get('xutools.test.test_csv_corpus', 'CSVDataPath1' )

    def test_parse(self):
        idx_path = [ None ]
        label_path = [ "CSV File" ]
        language_name_path = [ BuiltinGrammar.FILE ]
        file_path = self.csv_data_path1

        # 1: 10.1.24.117 (fw1), any/tcp, 10.101.107.13 (10.101.107.13), 1522/tcp
        # 2: 10.1.24.117 (fw1), any/tcp, 10.101.107.13 (10.101.107.13), 8003/tcp
        # 3: 10.1.24.117 (fw1), any/tcp, 10.101.107.13 (10.101.107.13), 21/tcp
        # 4: 10.1.24.117 (fw1), any/tcp, 10.101.107.13 (10.101.107.13), 1521/tcp
        # 5: 10.1.24.117 (fw1), any/tcp, 10.101.107.13 (10.101.107.13), 5000-5050/tcp
        # 6: 10.1.24.118 (PACS-FW), any/tcp, 10.101.107.13 (10.101.107.13), 1522/tcp
        # 7: 10.1.24.118 (PACS-FW), any/tcp, 10.101.107.13 (10.101.107.13), 8003/tcp
        # 8: 10.1.24.118 (PACS-FW), any/tcp, 10.101.107.13 (10.101.107.13), 21/tcp
        # 9: 10.1.24.118 (PACS-FW), any/tcp, 10.101.107.13 (10.101.107.13), 1521/tcp
        # 10:10.1.24.118 (PACS-FW), any/tcp, 10.101.107.13 (10.101.107.13), 5000-5050/tcp

        field_names = [ "path", "src_firewall", "src_node", "src_port", "src_group", "dest_fw", "dest_node", "dest_port", "dest_group", "service", "note", "rules", "policies" ]
        eq_hash_fields = [ "src_node" ]
        csv_corpus_element = CSVCorpusElement.create( idx_path, label_path, language_name_path, file_path)
        csv_corpus_element.set_field_names( field_names )
        csv_corpus_element.set_eq_hash_fields( eq_hash_fields )
        csv_row_corpus_elements = csv_corpus_element.parse( CSVGrammar.ROW )
        # There are only 2 firewalls, so we're going to just see two representative elements here
        self.assertEqual( len(csv_row_corpus_elements), 2 )

        eq_hash_fields = [ "src_node", "src_port", "dest_node", "dest_port" ]
        csv_corpus_element.set_eq_hash_fields( eq_hash_fields )
        csv_row_corpus_elements = csv_corpus_element.parse( CSVGrammar.ROW )
        self.assertEqual( len(csv_row_corpus_elements), 10 )
        
        eq_hash_fields = [ "dest_node" ]
        csv_corpus_element.set_eq_hash_fields( eq_hash_fields )
        csv_row_corpus_elements = csv_corpus_element.parse( CSVGrammar.ROW )
        self.assertEqual( len(csv_row_corpus_elements), 1 )

        eq_hash_fields = [ "dest_port" ]
        csv_corpus_element.set_eq_hash_fields( eq_hash_fields )
        csv_row_corpus_elements = csv_corpus_element.parse( CSVGrammar.ROW )
        self.assertEqual( len(csv_row_corpus_elements), 5 )

        
