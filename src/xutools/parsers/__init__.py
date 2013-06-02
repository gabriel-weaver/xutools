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
from pyparsing import *
import sys
import types
from xutools.grammar import GrammarLibrary 

## @package xutools.parsers

##
# An implementation of the parse tree that uses a Python Dictionary
#
class PythonDictionaryParseTree():

    # The root of the parse tree
    root = None

    @staticmethod
    def create(text, language_name):
        pd_parse_tree = PythonDictionaryParseTree()
        grammar_library = GrammarLibrary()
        production_parser = grammar_library.get_grammar( language_name )
        parse_tree = production_parser.parseString( text )
        normalized_pt = grammar_library.normalize_parse_tree( language_name, parse_tree )
        pd_parse_tree.root = normalized_pt
        return pd_parse_tree

    @staticmethod
    def create_from_dict( root_node ):
        pd_parse_tree = PythonDictionaryParseTree()
        pd_parse_tree.root = root_node
        return pd_parse_tree

    @staticmethod
    def create_tree_node( index, label, text, children ):
        tree_node = {}
        tree_node['index'] = index
        tree_node['label'] = label
        tree_node['text'] = text
        tree_node['children'] = children
        return tree_node

    def preorder_traverse( self, visitor_action, action_params ):
        self.preorder_traverse_worker( self.root, visitor_action, action_params )

    def preorder_traverse_worker(self, tree_node, visitor_action, action_params):
        visitor_action( tree_node, action_params )
        for child in tree_node['children']:
            self.preorder_traverse_worker( child, visitor_action, action_params )

    def postorder_traverse( self, visitor_action, action_params ):
        self.postorder_traverse_worker( self.root, visitor_action, action_params )

    def postorder_traverse_worker(self, tree_node, visitor_action, action_params ):
        for child in tree_node['children']:
            self.postorder_traverse_worker( child, visitor_action, action_params )
        visitor_action( tree_node, action_params )

    # We calculate this every time for now
    def tree_size(self):
        action_params = {}

        action_params['position'] = 1
        self.postorder_traverse( PythonDictionaryParseTree.iterate_position, action_params )
        tree_sz = action_params['position'] - 1  # we increment after last root too
        return tree_sz

    ## Different Visitor Actions
    @staticmethod
    def set_position_as_index( tree_node, action_params ):
        tree_node['index'] = action_params['position']
        action_params['position'] = action_params['position'] + 1
        
    @staticmethod
    def iterate_position( tree_node, action_params ):
        action_params['position'] = action_params['position'] + 1
    
    @staticmethod
    def get_field_value( tree_node, action_params ):
        field = action_params['field']
        action_params['indices'].append( tree_node[field] )
