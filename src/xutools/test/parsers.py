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
import ConfigParser
from pyparsing import *
from xutools.parsers import CiscoIOSParser, TEILiteParser, NVDParser, SubsetCParser, XPathParser
import unittest

## @package test
#    This module contains methods to test our XUTools parsers


## Test the Cisco IOS Grammar
#  We want to be more careful to think about the kinds of bugs and
#   exceptions that this utility may throw when it computes a result
#   set.
class TestCiscoIOSParser(unittest.TestCase):

    ios_data_path1 = None
    ios_data_path2 = None

    ios_data1 = None
    ios_data2 = None

    ## Method run prior to every test
    def setUp(self):
        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')

        self.ios_data_path1 = config.get('xutools.test.test_tools', 'IOSDataPath1')
        self.ios_data_path2 = config.get('xutools.test.test_tools', 'IOSDataPath2')
        self.ios_data_path3 = config.get('xutools.test.test_tools', 'IOSDataPath3')

        fp = open(self.ios_data_path1, 'r')
        self.ios_data1 = fp.read()
        fp.close()

        fp = open(self.ios_data_path2, 'r')
        self.ios_data2 = fp.read()
        fp.close()

    def preorder_tree_walk(self, parse_tree, indent):
        print indent + ' '.join(parse_tree.content).strip()
        for child in parse_tree.children:
            self.preorder_tree_walk(child, indent + " ")

    def test_get_region_id(self):
        # Write Cisco IOS tests for interface, and line
        parser = CiscoIOSParser()

        line_nos = range(1, 45)
        line_nos = map(str, line_nos)
        expected_ids = {'line': line_nos,
                         'interface': ['Loopback0', 'GigabitEthernet4/2']}

        for region_type in expected_ids.keys():
            production = parser.getGrammarForUnit(region_type)

            match_forest = production.scanString(self.ios_data1)
            ids = []
            subtree_idx = 0
            for subtree, s, e in match_forest:
                new_id = parser.getRegionID(subtree, region_type, subtree_idx)
                ids.append(new_id)
                subtree_idx = subtree_idx + 1

            i = 0
            for id in ids:
                self.assertEqual(id, expected_ids[region_type][i])
                i = i + 1

    def test_normalize_parse_tree(self):
        num_matches = 0
        for parse_tree, s, e in CiscoIOSParser.lineRegion.scanString(self.ios_data1):
            num_matches = num_matches + 1
            #pprint.pprint(parse_tree.asList())
            nparse_tree = CiscoIOSParser.normalizeParseTree(parse_tree.asList())
            #pprint.pprint(nparse_tree)
        self.assertEqual(num_matches, 16)

        num_matches = 0
        for parse_tree, s, e in CiscoIOSParser.indentedLineRegion.scanString(self.ios_data1):
            num_matches = num_matches + 1
            #pprint.pprint(parse_tree.asList())
            nparse_tree = CiscoIOSParser.normalizeParseTree(parse_tree.asList())
            #pprint.pprint(nparse_tree)
        self.assertEqual(num_matches, 12)

        num_matches = 0
        for parse_tree, s, e in CiscoIOSParser.interfaceRegion.scanString(self.ios_data1):
            num_matches = num_matches + 1
            nparse_tree = CiscoIOSParser.normalizeParseTree(parse_tree.asList())
            #pprint.pprint(parse_tree.asList())
            #pprint.pprint(nparse_tree)
            self.assertTrue(nparse_tree['type'] == 'interface')
            self.assertTrue(nparse_tree['id'] != None)
        self.assertEqual(num_matches, 2)

        num_matches = 0
        for parse_tree, s, e in CiscoIOSParser.cryptoRegion.scanString(self.ios_data1):
            num_matches = num_matches + 1
            #pprint.pprint(parse_tree.asList())
            nparse_tree = CiscoIOSParser.normalizeParseTree(parse_tree.asList())
            #pprint.pprint(nparse_tree)
            self.assertTrue(nparse_tree['type'] == 'crypto')
            self.assertTrue(nparse_tree['id'] != None)
        self.assertEqual(num_matches, 0)

        num_matches = 0
        for parse_tree, s, e in CiscoIOSParser.configFileRegion.scanString(self.ios_data1):
            num_matches = num_matches + 1
            #pprint.pprint(parse_tree.asList())
            nparse_tree = CiscoIOSParser.normalizeParseTree(parse_tree.asList())
            #pprint.pprint(nparse_tree)
            self.assertTrue(nparse_tree['type'] == None)
            self.assertTrue(nparse_tree['id'] == None)
        self.assertEqual(num_matches, 1)

    def test_parse_line(self):
        parser = CiscoIOSParser()
        text_tree = "interface GigabitEthernet4/2\n description Campus Core Network\n ip address 129.170.2.195 255.255.255.240\n ip access-group from_campus_filter2 in\n ip access-group to_campus_filter2 out\n no ip redirects\n no ip unreachables\n no ip proxy-arp\n ip flow ingress\n ip pim sparse-dense-mode\n ip policy route-map nat-private\n ip sap listen\n load-interval 30\n wrr-queue cos-map 1 2 2 \n wrr-queue cos-map 2 1 3 4 6 \n mls qos trust dscp\n hold-queue 4096 in\n!"
        match_forest = originalTextFor(parser.lineRegion).scanString(text_tree)
        new_result_forest = []
        for tree, s, e in match_forest:
            new_result_forest.append(tree[0].strip())
        self.assertEqual(len(new_result_forest), 18)

    def test_parse_interface(self):
        num_matches = 0
        for tokens, s, e in CiscoIOSParser.interfaceStart.scanString(self.ios_data1):
            num_matches = num_matches + 1
        #            print tokens
        self.assertEqual(num_matches, 2)

        num_matches = 0
        for tokens, s, e in CiscoIOSParser.blockEnd.scanString(self.ios_data1):
            num_matches = num_matches + 1
        #            print tokens
        self.assertEqual(num_matches, 2)

        num_matches = 0
        for tokens, s, e in CiscoIOSParser.interfaceRegion.scanString(self.ios_data1):
            num_matches = num_matches + 1
            #print tokens
        self.assertEqual(num_matches, 2)

        num_matches = 0
        for tokens, s, e in CiscoIOSParser.configFileRegion.scanString(self.ios_data1):
            num_matches = num_matches + 1
        #            print tokens.children
        self.assertEqual(num_matches, 1)


