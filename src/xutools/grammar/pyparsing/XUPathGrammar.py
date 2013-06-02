"""
Copyright (c) 2010-2012, Gabriel A. Weaver, Department of Computer
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
from xutools.exceptions import UndefinedLanguageName
import sys
import types

## @package xutools.grammar.pyparsing

class XUPathGrammar():

    NCName = Word(alphanums + '.-')
    qName = Combine(NCName + Literal(':') + NCName) | NCName

    StringLiteral = Literal("'") + ZeroOrMore(Word(alphanums + ':.*?\/-')) + \
        Literal("'")

    regexpexpr = Group(Combine(Literal("re:testsubtree") + Literal("(")) + \
        StringLiteral + Combine(Literal(",") + StringLiteral + \
            Literal(")"))).setResultsName("re_match")

    stepExpr = Forward()
    expr = regexpexpr + Group(ZeroOrMore((Literal('/') | Literal('//')) + \
        Group(stepExpr))).setResultsName("next_steps")
    predicate = Literal('[') + expr + Literal(']')

    abbrevForwardStep = Optional(Literal('@')) + (qName | Literal('*'))
    stepExpr << Group(Literal('.') | \
        abbrevForwardStep).setResultsName("production") + \
        Group(Optional(predicate)).setResultsName("predicate")
    relativePathExpr = Group(stepExpr).setResultsName("current_step") + \
        Group(ZeroOrMore((Literal('/') | Literal('//')) + \
            Group(stepExpr))).setResultsName("next_steps")
    pathExpr = (Literal('//') + \
        Group(Optional(relativePathExpr)).setResultsName("path")) | \
        (Literal('/') + Group(relativePathExpr).setResultsName("path")) | \
        Group(relativePathExpr).setResultsName("path")
    xuPath = pathExpr
    
    GRAMMAR_NAME = "xupath"
    XUPATH =  GRAMMAR_NAME + ":" + "xupath"

    # Given a language name, get the grammar that specifies strings in
    #  that language
    #
    # @param[in] language_name
    # @exception UndefinedLanguageName if the language name was not found
    def get_grammar(self, language_name):

        if ( self.XUPATH == language_name ):
            return self.xuPath
        else:
            raise UndefinedLanguageName("Unable to find language name: " + language_name +\
                                            " in XUPathGrammar")
    def get_language_names(self):
        language_names = [ self.XUPATH ]
        return language_names

    def get_label_for_match(self, language_name, match, match_idx):
        label = str(match_idx)
        return label

    def normalize_parse_tree( self, parse_tree_list ):
        raise NotImplementedError("Coming soon...")
