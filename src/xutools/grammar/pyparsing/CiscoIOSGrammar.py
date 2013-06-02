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
class CiscoIOSGrammar():
    
    classMapStart = LineStart() + Group(Literal("class-map") + restOfLine) + \
        LineEnd()
    classMapStart.leaveWhitespace()

    policyMapStart = LineStart() + Group(Literal("policy-map") + restOfLine) + \
        LineEnd()
    policyMapStart.leaveWhitespace()

    vlanStart = LineStart() + Group(Literal("vlan") + restOfLine) + LineEnd()
    vlanStart.leaveWhitespace()

    interfaceStart = LineStart() + Literal("interface") + restOfLine.setResultsName("label") + \
        LineEnd()
    interfaceStart.leaveWhitespace()

    cryptoStart = LineStart() + Group(Literal("crypto") + restOfLine) + \
        LineEnd()
    cryptoStart.leaveWhitespace()

    router_start = LineStart() + Group(Literal('router') + restOfLine) + \
        LineEnd()
    router_start.leaveWhitespace()

    address_family_start = LineStart() + Group(ZeroOrMore(Literal(' ')) + \
        Keyword('address-family', ) + restOfLine) + LineEnd()
    address_family_start.leaveWhitespace()

    address_family_end = LineStart() + Group(ZeroOrMore(Literal(' ')) + \
        Keyword('exit-address-family')) + LineEnd()
    address_family_end.leaveWhitespace()

    blockEnd = LineStart() + Literal("!") + ZeroOrMore(LineEnd())
    blockEnd.leaveWhitespace()

    indentedBlockEnd = LineStart() + ZeroOrMore(Literal(' ')) + Literal("!") + \
        ZeroOrMore(LineEnd())
    indentedBlockEnd.leaveWhitespace()

    ## This should not be used, instead use the builtin:line reference
    lineRegion = restOfLine.setWhitespaceChars(' \t') + Optional(Literal("\n"))
    lineRegion.leaveWhitespace()

    ## This should not be used, instead use builtin:line reference
    indentedLineRegion = LineStart() + " " + restOfLine + LineEnd()
    indentedLineRegion.leaveWhitespace()

    ## IOS address family
    address_family_region = address_family_start + \
        Group(ZeroOrMore(Group(indentedLineRegion)))  # + address_family_end
    address_family_region.leaveWhitespace()

    ## Production for Cisco IOS VLANs, reference is 'vlan'
    vlanRegion = vlanStart + Group(OneOrMore(Group(indentedLineRegion))) + \
        Group(blockEnd)
    vlanRegion.leaveWhitespace()

    ## Production for Cisco IOS interfaces, reference is 'interface'
    interfaceRegion = interfaceStart + \
        Group(OneOrMore(Group(indentedLineRegion))) + Group(blockEnd)
    interfaceRegion.leaveWhitespace()

    ## Production for Cisco IOS crypto blocks, reference is 'crypto'
    cryptoRegion = cryptoStart + Group(ZeroOrMore(Group(indentedLineRegion))) + \
        Group(blockEnd)
    cryptoRegion.leaveWhitespace()

    ## Production for Cisco IOS router blocks, reference is 'router'
    router_region = router_start + Group(ZeroOrMore(Group(indentedLineRegion))) + \
        Group(blockEnd)
    router_region.leaveWhitespace()

    ## Production for Cisco IOS class-maps, reference is 'classmap'
    classMapRegion = classMapStart + \
        Group(ZeroOrMore(Group(indentedLineRegion))) + Optional(Group(blockEnd))
    classMapRegion.leaveWhitespace()

    ## Production for Cisco IOS policy-maps, reference is 'policymap'
    policyMapRegion = policyMapStart + \
        Group(ZeroOrMore(Group(indentedLineRegion))) + Optional(Group(blockEnd))
    policyMapRegion.leaveWhitespace()

    ## Production for Cisco IOS config files, the entire file. reference is 'config'
    configFileRegion = Group(OneOrMore(Group(interfaceRegion) | \
        Group(cryptoRegion) | Group(vlanRegion) | Group(classMapRegion) | \
        Group(policyMapRegion)) | Group(address_family_region))
    configFileRegion.leaveWhitespace()

    GRAMMAR_NAME = "ios"
    
    CONFIG = GRAMMAR_NAME + ":" + "config"
    INTERFACE = GRAMMAR_NAME + ":" + "interface"
    
    # Given a language name, get the grammar that specifies strings in 
    #  that language
    # 
    # @param[in] language_name
    # @exception UndefinedLanguageName if the language name was not found
    def get_grammar(self, language_name):
        if ( self.CONFIG == language_name ):
            return self.configFileRegion
        elif ( self.INTERFACE == language_name ):
            return self.interfaceRegion
        else:
            raise UndefinedLanguageName("Unable to find language name:" + language_name +\
                                            " in CiscoIOSGrammar")
    # Get all language names
    #
    # @return an array of all language names defined by the grammar
    def get_language_names(self):
        language_names = [ self.CONFIG, self.INTERFACE ]
        return language_names
    
    def get_label_for_match(self, language_name, match, match_idx):
        label = None
        if ( "label" in match ):
            label = match["label"].strip()
        else:
            label = str(match_idx)
        return label

    ## Take a parse object and put it into a canoncial 
    #   parse tree representation.  This method should go bye-bye.
    #
    #  @param parse_tree_list The list of parse trees that resulted 
    #    from parsing
    #  @return the normalized parse tree
    #  @note  think about how to do this more generally in a language-agnostic way
    def normalize_parse_tree( self, parse_tree_list ):
        ntree = { 'id':None,
                  'type':'ios:config',
                  'value':'root',
                  'children':[] }
        for item in parse_tree_list:
            if isinstance( item, types.ListType ) and len(item) > 0:
                if ( 'interface' == item[0] ):
                    ntree['type'] = 'ios:interface'
                    ntree['id'] = item[1].strip()
                    ntree['value'] = ntree['id']
                elif ( 'crypto' == item[0] ):
                    ntree['type'] = 'crypto'
                    ntree['id'] = item[1].strip()
                    ntree['value'] = ntree['id']
                elif ( isinstance( item[0], types.ListType ) ):
                    #ntree['type'] = ''
                    #ntree['id'] = ''
                    #ntree['value'] = ''
                    for subtree_list in item:
                        nsubtree = self.normalize_parse_tree( subtree_list )
                        ntree['children'].append( nsubtree );
            elif isinstance( item, types.StringType ):
                if ( '\n' != item and ' ' != item ):
                    ntree['type'] = 'builtin:line'
                    ntree['value'] = item.strip()                    
        return ntree
