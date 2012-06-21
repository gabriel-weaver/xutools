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
from pyparsing import *
import sys
import types

## @package xutools.parsers
#     The Parser module contains classes for every 
#     grammar that is currently supported by XUTools.
#    
#    We will eventually rethink the parser module to 
#     parse Grammars expressed in Flex/Bison, etc.
#

## The XPathParser class is used to parse xupath expressions.
#    This is a very limited implementation of the xpath syntax.
#  
#  @note There is no reference string for this grammar
class XPathParser():

    NCName = Word( alphanums + '.-' )
    qName = Combine(NCName + Literal(':') + NCName) | NCName

    StringLiteral = Literal("'") + ZeroOrMore( Word(alphanums + ':.*?\/-') ) + Literal("'") 

    regexpexpr = Group( Combine( Literal("re:testsubtree") + Literal("(") ) + StringLiteral + Combine(Literal(",") + StringLiteral  + Literal(")") ) ).setResultsName("re_match")

    stepExpr = Forward()
    expr = regexpexpr + Group( ZeroOrMore( (Literal('/') | Literal('//') ) + Group(stepExpr) ) ).setResultsName("next_steps")
    predicate = Literal('[') + expr + Literal(']') 

    abbrevForwardStep = Optional( Literal('@') ) + (qName | Literal('*'))
    stepExpr << Group( Literal('.') | abbrevForwardStep ).setResultsName("cf_match") + Group( Optional(predicate) ).setResultsName("predicate") 
    relativePathExpr = Group(stepExpr).setResultsName("current_step") + Group( ZeroOrMore( (Literal('/') | Literal('//')) + Group(stepExpr) ) ).setResultsName("next_steps")
    pathExpr = ( Literal('//') + Group( Optional(relativePathExpr) ).setResultsName("path") ) | ( Literal('/') + Group(relativePathExpr).setResultsName("path") ) | Group( relativePathExpr ).setResultsName("path")
    xPath = pathExpr

    ## Action to take a tnode of type 'xpath' when printing xpath
    #   parse tree.
    #  @param xpath the 'xpath' node to visit
    #  @param indent the current indentation level of the output string
    @staticmethod
    def print_xpath( xpath, indent ):
        if xpath == None or xpath == '':
            return
        XPathParser.print_step( xpath.current_step, indent + " " )
        XPathParser.print_next_steps( xpath.next_steps, indent)

    ## Action to take at node of type 'step' when printing xpath
    #   parse tree.        
    #  @param step the step node to visit
    #  @param indent the current indentation level of the output string
    @staticmethod
    def print_step( step, indent ):
        if step == None or step == '':
            return
        print indent + "step:"
        XPathParser.print_cf_match( step.cf_match, indent + " ")
        XPathParser.print_predicate( step.predicate, indent)
    
    ## Action to take at node of type 'next_steps' when printing xpath
    #   parse tree.
    #  @param next_steps the node to visit
    #  @param indent the current indentation level of the output string
    @staticmethod
    def print_next_steps( next_steps, indent ):
        if next_steps == None or next_steps == '' or len(next_steps) == 0:
            return

        for step in next_steps:
            if step != '/' and step != '//':
                XPathParser.print_step( step, indent + " " )

    ## Action to take at node of type 'cf_match' when printing xpath
    #   parse tree
    #  @param cf_match the node to visit
    #  @param indent the current indentation level of the output string
    @staticmethod
    def print_cf_match( cf_match, indent ):
        if cf_match == None or cf_match == '':
            return
        print indent + "cf_match: " + cf_match[0]

    ## Action to take at node of type 're_match' when printing xpath
    #   parse tree
    #  @param re_match the node to visit
    #  @param indent the current indentation level of the output string
    @staticmethod
    def print_re_match( re_match, indent ):
        if re_match == None or re_match == '':
            return
        print indent + "re_match: " + re_match[2]
    
    ## Action to take at node to type 'predicate' when printing xpath
    #   parse tree
    #  @param predicate the node to visit
    #  @param indent the current indentation level of the output string
    @staticmethod
    def print_predicate( predicate, indent ):
        if predicate == None or predicate == '' or len(predicate) == 0:
            return
        XPathParser.print_re_match( predicate.re_match, indent + " " )
        XPathParser.print_next_steps( predicate.next_steps, indent + " " )


