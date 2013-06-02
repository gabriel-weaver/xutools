"""
copyright (c) 2013, Gabriel A. Weaver <gabriel.a.l.weaver@gmail.com>

This file is part of XUTools, Python Distribution

This code is free software:  you can redistribute
it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundations, either version
3 of the License, or (at your option) any later version.

XUTools is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.
                                                                                
You should have received a copy of the GNU General Public License               
along with this program.  If not, see http://www.gnu.org/licenses/
"""
from pyparsing import *
from xutools.corpus import Corpus
from xutools.analysis.distances import ZhangShashaTreeDist as TD
from xutools.grammar import GrammarLibrary
from xutools.grammar.pyparsing.BuiltinGrammar import BuiltinGrammar
from xutools.grammar.pyparsing.XUPathGrammar import XUPathGrammar
from xutools.parsers import PythonDictionaryParseTree
import re
import sys

## package xutools.tools
#   This module contains classes for each of our XUTools.  Currently 
#     this means xugrep, xuwc, and xudiff.

## The XUGrep class implements xugrep
class XUGrep():
    
    corpus = None
    element_equality_fields = None
    ## Method used by the command line interface.
    #  @param[in] xupath The xupath query that specifies a result set
    #  @param[in] input_corpus The corpus from which to extract results
    #  @return the result corpus
    @staticmethod
    def create(xupath, file_paths, element_equality_fields,\
                   path_field_equality_components=None,\
                   path_field_equality_components_is_whitelist=None):
        # Instantiate the XUPath
        xupath_parse_trees = []
        grammar_library = GrammarLibrary()
        grammar_production = grammar_library.get_grammar( XUPathGrammar.XUPATH )
        matches = grammar_production.scanString( xupath )
        for p, s, e in matches:
            xupath_parse_trees.append(p)
        xupath_pt_node = xupath_parse_trees[0].path

        # Now do XUGrep
        xugrep = XUGrep()
        xugrep.corpus = Corpus.create_from_files( file_paths, element_equality_fields,\
                                                      path_field_equality_components,\
                                                      path_field_equality_components_is_whitelist )
        xugrep.process_xupath(xupath_pt_node)
        return xugrep

    def process_xupath(self, xupath_pt_node):
        if xupath_pt_node == None or len(xupath_pt_node) == 0:
            return

        self.process_step(xupath_pt_node.current_step )
        self.process_next_steps(xupath_pt_node.next_steps )
        
    def process_step(self, step_pt_node):
        if step_pt_node == None or len(step_pt_node) == 0:
            return
        
        self.process_production( step_pt_node.production )
        self.process_predicate( step_pt_node.predicate )
        
    def process_next_steps(self, next_steps_pt_nodes):
        if next_steps_pt_nodes == None or len(next_steps_pt_nodes) == 0:
            return
        
        for step_pt_node in next_steps_pt_nodes:
            if step_pt_node != '/' and step_pt_node != '//':
                self.process_step(step_pt_node)
                
    def process_production(self, production_pt_node):
        if production_pt_node == None:
            return
        
        old_corpus = self.corpus
        language_name = production_pt_node[0]
        if language_name != BuiltinGrammar.FILE:
            self.corpus = old_corpus.parse( language_name )


    def process_predicate( self, predicate_pt_node ):
        if predicate_pt_node == None or len(predicate_pt_node) == 0:
            return
        
        pattern = re.compile(predicate_pt_node.re_match[2])
        self.corpus.filter( lambda x: pattern.search(x.text) != None )
        self.process_next_steps(predicate_pt_node.next_steps)