## These are test cases for the TEI XML parser
#    We want to rethink our parsing test cases because
#    1)  hand coded parsers should be secondary to parsers read in
#       from XSD or RELAXNG
#    2)  some of the methods in the parser should be refactored out
#       or removed altogether
#    3)  We should distinguish between whitebox testing (testing the
#       Parser interface) and blackbox testing (testing the implementation)
class TestTEILiteParser(unittest.TestCase):

    tei_data_path1 = None
    tei_data_path2 = None

    tei_data1 = None
    tei_data2 = None

    def setUp(self):

        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')

        self.tei_data_path1 = config.get('xutools.test.test_tools', 'TEIDataPath1')
        self.tei_data_path2 = config.get('xutools.test.test_tools', 'TEIDataPath2')

        fp = open(self.tei_data_path1, 'r')
        self.tei_data1 = fp.read()
        fp.close()

        fp = open(self.tei_data_path2, 'r')
        self.tei_data2 = fp.read()
        fp.close()

    def test_parse_head(self):
        num_matches = 0
        for tokens, s, e in TEILiteParser.headRegion.scanString(self.tei_data1):
            num_matches = num_matches + 1
        self.assertEqual(num_matches, 5)

    def test_get_region_id(self):
        # Write TEI tests for subsubsection, subsection, and section
        parser = TEILiteParser()
        expected_ids = {'subsubsection': ['1', '2'],
                         'subsection': ['1'],
                         'section': ['1', '9']}

        for region_type in expected_ids.keys():
            production = parser.getGrammarForUnit(region_type)

            ids = []
            match_forest = production.scanString(self.tei_data1)

            subtree_idx = 0
            for subtree, s, e in match_forest:
                new_id = parser.getRegionID(subtree, region_type, subtree_idx)
                ids.append(new_id)
                subtree_idx = subtree_idx + 1

            i = 0
            for id in ids:
                self.assertEqual(id, expected_ids[region_type][i])
                i = i + 1

    def test_parse_p(self):
        num_matches = 0
        for tokens, s, e in TEILiteParser.pRegion.scanString(self.tei_data1):
            num_matches = num_matches + 1
        self.assertEqual(num_matches, 6)

    def test_parse_section(self):
        num_matches = 0
        for parse_tree, s, e in TEILiteParser.sRegion.scanString(self.tei_data1):
            num_matches = num_matches + 1
        self.assertEqual(num_matches, 2)

    def test_normalize_parse_tree(self):
        num_matches = 0
        for parse_tree, s, e in TEILiteParser.pRegion.scanString(self.tei_data1):
            num_matches = num_matches + 1
            nparse_tree = TEILiteParser.normalizeParseTree(parse_tree.asList())
            self.assertTrue(nparse_tree['type'] == 'p')
            self.assertTrue(nparse_tree['id'] != None)
        self.assertEqual(num_matches, 6)

        num_matches = 0
        for parse_tree, s, e in TEILiteParser.headRegion.scanString(self.tei_data1):
            num_matches = num_matches + 1
            nparse_tree = TEILiteParser.normalizeParseTree(parse_tree.asList())
            self.assertTrue(nparse_tree['type'] == 'head')
            self.assertTrue(nparse_tree['id'] != None)
        self.assertEqual(num_matches, 5)

        num_matches = 0
        for parse_tree, s, e in TEILiteParser.sssRegion.scanString(self.tei_data1):
            num_matches = num_matches + 1
            nparse_tree = TEILiteParser.normalizeParseTree(parse_tree.asList())
            self.assertTrue(nparse_tree['type'] == 'subsubsection')
            self.assertTrue(nparse_tree['id'] != None)
        self.assertEqual(num_matches, 2)

        num_matches = 0
        for parse_tree, s, e in TEILiteParser.ssRegion.scanString(self.tei_data1):
            num_matches = num_matches + 1
            nparse_tree = TEILiteParser.normalizeParseTree(parse_tree.asList())
            self.assertTrue(nparse_tree['type'] == 'subsection')
            self.assertTrue(nparse_tree['id'] != None)
        self.assertTrue(num_matches, 1)

        num_matches = 0
        for parse_tree, s, e in TEILiteParser.sRegion.scanString(self.tei_data1):
            num_matches = num_matches + 1
            nparse_tree = TEILiteParser.normalizeParseTree(parse_tree.asList())
            self.assertTrue(nparse_tree['type'] == 'section')
            self.assertTrue(nparse_tree['id'] != None)
        self.assertTrue(num_matches, 2)


