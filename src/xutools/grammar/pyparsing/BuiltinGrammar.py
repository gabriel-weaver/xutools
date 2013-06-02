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
from pyparsing import *

## @package xutools.grammar.pyparsing
class BuiltinGrammar():
    

    line = restOfLine.setWhitespaceChars(' \t') + Optional(Literal("\n"))
    line.leaveWhitespace()

    GRAMMAR_NAME = "builtin"
    BYTE = GRAMMAR_NAME + ":" + "byte"
    CHARACTER = GRAMMAR_NAME + ":" + "character"
    DIRECTORY = GRAMMAR_NAME + ":" + "directory"
    FILE = GRAMMAR_NAME + ":" + "file"
    LINE = GRAMMAR_NAME + ":" + "line"
    WORD = GRAMMAR_NAME + ":" + "word"
    
    def get_grammar(self, language_name):
        
        if self.LINE == language_name:
            return self.line
        else:
            raise NotImplementedError("Coming soon...")

    def get_language_names(self):
        language_names = [ self.LINE ]
        return language_names

    def get_label_for_match(self, language_name, match, match_idx):
        label = None
        if ( "label" in match ):
            label = match["label"].strip()
        else:
            label = str(match_idx)
        return label

    def normalize_parse_tree( self, parse_tree_list ):
        raise NotImplementedError("Coming soon...")