## The TEILiteParser class is used to parse XML documents encoded 
#    in TEI-XML.
#
#  @note The grammar reference is 'tei'
class TEILiteParser():

    commentStart = Literal("<!--")
    commentEnd = Literal("-->")
    ## Production for TEI comments, reference is 'comment'
    commentRegion = commentStart + SkipTo( MatchFirst(commentEnd) ) + commentEnd

    headStart, headEnd = makeXMLTags("tei:head")
    ## Production for TEI headers, reference is 'head'
    headRegion = headStart + SkipTo(MatchFirst(headEnd)) + headEnd
    
    pStart, pEnd = makeXMLTags("tei:p")
    ## Production for TEI paragraphs, reference is 'p'
    pRegion = pStart + SkipTo(MatchFirst(pEnd)) + pEnd

    tableStart, tableEnd = makeXMLTags("tei:table")
    ## Production for TEI Tables, reference is 'table'
    tableRegion = tableStart + SkipTo(MatchFirst(tableEnd)) + tableEnd

    sssStart, sssEnd = makeXMLTags("div")
    sssStart.setParseAction( withAttribute( type="subsubsection" ) )
    ## Production for TEI Subsubsections, reference is 'subsubsection'
    sssRegion = sssStart + Group( Group(headRegion) + ZeroOrMore(Group(pRegion) | Group(commentRegion) | Group(tableRegion) ) ) + MatchFirst(sssEnd)
    
    ssStart, ssEnd = makeXMLTags("div")
    ssStart.setParseAction( withAttribute( type="subsection" ) )
    ## Production for TEI Subsections, reference is 'subsection'
    ssRegion = ssStart + Group( Group(headRegion) + ZeroOrMore( Group(pRegion) | Group(commentRegion) | Group(sssRegion) | Group(tableRegion) ) )+ MatchFirst(ssEnd)
    
    sStart, sEnd = makeXMLTags("div")
    sStart.setParseAction( withAttribute( type="section" ) )
    ## Production for TEI Sections, reference is 'section'
    sRegion = sStart + Group( Group(headRegion) + ZeroOrMore( Group(pRegion) | Group(commentRegion) | Group(ssRegion) | Group(tableRegion) ) ) + MatchFirst(sEnd)

    ## Production for the entire TEI document, reference is 'edition'
    editionRegion = Group( OneOrMore( Group( sRegion ) ) )

    refKey = "id_attr"

    ## Given a parse tree node for a text region, return the corresponding ID
    #  @param[in]     subtree_parse the parse tree node
    #  @param[in]     region_type   the type of the node
    #  @param[in,out] subtree_idx   a node index determined by a tree traversal
    #  @return a string that encodes the region ID
    #  @exception UnrecognizedProductionRef the production reference is not recognized
    #  @exception MalformedParseTree   the parse tree has an unexpected format
    def getRegionID( self, subtree_parse, region_type, subtree_idx ):
        result = None
        if ( "subsubsection" == region_type or "subsection" == region_type or "section" == region_type ):
            if subtree_parse[1][0] == 'n':
                result = subtree_parse[1][1]
            else:
                print "Unrecognized parse tree for entry: " + str(subtree_parse)
                sys.exit(-1)
        elif ( "p" == region_type ):
            result = str( subtree_idx + 1 )
        else:
            print "unrecognized region type: " + region_type
            sys.exit(-1)

        return result

    ## Retrieve a production by reference
    #  @param[in] report_unit  This is the production reference
    #  @return the production
    #  @exception UnrecognizedProductionRef
    def getGrammarForUnit( self, report_unit ):
        if ( "comment" == report_unit):
            regionGrammar = self.commentRegion
        elif ( "edition" == report_unit ):
            regionGrammar = self.editionRegion
        elif ( "head" == report_unit ):
            regionGrammar = self.headRegion
        elif ( "p" == report_unit ):
            regionGrammar = self.pRegion
        elif ( "section" == report_unit ):            
            regionGrammar = self.sRegion
        elif ( "subsection" == report_unit ):
            regionGrammar = self.ssRegion
        elif ( "subsubsection" == report_unit ):
            regionGrammar = self.sssRegion
        elif ( "table" == report_unit ):
            regionGrammar = self.tableRegion
        else:
            print "Unknown Grammar error!\n"
            print report_unit
            sys.exit(-1)

        return regionGrammar
    
    ## Extract all occurrences of strings in the language
    #   of the production from the text.
    #
    #  @param grammar The productionObject, this should be 
    #    a production reference
    #  @param text The string from which to extract occurrences
    #  @param match Not sure what this is doing
    #  @return a list of strings in the language of this production 
    #    from the text
    #  @note What about Exceptions?  Should we be returning tokens 
    #    instead so that we can support highlighting, etc?
    def getOriginalText( self, grammar, text, match ):
        regions = []
        matchExpr = originalTextFor( grammar ).scanString(text)
        for tokens, s, e in matchExpr:
            if match == None:
                regions.append( tokens[0].strip() )
            elif match in tokens[0]:
                regions.append( tokens[0].strip() )
        return regions


    ## Take a parse object and put it into a canonical 
    #   parse tree representation.  Rethink this interface in terms of 
    #   the XUTools (space and time complexity) and also in terms
    #   of extant libraries such as libaugeas.
    #
    #  @param parse_tree_list The list of parse trees that resulted
    #   from parsing
    #  @return the normalized parse tree
    #  @note  think about how to do this more generally in a language-agnostic way.
    @staticmethod
    def normalizeParseTree( parse_tree_list ):
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
                        nsubtree = TEILiteParser.normalizeParseTree( subtree_list )
                        ntree['children'].append( nsubtree );
            elif isinstance( item, types.StringType ):
                if ( not '</' in item ):
                    ntree['value'] = item
                elif ( 'tei:p' in item ):
                    ntree['type'] = "p"
                elif ( 'tei:head' in item ):
                    ntree['type'] = "head"
        return ntree

