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
from xutools.grammar.pyparsing.BuiltinGrammar import BuiltinGrammar
from xutools.grammar.pyparsing.CiscoIOSGrammar import CiscoIOSGrammar
from xutools.grammar.pyparsing.TEIXMLGrammar import TEIXMLGrammar
from xutools.grammar.pyparsing.XUPathGrammar import XUPathGrammar

class GrammarLibrary():
    
    BUILTIN_GRAMMAR_NAME = "builtin"
    CISCOIOS_GRAMMAR_NAME = "ios"
    TEIXML_GRAMMAR_NAME = "tei"
    XUPATH_GRAMMAR_NAME = "xupath"

    # Given a language name, return the path to the grammar 
    #  in which that language construct is specified.
    #
    # @param[in] language_name
    # @return The path to the grammar that specifies the construct
    def get_grammar_path(self, language_name):
        raise NotImplementedError("Coming soon...")

    # Given a language name, get the grammar name
    #
    # @param[in] language_name
    # @return The grammar name for the specified language
    def get_grammar_name( self, language_name ):
        [ grammar_name, production_name ] = language_name.split(':')
        return grammar_name

    # Given a language name, get the production name
    #
    # @param[in] language_name
    # @return The production name for the specified language
    def get_production_name( self, language_name ):
        [ grammar_name, production_name ] = language_name.split(':')
        return production_name

    # Given a language name, get the parser used to recognize
    #  strings in that language.
    #
    # @param[in] language_name
    # @return The parser for the specified language
    def get_grammar(self, language_name):
        grammar_name = self.get_grammar_name( language_name )
        grammar = None

        grammar_instance = self.get_grammar_instance(language_name)
        grammar = grammar_instance.get_grammar(language_name)
        return grammar

    # Given a path to a grammar library, return a list of 
    #   grammars defined within that library
    #
    # @param[in] grammar_library_path
    # @return A list of grammars within that library
    def get_grammar_names(self, grammar_library_path):
        raise NotImplementedError("Coming soon...")

    # Given a path to a grammar library, and a grammar_name, return
    #   a list of languages defined within that grammar
    #
    # @param[in] grammar_library_path
    # @param[in] grammar_name
    # @return A list of grammars within that library
    def get_language_names(self, grammar_name):
        if ( XUPATH_GRAMMAR_NAME == grammar_name ):
            return XUPathGrammar.get_language_names()
        else:
            raise NotImplementedError("Coming soon...")
    
    def get_grammar_instance(self, language_name):
        grammar_name = self.get_grammar_name( language_name )
        grammar_instance = None
        if ( self.BUILTIN_GRAMMAR_NAME == grammar_name ):
            grammar_instance = BuiltinGrammar()
        elif ( self.CISCOIOS_GRAMMAR_NAME == grammar_name ):
            grammar_instance = CiscoIOSGrammar()
        elif ( self.TEIXML_GRAMMAR_NAME == grammar_name ):
            grammar_instance = TEIXMLGrammar()
        elif ( self.XUPATH_GRAMMAR_NAME == grammar_name ):
            grammar_instance = XUPathGrammar()
        else:
            raise NotImplementedError("Coming soon...")
        return grammar_instance
        
    def normalize_parse_tree(self, language_name, parse_tree ):
        grammar = self.get_grammar_instance( language_name )
        ptl = parse_tree.asList()
        normalized_parse_tree = grammar.normalize_parse_tree( ptl )
        return normalized_parse_tree
        
    
    