## These are test cases for the National Vulnerability Database XML Parser
#    We want to rethink our parsing test cases because
#    1)  hand coded parsers should be secondary to parsers read in
#       from XSD or RELAXNG
#    2)  some of the methods in the parser should be refactored out
#       or removed altogether
#    3)  We should distinguish between whitebox testing (testing the
#       Parser interface) and blackbox testing (testing the implementation)
class TestNVDParser(unittest.TestCase):

    nvd_data_path1 = None
    nvd_data1 = None

    def setUp(self):
        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')

        self.nvd_data_path1 = config.get('xutools.test.test_tools', 'NVDDataPath1')

        fp = open(self.nvd_data_path1, 'r')
        self.nvd_data1 = fp.read()
        fp.close()

    def test_parse_score(self):
        num_matches = 0
        for parse_tree, s, e in NVDParser.scoreRegion.scanString(self.nvd_data1):
            num_matches = num_matches + 1
        self.assertEqual(num_matches, 2)

    def test_get_region_id(self):
        # Write NVD tests for entry and cpss and score
        parser = NVDParser()
        expected_ids = {'score': ['1', '2'],
                         'entry': ['CVE-2012-0001', 'CVE-2012-0002']}
        for region_type in expected_ids.keys():
            production = parser.getGrammarForUnit(region_type)

            match_forest = production.scanString(self.nvd_data1)
            ids = []

            subtree_idx = 0
            for subtree, s, e in match_forest:
                new_id = parser.getRegionID(subtree, region_type, subtree_idx)
                ids.append(new_id)
                subtree_idx = subtree_idx + 1

            i = 0
            for id in ids:
                self.assertEqual(id, expected_ids[region_type][i])
                i = i + 1

    def atest_normalize_parse_tree(self):
        num_matches = 0
        for parse_tree, s, e in NVDParser.entryRegion.scanString(self.nvd_data1):
            #pprint.pprint(parse_tree.asList())
            num_matches = num_matches + 1
            nparse_tree = NVDParser.normalizeParseTree(parse_tree.asList())
            #pprint.pprint(nparse_tree)
        self.assertEqual(num_matches, 2)

        num_matches = 0
        for parse_tree, s, e in NVDParser.nvdRegion.scanString(self.nvd_data1):
            #pprint.pprint(parse_tree.asList())
            num_matches = num_matches + 1
            nparse_tree = NVDParser.normalizeParseTree(parse_tree.asList())
            #pprint.pprint(nparse_tree)
        self.assertEqual(num_matches, 1)