## The BuiltinParser class contains frequently-used constructs
# 
#  @note The grammar reference is 'builtin'
class BuiltinParser():
    
    ## Production for lines, reference is 'line'
    lineRegion = restOfLine.setWhitespaceChars(' \t') + Optional(Literal("\n"))
    lineRegion.leaveWhitespace()

    ## Given a parse tree node for a text region, return the corresponding ID
    #  @param[in]     subtree_parse  the parse tree node
    #  @param[in]     region_type    the type of the node
    #  @param[in,out] subtree_idx    a node index determined by a tree traversal
    #  @return a string that encodes the region ID
    #  @exception UnrecognizedProductionRef the production reference is not recognized
    #  @exception MalformedParseTree        the parse tree has an unexpected format
    def getRegionID( self, subtree_parse, region_type, subtree_idx ):
        result = None
        if 'line' == region_type:
            result = str( subtree_idx + 1 )
        else:
            print "unrecognized region type: " + region_type
            sys.exit(-1)
        return result

    ## Retrieve a production by reference
    #  @param[in] report_unit  This is the production reference
    #  @return the production
    #  @exception UnrecognizedProductionRef
    def getGrammarForUnit( self, region_type ):
        if ( "line" == region_type ):
            regionGrammar = self.lineRegion
        else:
            printf("Unknown Grammar error!\n")
            sys.exit(-1)
        return regionGrammar

