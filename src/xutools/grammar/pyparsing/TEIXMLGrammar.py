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
from xutools.exceptions import UndefinedLanguageName
import sys
import types

## @package xutools.grammar.pyparsing
class TEIXMLGrammar():

    commentStart = Literal("<!--")
    commentEnd = Literal("-->")
    ## Production for TEI comments, reference is 'comment'
    commentRegion = commentStart + SkipTo( MatchFirst(commentEnd) ) + commentEnd

    headStart, headEnd = makeXMLTags("tei:head")
    ## Production for TEI headers, reference is 'head'
    headRegion = headStart + SkipTo(MatchFirst(headEnd)).setResultsName("label") + headEnd
    
    pStart, pEnd = makeXMLTags("tei:p")
    pStart.setParseAction( withAttribute(n=withAttribute.ANY_VALUE) )
    ## Production for TEI paragraphs, reference is 'p'
    pRegion = pStart + SkipTo(MatchFirst(pEnd)) + pEnd

    tableStart, tableEnd = makeXMLTags("tei:table")
    ## Production for TEI Tables, reference is 'table'
    tableRegion = tableStart + SkipTo(MatchFirst(tableEnd)) + tableEnd

    sssStart, sssEnd = makeXMLTags("div")
    sssStart.setParseAction( withAttribute( type="subsubsection" ) )
    ## Production for TEI Subsubsections, reference is 'subsubsection'
    sssRegion = sssStart + headRegion + ZeroOrMore(Group(pRegion) | Group(commentRegion) | Group(tableRegion) ) + MatchFirst(sssEnd)
    
    ssStart, ssEnd = makeXMLTags("div")
    ssStart.setParseAction( withAttribute( type="subsection" ) )
    ## Production for TEI Subsections, reference is 'subsection'
    ssRegion = ssStart + headRegion + ZeroOrMore( Group(pRegion) | Group(commentRegion) | Group(sssRegion) | Group(tableRegion) )+ MatchFirst(ssEnd)
    
    sStart, sEnd = makeXMLTags("div")
    sStart.setParseAction( withAttribute( type="section" ) )
    ## Production for TEI Sections, reference is 'section'
    #sRegion = sStart + Group( Group(headRegion) + ZeroOrMore( Group(pRegion) | Group(commentRegion) | Group(ssRegion) | Group(tableRegion) ) ) + MatchFirst(sEnd)
    sRegion = sStart + headRegion + ZeroOrMore( Group(pRegion) | Group(commentRegion) | Group(ssRegion) | Group(tableRegion) )  + MatchFirst(sEnd)

    ## Production for the entire TEI document, reference is 'edition'
    editionRegion = Group( OneOrMore( Group( sRegion ) ) )
    
    GRAMMAR_NAME = "tei"

    SECTION = GRAMMAR_NAME + ":" + "section"
    SUBSECTION = GRAMMAR_NAME + ":" + "subsection"
    SUBSUBSECTION = GRAMMAR_NAME + ":" + "subsubsection"
    PARAGRAPH = GRAMMAR_NAME + ":" + "paragraph"

    # Given a language name, get the grammar that specifies strings in
    #  that language
    #
    # @param[in] language_name
    # @exception UndefinedLanguageName if the language name was not found
    def get_grammar(self, language_name):

        if ( self.SECTION == language_name ):
            return self.sRegion
        elif ( self.SUBSECTION == language_name ):
            return self.ssRegion
        elif ( self.SUBSUBSECTION == language_name ):
            return self.sssRegion
        elif ( self.PARAGRAPH == language_name ):
            return self.pRegion
        else:
            raise UndefinedLanguageName("Unable to find language name:" + language_name +\
                                            " in TEIXMLGrammar")

    # Get all language names
    #
    # @return an array of all language names defined by the grammar
    def get_language_names(self):
        language_names = [ self.SECTION, self.SUBSECTION, self.SUBSUBSECTION, self.PARAGRAPH]
        return language_names

    def get_label_for_match(self, language_name, match, match_idx):
        label = None
        if ( "label" in match ):
            label = match["label"].strip()
        elif (self.PARAGRAPH == language_name):
            if "n" in match:
                label = match["n"]
            else:
                label = str(match_idx)
        else:
            raise ValueError("Unable to find label for match to " + language_name)
        return label

    ## Take a parse object and put it into a canonical 
    #   parse tree representation.  Rethink this interface in terms of 
    #   the XUTools (space and time complexity) and also in terms
    #   of extant libraries such as libaugeas.
    #
    #  @param parse_tree_list The list of parse trees that resulted
    #   from parsing
    #  @return the normalized parse tree
    #  @note  think about how to do this more generally in a language-agnostic way.
    def normalize_parse_tree( self, parse_tree_list ):
        ntree = { 'id':None, 
                  'type':None,
                  'children':[] }
        for item in parse_tree_list:
            if isinstance( item, types.ListType ):
                if ( item[0] == 'n' ):
                    ntree['id'] = item[1]
                elif ( 'type' == item[0] ):
                    ntree['type'] = item[1]
                elif ( isinstance( item[0], types.ListType ) ):
                    for subtree_list in item:
                        nsubtree = self.normalize_parse_tree( subtree_list )
                        ntree['children'].append( nsubtree );
            elif isinstance( item, types.StringType ):
                if ( not '</' in item ):
                    ntree['value'] = item
                elif ( 'tei:p' in item ):
                    ntree['type'] = "p"
                elif ( 'tei:head' in item ):
                    ntree['type'] = "head"
        return ntree