## These are test cases for the Subset C parser
#    We want to rethink our parsing test cases because
#    1)  hand coded parsers should be secondary to parsers read in
#       from Bison/Flex, or ANTLR
#    2)  some of the methods in the parser should be refactored out
#       or removed altogether
#    3)  We should distinguish between whitebox testing (testing the
#       Parser interface) and blackbox testing (testing the implementation)
class TestSubsetCParser(unittest.TestCase):

    c_data_path1 = None
    c_data1 = None

    ## Method run prior to every test
    def setUp(self):
        config = ConfigParser.RawConfigParser()
        config.read('./config/xutools.test.ini')

        self.c_data_path1 = config.get('xutools.test.test_tools', 'CDataPath1')
        data_files = [self.c_data_path1]

        fp = open(self.c_data_path1, 'r')
        self.c_data1 = fp.read()
        fp.close()

    def test_get_region_id(self):
        # Write C tests for the function
        parser = SubsetCParser()
        expected_ids = {'function': ['putstr', 'fac', 'putn', 'facpr', 'main']}

        for region_type in expected_ids.keys():
            production = parser.getGrammarForUnit(region_type)

            match_forest = production.scanString(self.c_data1)
            ids = []

            subtree_idx = 0
            for subtree, s, e in match_forest:
                new_id = parser.getRegionID(subtree, region_type, subtree_idx)
                ids.append(new_id)
                subtree_idx = subtree_idx + 1

            i = 0;
            for id in ids:
                self.assertEqual(id, expected_ids[region_type][i])
                i = i + 1