## The CiscoIOSParser class is used to parse Cisco IOS files encoded
#   in TEI-XML.
#  
#  @note The grammar reference is 'ios'
class CiscoIOSParser():

    classMapStart = LineStart() + Group(Literal("class-map") + restOfLine) + LineEnd()
    classMapStart.leaveWhitespace()

    policyMapStart = LineStart() + Group(Literal("policy-map") + restOfLine) + LineEnd()
    policyMapStart.leaveWhitespace()

    vlanStart = LineStart() + Group(Literal("vlan") + restOfLine) + LineEnd()
    vlanStart.leaveWhitespace()

    interfaceStart = LineStart() + Group(Literal("interface")  + restOfLine) + LineEnd()
    interfaceStart.leaveWhitespace()

    cryptoStart = LineStart() + Group(Literal("crypto") + restOfLine) + LineEnd()
    cryptoStart.leaveWhitespace()

    blockEnd = LineStart() + Literal("!") + ZeroOrMore(LineEnd())
    blockEnd.leaveWhitespace()

    ## This should not be used, instead use the builtin:line reference
    lineRegion = restOfLine.setWhitespaceChars(' \t') + Optional(Literal("\n"))
    lineRegion.leaveWhitespace()

    ## This should not be used, instead use builtin:line reference
    indentedLineRegion = LineStart() + " " + restOfLine + LineEnd()
    indentedLineRegion.leaveWhitespace()

    ## Production for Cisco IOS VLANs, reference is 'vlan'
    vlanRegion = vlanStart + Group( OneOrMore(Group(indentedLineRegion)) ) + Group(blockEnd)
    vlanRegion.leaveWhitespace()

    ## Production for Cisco IOS interfaces, reference is 'interface'
    interfaceRegion = interfaceStart + Group( OneOrMore(Group(indentedLineRegion)) ) + Group(blockEnd)
    interfaceRegion.leaveWhitespace()

    ## Production for Cisco IOS crypto blocks, reference is 'crypto'
    cryptoRegion = cryptoStart + Group( ZeroOrMore(Group(indentedLineRegion)) ) + Group(blockEnd)
    cryptoRegion.leaveWhitespace()

    ## Production for Cisco IOS class-maps, reference is 'classmap'
    classMapRegion = classMapStart + Group( ZeroOrMore(Group(indentedLineRegion)) ) + Optional(Group(blockEnd))
    classMapRegion.leaveWhitespace()

    ## Production for Cisco IOS policy-maps, reference is 'policymap'
    policyMapRegion = policyMapStart + Group( ZeroOrMore(Group(indentedLineRegion)) ) + Optional(Group(blockEnd))
    policyMapRegion.leaveWhitespace()

    ## Production for Cisco IOS config files, the entire file. reference is 'config'
    configFileRegion = Group( OneOrMore( Group(interfaceRegion) | Group(cryptoRegion) | Group(vlanRegion) | Group(classMapRegion) | Group(policyMapRegion) ) )
    configFileRegion.leaveWhitespace()

    refKey = "label"


    ## Given a parse tree node for a text region, return the corresponding ID
    #  @param[in]     subtree_parse  the parse tree node
    #  @param[in]     region_type    the type of the node
    #  @param[in,out] subtree_idx    a node index determined by tree traversal
    #  @return a string that encodes the region ID
    #  @exception UnrecognizedProductionRef the production reference is not recognized
    #  @exception MalformedParseTree the parse tree has an unexpected format
    #  @note If we return None, then a number gets assigned that starts at 1
    #          since files start with line 1.  This is hackish, figure out a nice interface.
    def getRegionID( self, subtree_parse, region_type, subtree_idx ):
        result = None
        if 'interface' == region_type:
            if subtree_parse[0][0] == 'interface':
                result = subtree_parse[0][1].strip()
            else:
                print "Unrecognized parse for interface " + str(subtree_parse)
        elif 'policyMap' == region_type:
            if subtree_parse[0][0] == 'policy-map':
                result = subtree_parse[0][1].strip()
            else:
                print "Unrecognized parse for policy-map " + str(subtree_parse)
        elif 'vlan' == region_type:
            if subtree_parse[0][0] == 'vlan':
                result = subtree_parse[0][1].strip()
            else:
                print "Unrecognized parse for vlan " + str(subtree_parse)
        elif 'line' == region_type:
            result = str( subtree_idx + 1 )
        elif 'classMap' == region_type:
            if subtree_parse[0][0] == 'class-map':
                result = subtree_parse[0][1].strip().split()[1]
            else:
                print "Unrecognized parse for class-map " + str(subtree_parse)
        elif 'config' == region_type:
            result = "root"
        else:
            print "unrecognized region type: " + region_type
            sys.exit(-1)

        return result

    ## Retrieve a production by reference
    #  @param[in] report_unit  This is the production reference
    #  @return the production
    #  @exception UnrecognizedProductionRef
    def getGrammarForUnit( self, report_unit ):
        if ( "classMap" == report_unit ):
            regionGrammar = self.classMapRegion
        elif ( "interface" == report_unit ):
            regionGrammar = self.interfaceRegion
        elif ( "line" == report_unit ):
            regionGrammar = self.lineRegion
        elif ( "iline" == report_unit ):
            regionGrammar = self.indentedLineRegion
        elif ( "policyMap" == report_unit ):
            regionGrammar = self.policyMapRegion
        elif ( "vlan" == report_unit ):
            regionGrammar = self.vlanRegion
        elif ( "config" == report_unit ):
            regionGrammar = self.configFileRegion
        else:
            printf("Unknown Grammar error!\n")
            sys.exit(-1)

        return regionGrammar

    ## Extract all occurrences of strings in the language of the 
    #   production from the text.
    # 
    #  @param grammar The productionObject, this should be a 
    #   production reference
    #  @param text    The string from which to extract occurrences
    #  @param match   Not sure what this is doing or why necessary
    #  @return a list of strings in the language of this production 
    #     from the text.
    #  @note What about Exceptions?  Should we be returning tokens 
    #     instead so that we can support highlighting, etc?
    def getOriginalText( self, grammar, text, match ):
        regions = []
        matchExpr = originalTextFor( grammar ).scanString(text)
        for tokens, s, e in matchExpr:
            if match == None:
                regions.append( tokens[0].strip() )
            elif match in tokens[0]:
                regions.append( tokens[0].strip() )
        return regions

    ## Take a parse object and put it into a canoncial 
    #   parse tree representation.  Rethink this interface in terms of 
    #   the XUTools (space and time complexity) and also in terms of 
    #   extant libraries such as libaugeas.
    #
    #  @param parse_tree_list The list of parse trees that resulted 
    #    from parsing
    #  @return the normalized parse tree
    #  @note  think about how to do this more generally in a language-agnostic way
    @staticmethod
    def normalizeParseTree( parse_tree_list ):
        ntree = { 'id':None,
                  'type':None,
                  'children':[] }
        for item in parse_tree_list:
            if isinstance( item, types.ListType ) and len(item) > 0:
                if ( 'interface' == item[0] ):
                    ntree['type'] = 'interface'
                    ntree['id'] = item[1].strip()
                elif ( 'crypto' == item[0] ):
                    ntree['type'] = 'crypto'
                    ntree['id'] = item[1].strip()
                elif ( isinstance( item[0], types.ListType ) ):
                    for subtree_list in item:
                        nsubtree = CiscoIOSParser.normalizeParseTree( subtree_list )
                        ntree['children'].append( nsubtree );
            elif isinstance( item, types.StringType ):
                if ( '\n' != item and ' ' != item ):
                    ntree['type'] = 'line'
                    ntree['value'] = item.strip()                    
        return ntree
    