## The XUWc class implements xuwc
class XUWc():

    xugrep_corpus = None
    counts = None
    count_unit = None
    container_unit = None
    label_path_delimiter = None

    ## Method used by the command line interface
    #  @param[in] xupath The xupath query that specifies a result set to count
    #  @param[in] container_unit The context in which to count
    #  @param[in] count_unit The unit to count within the container unit
    #  @param[in] file_paths The files from which to extract results
    #  @return the result corpus
    @staticmethod
    def create(xupath, file_paths, element_equality_fields, count_unit, container_unit="builtin:file", label_path_delimiter=":" ):

        xugrep = XUGrep.create(xupath, file_paths, element_equality_fields)

        xuwc = XUWc()
        xuwc.container_unit = container_unit
        xuwc.count_unit = count_unit
        xuwc.counts = {}
        xuwc.xugrep_corpus = xugrep.corpus
        xuwc.label_path_delimiter = label_path_delimiter

        """
         0.  Run xugrep
         1.  Get the container_unit's index within the language name path
         2.  Loop through the corpus results 
             a) assert that the 
                element.language_name_path[container_unit_index] == container_unit
             b) label_path_key = " ".join(element.label_path)
                counts[label] += 1 (unless count unit is a builtin, then we extract appropriately)
             c) output the counts, sorted by label somehow   
        """
        for element in xuwc.xugrep_corpus.list():
            if container_unit in element.language_name_path:
                container_idx = element.language_name_path.index(container_unit)
            else:
                raise Exception("Corpus element not extracted from " + container_unit)
            container_label_path = ":".join(element.label_path[:container_idx + 1])
            if not container_label_path in xuwc.counts:
                xuwc.counts[container_label_path] = 0
            xuwc.counts[container_label_path] += xuwc.get_match_counts( element )
        return xuwc

    def get_match_counts( self, element ):
        match_counts = None
        container_idx = element.language_name_path.index( self.container_unit )
        if BuiltinGrammar.BYTE == self.count_unit:
            if container_idx != len( element.language_name_path ) - 1:
                raise TypeError( BuiltinGrammar.BYTE + " extraction must be done on last language unit in XUPath")
            match_counts = len( element.text )
        elif BuiltinGrammar.CHARACTER == self.count_unit:
            if container_idx != len( element.language_name_path ) - 1:
                raise TypeError( BuiltinGrammar.CHARACTER + " extraction must be done on last language unit in XUPath")
            match_counts = len( element.text )
        elif BuiltinGrammar.WORD == self.count_unit:
            if container_idx != len( element.language_name_path ) - 1:
                raise TypeError( BuiltinGrammar.WORD + " extraction must be done on last language unit in XUPath")
            match_counts = len( element.text.split() )
        elif self.count_unit in element.language_name_path:
            count_idx = element.language_name_path.index( self.count_unit )
            if count_idx < container_idx:
                raise IndexError("Count unit " + self.count_unit + " is not contained in context type " + self.container_unit )
            match_counts = 1
        else:
            raise ValueError("Count unit " + self.count_unit + " is not contained in context type " + self.container_unit )
        return match_counts

    def get_container_unit(self):
        return self.container_unit
    
    def get_count_unit(self):
        return self.count_unit

    def get_counts(self):
        return self.counts

    def output(self):
        rows = []
        for container_label_path in self.counts.keys():
            count = self.counts[container_label_path]
            row = [ container_label_path, str(count)]
            row_str = "\t".join(row)
            rows.append( row_str )
        return rows
        
class XUDiff():
    ##
    # @param[in] xupath The xupath query that specifies a result set to count.  
    # @param[in] input_files The files to compare
    # @param[in] output_fields The fields to output
    # @param[in] cost_fn The cost of edit operations 
    # @return parameters to output an edit script
    @staticmethod
    def xudiff_main( xupath, input_files, output_field_names, comparison_field, cost_fn_name ):

        # Handle the xupath
        language_name = xupath.replace("/","")

        # Open the input files
        if len(input_files) != 2:
            print "Error, two input files are required.\n"
            return -1
        
        infile1 = input_files[0]
        infile2 = input_files[1]
        
        fp = open( infile1, 'r' )
        text1 = fp.read()
        fp.close()

        fp = open( infile2, 'r' )
        text2 = fp.read()
        fp.close()
        
        # Fix the output field
        if output_field_names == None or output_field_names == "":
            output_field_names = "value,type"

        tree_node_output_fields = output_field_names.split(",")
        
        # Fix the comparison field
        if comparison_field == None or comparison_field == "":
            comparison_field = "value"

        # Fix the cost fn
        if TD.WORD_EDIST_COST == cost_fn_name:
            cost_fn = TD.WORD_EDIST_COST
        elif TD.CHARACTER_EDIST_COST == cost_fn_name:
            cost_fn = TD.CHARACTER_EDIST_COST
        else:
            cost_fn = TD.UNIT_COST
            
        t1 = PythonDictionaryParseTree.create( text1, language_name )
        t2 = PythonDictionaryParseTree.create( text2, language_name )

        td = TD.create(t1, t2, cost_fn, comparison_field)
        td.compute_mapping()
        td.output_mapping(sys.stdout, tree_node_output_fields)
        