## These are test cases for parsing xupaths into a parse tree
#    We want to rethink these test cases because
#    1) If we port to C, we may use the Augeas path representation
#      in our library and we want a good set of whitebox tests for
#    2) We also want a good set of blackbox tests
class TestXPathParser(unittest.TestCase):

    # I may want to do something very similar to XML
    tei_xupath1 = "//tei:section"
    tei_xupath2 = "//tei:section/tei:subsection/tei:subsubsection[re:testsubtree('horse','gi')]"

    nvd_xupath1 = "//nvd:entry[re:testsubtree('RedHat','gi')]/nvd:cpss"
    nvd_xupath2 = "//nvd:entry[re:testsubtree('RedHat','gi')/nvd:cpss]"

    # I may want to grab all interfaces within a document
    ios_xupath1 = "//ios:interface"
    ios_xupath2 = "//ios:interface[re:testsubtree('access-group','gi')]"

    # I may want to be able to grab all C functions in a document
    c_xupath1 = "//cspec:function"
    c_xupath2 = "//cspec:function[re:testsubtree('malloc','gi')]"
    c_xupath3 = "//cspec:function/cspec:line[re:testsubtree('malloc','gi')]"

    def test_parse_ncname(self):
        parser = XPathParser()

        parses = parser.NCName.scanString(self.tei_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p.asList())
        assert(result[0][0] == 'tei')
        assert(result[1][0] == 'section')
        assert(len(result) == 2)


    def test_parse_qName(self):
        parser = XPathParser()

        parses = parser.qName.scanString(self.tei_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p.asList())
        assert(result[0][0] == 'tei:section')
        assert(len(result) == 1)

        parses = parser.qName.scanString(self.nvd_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p.asList())
        assert(result[0][0] == 'nvd:entry')
        assert(result[1][0] == 're:testsubtree')
        assert(result[2][0] == 'RedHat')
        assert(result[3][0] == 'gi')
        assert(result[4][0] == 'nvd:cpss')
        assert(len(result) == 5)

    def test_parse_stringliteral(self):
        parser = XPathParser()

        parses = parser.StringLiteral.scanString(self.nvd_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p.asList())
        #print result

    def test_parse_predicate(self):
        parser = XPathParser()
        parses = parser.predicate.scanString(self.nvd_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p.asList())

        parses = parser.predicate.scanString(self.ios_xupath2)
        result = []
        for p, s, e in parses:
            result.append(p.asList())


    def test_parse_regexpexpr(self):
        parser = XPathParser()

        parses = parser.regexpexpr.scanString(self.nvd_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p.asList())
        self.assertTrue(len(result) == 1)

        parses = parser.regexpexpr.scanString(self.ios_xupath2)
        result = []
        for p, s, e in parses:
            result.append(p.asList())
        self.assertTrue(len(result) == 1)

    def test_parse_abbrevforwardstep(self):
        parser = XPathParser()
        parses = parser.abbrevForwardStep.scanString(self.nvd_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p.asList())
        self.assertTrue(len(result) == 5)

    def test_parse_stepexpr(self):
        parser = XPathParser()
        parses = parser.stepExpr.scanString(self.nvd_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p.asList())

    def test_parse_xpath(self):
        parser = XPathParser()
        parses = parser.xPath.scanString(self.tei_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p)
        XPathParser.print_xpath(result[0].path, "")

        parser = XPathParser()
        parses = parser.xPath.scanString(self.tei_xupath2)
        result = []
        for p, s, e in parses:
            result.append(p)
        XPathParser.print_xpath(result[0].path, "")

        parser = XPathParser()
        parses = parser.xPath.scanString(self.nvd_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p)
        XPathParser.print_xpath(result[0].path, "")

        parses = parser.xPath.scanString(self.nvd_xupath2)
        result = []
        for p, s, e in parses:
            result.append(p)
        XPathParser.print_xpath(result[0].path, "")

        parses = parser.xPath.scanString(self.ios_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p)
        XPathParser.print_xpath(result[0].path, "")

        parses = parser.xPath.scanString(self.ios_xupath2)
        result = []
        for p, s, e in parses:
            result.append(p)
        XPathParser.print_xpath(result[0].path, "")

        parses = parser.xPath.scanString(self.c_xupath1)
        result = []
        for p, s, e in parses:
            result.append(p)
        XPathParser.print_xpath(result[0].path, "")

        parses = parser.xPath.scanString(self.c_xupath2)
        result = []
        for p, s, e in parses:
            result.append(p)
        XPathParser.print_xpath(result[0].path, "")

        parses = parser.xPath.scanString(self.c_xupath3)
        result = []
        for p, s, e in parses:
            result.append(p)
        XPathParser.print_xpath(result[0].path, "")