# The SubsetCParser class is used to parse C files.  This is directly taken
#   from a subset-C parser by Paul McGuire (c) 2010 that is available on 
#   t
# This is a subset-C parser taken from
#   Paul McGuire, 2010
#
# @note The grammar reference is 'cspec'
class SubsetCParser():
    
    LPAR,RPAR,LBRACK,RBRACK,LBRACE,RBRACE,SEMI,COMMA = map(Suppress, "()[]{};,")
    INT = Keyword("int")
    CHAR = Keyword("char")
    WHILE = Keyword("while")
    DO = Keyword("do")
    IF = Keyword("if")
    ELSE = Keyword("else")
    RETURN = Keyword("return")
    NAME = Word(alphas+"_", alphanums+"_")
    integer = Regex(r"[+-]?\d+")
    char = Regex(r"'.'")
    string_ = dblQuotedString
        
    TYPE = Group((INT | CHAR ) + ZeroOrMore("*"))
    expr = Forward()
    operand = NAME | integer | char | string_
    expr << (operatorPrecedence(operand, 
                                     [
                (oneOf('! - *'), 1, opAssoc.RIGHT),
                (oneOf('++ --'), 1, opAssoc.RIGHT),
                (oneOf('++ --'), 1, opAssoc.LEFT),
                (oneOf('* / %'), 2, opAssoc.LEFT),
                (oneOf('+ -'), 2, opAssoc.LEFT),
                (oneOf('< == > <= >= !='), 2, opAssoc.LEFT),
                (Regex(r'=[^=]'), 2, opAssoc.LEFT),
                ]) + 
                  Optional( LBRACK + expr + RBRACK | 
                            LPAR + Group(Optional(delimitedList(expr))) + RPAR )
                  )
    
    stmt = Forward()
    
    ifstmt = IF - LPAR + expr + RPAR + stmt + Optional(ELSE + stmt)
    whilestmt = WHILE - LPAR + expr + RPAR + stmt
    dowhilestmt = DO - stmt + WHILE + LPAR + expr + RPAR + SEMI
    returnstmt = RETURN - expr + SEMI
    
    stmt << Group( ifstmt |
                        whilestmt |
                        dowhilestmt |
                        returnstmt | 
                        expr + SEMI |
                        LBRACE + ZeroOrMore(stmt) + RBRACE |
                        SEMI)
    
    vardecl = Group(TYPE + NAME + Optional(LBRACK + integer + RBRACK)) + SEMI

    arg = Group(TYPE + NAME)
    body = ZeroOrMore(vardecl) + ZeroOrMore(stmt)

    ## Production for C functions, reference is 'function'
    fundecl = Group(TYPE + NAME + LPAR + Optional(Group(delimitedList(arg))) + RPAR +
                         LBRACE + Group(body) + RBRACE)
    decl = fundecl | vardecl
    program = ZeroOrMore(decl)
    
    program.ignore(cStyleComment)

    ## Given a parse tree node for a text region, return the corresponding ID
    #  @param[in]     subtree_parse the parse tree node
    #  @param[in]     region_type   the type of the node
    #  @param[in,out] subtree_idx   a node index determined by a tree traversal
    #  @return a string that encodes the region ID
    #  @exception UnrecognizedProductionRef the production reference is not recognized
    #  @exception MalformedParseTree   the parse tree has an unexpected format
    def getRegionID( self, subtree_parse, region_type, subtree_idx ):
        result = None
        if "function" == region_type:
            # need better checks here for valid subtree parse as input
            result = subtree_parse[0][1]
        else:
            print "unrecognized region type: " + region_type
            sys.exit(-1)

        return result

    ## Retrieve a production by reference
    #  @param[in] report_unit  This is the production reference
    #  @return the production
    #  @exception UnrecognizedProductionRef    
    def getGrammarForUnit( self, report_unit ):
        if ( "function" == report_unit ):
            regionGrammar = self.fundecl
        else:
            print "Unknown Grammar error!\n"
            print report_unit
            sys.exit(-1)

        return regionGrammar
        
## The NVDParser class is used to parse XML documents encoded 
#    in the National Vulnerability Database XML format.
#
#  @note The grammar reference is 'nvd' 
class NVDParser():

    scoreStart, scoreEnd = makeXMLTags("cvss:score")
    ## Production for score elements, reference is 'score'
    scoreRegion = scoreStart + SkipTo(MatchFirst(scoreEnd)) + Group(scoreEnd)

    entryStart, entryEnd = makeXMLTags("entry")
    ## Production for entry elements, reference is 'entry'
    entryRegion = entryStart + SkipTo(MatchFirst(entryEnd)) + Group(entryEnd)

    nvdStart, nvdEnd = makeXMLTags("nvd")
    ## Production for the entire NVD, reference is 'nvd'
    nvdRegion = nvdStart + Group( ZeroOrMore(Group(entryRegion)) ) + Group(nvdEnd)
    
    ## Take a parse object and put it into a canonical
    #   parse tree representation.  Rethink this interface in terms of 
    #   the XUTools (space and time complexity) and also in terms
    #   of extant libraries such as libaugeas.
    #
    #  @param parse_tree_list The list of parse trees that resulted
    #   from parsing
    #  @return the normalized parse tree
    #  @note  think about how to do this more generally in a language-agnostic way.
    @staticmethod
    def normalizeParseTree( parse_tree_list ):
        ntree = { 'id':None,
                  'type':None,
                  'children':[] }
        for item in parse_tree_list:
            if isinstance( item, types.ListType ):
                if ( 'id' == item[0] ):
                    ntree['id'] = item[1]
                elif ( isinstance( item[0], types.ListType ) ):
                    for subtree_list in item:
                        nsubtree = NVDParser.normalizeParseTree( subtree_list )
                        ntree['children'].append( nsubtree )
            elif isinstance( item, types.StringType ):
                if ( 'entry' == item ):
                    ntree['type'] = item
                elif ( 'nvd' == item ):
                    ntree['type'] = item
                else:
                    ntree['value'] = item
        return ntree

    ## Given a parse tree node for a text region, return the corresponding ID
    #  @param[in]     subtree_parse the parse tree node
    #  @param[in]     region_type   the type of the node
    #  @param[in,out] subtree_idx   a node index determined by a tree traversal
    #  @return a string that encodes the region ID
    #  @exception UnrecognizedProductionRef the production reference is not recognized
    #  @exception MalformedParseTree   the parse tree has an unexpected format    
    def getRegionID( self, subtree_parse, region_type, subtree_idx ):
        result = None
        if "entry" == region_type:
            if "id" == subtree_parse[1][0] and "entry" == subtree_parse[0]:
                result = subtree_parse[1][1]
            else:
                print "Unrecognized parse tree for entry: " + str(subtree_parse)
                sys.exit(-1)
        elif "score" == region_type:
            result = str(subtree_idx + 1)
        else:
            print "unrecognized region type: " + region_type
            sys.exit(-1)

        return result

    ## Retrieve a production by reference
    #  @param[in] report_unit  This is the production reference
    #  @return the production
    #  @exception UnrecognizedProductionRef
    def getGrammarForUnit( self, report_unit ):
        if ( "entry" == report_unit ):
            regionGrammar = self.entryRegion
        elif ( "nvd" == report_unit ):
            regionGrammar = self.nvdRegion
        elif ( "score" == report_unit ):
            regionGrammar = self.scoreRegion
        else:
            printf("Unknown Grammar error!\n")
            sys.exit(-1)
        
        return regionGrammar

    ## Extract all occurrences of strings in the language
    #   of the production from the text.
    #
    #  @param grammar The productionObject, this should be 
    #    a production reference
    #  @param text The string from which to extract occurrences
    #  @param match Not sure what this is doing
    #  @return a list of strings in the language of this production 
    #    from the text
    #  @note What about Exceptions?  Should we be returning tokens 
    #    instead so that we can support highlighting, etc?    
    def getOriginalText( self, grammar, text, match ):
        regions = []
        matchExpr = originalTextFor( grammar ).scanString(text)
        for tokens, s, e in matchExpr:
            if match == None:
                regions.append( tokens[0].strip() )
            elif match in tokens[0]:
                regions.append( tokens[0].strip() )
        return regions


    

    
