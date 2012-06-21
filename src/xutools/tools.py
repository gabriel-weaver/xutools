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
import parsers
import re
import sys
import types
from distances import ZhangShashaTreeDist as TD

## @package xutools.tools
#    This module contains classes for each of our XUTools.  Currently
#      this means xugrep, xuwc, and xudiff.
# 
#    We may want to break each of these tools out into separate files.
#      I am not sure about this yet.


## The XUGrep class implements xugrep.  
class XUGrep():

    ## Method used by the command line interface.  
    #  
    #  @param[in] xpath The xupath query that specifies a result set
    #  @param[in] file_paths The files from which to extract results
    #  @return the xugrep report
    #  @note What about Exceptions?
    @staticmethod
    def xugrep_main( xpath, file_paths ):

        xugrep = XUGrep()
        reports = {}

        for file_path in file_paths:
            fp = open( file_path, 'r' )
            text = fp.read()
            fp.close()
            
            report = {}
            report['result_forest'] = [ text ]
            report['tree_ids'] = [ file_path.replace('.','_') ]
            report['tree_types'] = [ "file_path" ]
            report['re_matches'] = []
            reports[ file_path ] = xugrep.xugrep( xpath, report )

        return reports

    ## Method used to print reports to stdout
    # 
    #  @param[in] reports The xugrep reports for each of the files
    #  @param[in] r2 specifies how regions should be displayed.  This
    #                parameter needs more mediation
    #  @return nothing
    #  @note What about exceptions?
    @staticmethod
    def output_reports( reports, r2 ):
        for file_path in reports.keys():
            report = reports[ file_path ]

            if ( 'LE' == r2 ):
                print "\t".join( report['tree_types'] + ['region'] ) 
            i = 0
            for tree in report['result_forest']:
                id = report['tree_ids'][i]
                id = id.replace(".", "\t")
                region = tree
                if ( 'LE' == r2 ):
                    region = tree.replace('\n', '/n')
                    print "\t".join( [id, region] )
                else:
                    #print id + "\n" + region + "\n"
                    print region
                i = i + 1

    ## Method that actually processes the xupath query and
    #    generates a report
    #  @param self 
    #  @param[in] xPath  The xupath query that specifies results
    #  @param[in] report The blank report.  This should be an in/out param 
    #  @return  The xugrep report that contains matches that are in
    #    the language of the xupath query.
    #  @note What about exceptions            
    def xugrep( self, xPath, report ):
        result = []
        parser = parsers.XPathParser()
        parses = parser.xPath.scanString( xPath )
        for p, s, e in parses:
            result.append(p)
        report = self.process_xpath( result[0].path, "", report )
        return report

    ## Action to take a node of type 'xpath' when generating an xugrep report
    #  @param self
    #  @param[in] xpath The 'xpath' parse-tree node to visit
    #  @param[in] indent the current indentation level within the parse tree
    #  @param[in] report The current xugrep report.  This should really be 
    #              an in,out param
    #  @return The xugrep report that contains matches that are in the
    #     language of the xupath query.
    #  @precondition If the 'xpath' node is None or empty, then we've reached
    #              a base case on recursion.  Just return the report.
    #  @note What about exceptions?
    def process_xpath( self, xpath, indent, report ):
        if xpath == None or len(xpath) == 0:
            return
        report = self.process_step( xpath.current_step, indent + " ", report )
        report = self.process_next_steps( xpath.next_steps, indent + " ", report )
        return report

    ## Action to take a node of type 'step' when generating an xugrep report
    #  @param self
    #  @param[in] step The 'step' parse-tree node to visit
    #  @param[in] indent The current indentation level within the parse tree
    #  @param[in] report The current xugrep report.  This should really be 
    #              an in,out param
    #  @return An xugrep report that contains a subset of the current 
    #    result forest that is in the language of this 'step'.
    #  @precondition If the 'step' node is None or empty, then we've
    #    reached a base case on recursion.  Just return the report.
    #  @note What about exceptions?
    def process_step( self, step, indent, report ):
        if step == None or len(step) == 0:
            return report

        report = self.process_cf_match( step.cf_match, indent + " ", report )
        report = self.process_predicate( step.predicate, indent + " ", report )
        return report

    ## Action to take a node of type 'next_steps' when generating an xugrep
    #   report.
    #  @param self
    #  @param[in] next_steps The 'next_steps' parse-tree node to visit
    #  @param[in] indent The current indentation level within the parse tree
    #  @param[in] report The current xugrep report.  This should really be an
    #                      in,out param
    #  @return An xugrep report that contains a subset of the current result
    #                      forest that is in the language of these
    #                      next steps.
    #  @precondition  If the 'next_steps' node is None or empty, then
    #     we've reached a base case on recursion.  Just return the report.
    #  @note  What about exceptions?
    def process_next_steps( self, next_steps, indent, report):
        if next_steps == None or len(next_steps) == 0:
            return report

        for step in next_steps:
            if step != '/' and step != '//':
                report = self.process_step( step, indent, report )
        return report

    ## Action to take on a parse tree node of type 'cf_match' when we generate
    #  an xugrep report.
    #
    #  @param self
    #  @param[in] cf_match The 'cf_match' parse-tree node to visit
    #  @param[in] indent The current indentation level within the parse tree
    #  @param[in] report The current xugrep report.  This should really be
    #                      an in,out param
    #  @return The xugrep report that results when we filter out the
    #    result set according to those that match the grammar reference
    #    associated with this 'cf_match' node. 
    #  @precondition If the node is None or empty, then we've reached a base case on recursion
    #    just return the report.
    #  @note What about exceptions
    def process_cf_match( self, cf_match, indent, report ):
        if cf_match == None or len(cf_match) == 0:
            return report

        parser = None
        production = None
        [ gname, pname ] = cf_match[0].split(':')
        parser = self.get_parser( gname )
        production = parser.getGrammarForUnit( pname )

        # Loop through each tree in the forest and scanString
        #  using the grammar for this production_name
        #  get the resultant result forest        
        new_result_forest = []
        new_tree_ids = []

        i = 0
        for text_tree in report['result_forest']:
            # Get the ids
            old_id = None
            if ( len( report['tree_ids'] ) > 0 ):
                old_id = report['tree_ids'][i]

            match_forest = production.scanString( text_tree )

            subtree_idx = 0
            for subtree, s, e in match_forest:
                new_id = parser.getRegionID( subtree, pname, subtree_idx )
                if old_id != None:
                    new_id = old_id + "." + new_id
                new_tree_ids.append( new_id )
                subtree_idx = subtree_idx + 1

            # Get the matching trees
            match_forest = originalTextFor( production ).scanString( text_tree )
            for subtree, s, e in match_forest:
                new_result_forest.append( subtree[0].strip() )

            i = i + 1
   
        report['result_forest'] = new_result_forest
        report['tree_ids'] = new_tree_ids
        report['tree_types'].append( cf_match[0] )
        return report

    # Action to take on a parse tree node of type 're_match' when we generate
    #  an xugrep report.
    #
    # @param     self
    # @param[in] re_match The 're_match' parse-tree node to visit
    # @param[in] indent   The current indentation level within the parse tree
    # @param[in] report   The current xugrep report.  This should really be an
    #                       in,out param
    # @return The xugrep report that results when we filter out the
    #  current result set according to those that match the regular
    #  expression associated with this 're_match' node.
    # @precondition  If the node is None or empty, then we've reached
    #  a base case, just return the report.
    # @note What about exceptions?
    def process_re_match( self, re_match, indent, report ):
        if re_match == None or len(re_match) == 0:
            return result_forest
        
        regexp = None
        if (len(re_match) != 1):
            regexp = re_match[2]
        else:
            regexp = re_match[0]

        pattern = re.compile( regexp )

        # Loop through each tree in the forest and keep the
        #  trees that have a match
        new_result_forest = []
        new_tree_ids = []
        new_re_matches = []

        i = 0
        for text_tree in report['result_forest']:
            matches = pattern.findall( text_tree ) 
            if ( None != matches and len(matches) > 0 ):
                new_result_forest.append( text_tree.strip() )
                new_tree_ids.append( report['tree_ids'][i] )
                new_re_matches.append( matches )
            i = i + 1
        
        report['result_forest'] = new_result_forest
        report['tree_ids'] = new_tree_ids
        report['re_matches'] = new_re_matches
        return report

    ## Action to take on a parse tree node of type 'predicate' when we
    #   generate an xugrep report
    #
    #  @param self
    #  @param[in] predicate  The 'predicate' parse-tree node to visit
    #  @param[in] indent The current indentation level within the parse tree
    #  @param[in] report The current xugrep report.  This should
    #   really be an in,out param.
    #  @return The xugrep report that results when we filter out the current
    #   result set according to those that match the predicate.
    #  @precondition If the node is None or empty, then we've reached 
    #   a base case, just return the report
    #  @note What about exceptions?
    def process_predicate( self, predicate, indent, report ):
        if predicate == None or len(predicate) == 0:
            return report
        report = self.process_re_match( predicate.re_match, indent + " ", report )
        report = self.process_next_steps( predicate.next_steps, indent + " ", report )
        return report
    
    ## Retrieve a grammar by reference.  I think that this should
    #   really live in the Parser module.
    #  
    #  @param[in] gname This is the grammar reference
    #  @return the Parser for the given grammar reference
    #  @exception UnrecognizedGrammarRef the grammar reference is not
    #   recognized
    def get_parser( self, gname ):
        if ( 'tei' == gname ):
            parser = parsers.TEILiteParser()
        elif ('ios' == gname ):
            parser = parsers.CiscoIOSParser()
        elif ('nvd' == gname ):
            parser = parsers.NVDParser()
        elif ('cspec' == gname ):
            parser = parsers.SubsetCParser()
        elif ('builtin' == gname ):
            parser = parsers.BuiltinParser()
        elif ('script' == gname ):
            parser = parsers.ScriptParser()
        else:
            print "Parser not yet implemented!"        
            return -1
        return parser

## The XUWc class implements xuwc.  This class needs to be renamed.
class XUWc():
    
    ## Method used by the command line interface
    #  
    # @param[in] xpath The xupath query that specifies a result set to 
    #   count
    # @param[in] file_paths The files from which to extract results
    # @param[in] wc_params The parameters specific to wc.  
    # @details  wc_params['count_type']    Count occurrences of
    #  strings in the language of this grammar production reference.
    # @details  wc_params['count_regexp']  Count occurrences of 
    #  strings in the language of this regular expression
    # @details  wc_params['context_type']  Report counts relative to 
    #  strings in the language of this grammar production reference.
    # @details  wc_params['context_regexp'] Report counts relative to 
    #  strings in the language of this regular expression reference
    # @return the xuwc report
    # @note What about Exceptions?
    @staticmethod
    def xuwc_main( xpath, file_paths, wc_params ):
        xuwc = XUWc()
        reports = XUGrep.xugrep_main( xpath, file_paths )
        wc_reports = xuwc.get_wc_reports( reports, wc_params )
        return wc_reports

    ## Method used to print reports to stdout
    # 
    #  @param[in] wc_reports The xuwc reports for each of the files.
    #  @param[in] wc_params  The parameters specific to wc
    #  @return None
    #  @exception CountTypeUndefined
    @staticmethod
    def output_reports( wc_reports, wc_params ):

        num_context_regions = 0
        total_count = 0

        counted_unit = None
        if wc_params['count_type'] != None:
            counted_unit = wc_params['count_type']
        elif wc_params['count_regexp'] != None:
            counted_unit = wc_params['count_regexp']
        else:
            print "Either count_type or count_regexp must be defined."
            return -1

        for file_path in wc_reports.keys():
            wc_report = wc_reports[ file_path ]

            for context_region_id in wc_report.keys():
                if wc_report[context_region_id] > 0:  #if region has no hits, no count
                    num_context_regions = num_context_regions + 1
                total_count = total_count + wc_report[context_region_id]
                print "\t".join( [ str(wc_report[context_region_id]), counted_unit, context_region_id.replace("_",".") ] )
        
        print "\t".join( [ str(total_count), counted_unit, str(num_context_regions), wc_params['context_type'], "TOTAL"] )


    ## Method that actually generates the wc reports for each of the
    #  input files
    #  @param self
    #  @param[in] reports The xugrep reports to process
    #  @param[in] wc_params 
    #  @precondition If neither 'count_regexp' or 'count_type' are
    #     set, then we count the last item in the xupath. 
    #  @precondition If neither 'context_regexp' or 'context_type' are 
    #     set, then we report matches in terms of the first type.
    #  @return the updated wc_reports
    #  @note  What about Exceptions?
    def get_wc_reports( self, reports, wc_params ):
        wc_reports = {}
        for file_path in reports.keys():
            report = reports[file_path]
            # fill in the defaults if count and contexts not specified
            if None == wc_params['count_regexp'] and None == wc_params['count_type']:
                wc_params['count_type'] = report['tree_types'][ len( report['tree_types'] ) - 1  ]
            if None == wc_params['context_regexp'] and None == wc_params['context_type']:
                wc_params['context_type'] = report['tree_types'][0]

            wc_reports[file_path] = self.get_wc_report( report, wc_params )
        return wc_reports

    ## Method that computes a wc_report 
    #  @param self
    #  @param[in] report     The xugrep report to process
    #  @param[in] wc_params  
    #  @exception NotYetImplemented Regular expression as context is
    #    not implemented
    #  @exception InvalidContextException the context must be in the
    #    xupath
    #  @return wc report
    def get_wc_report( self, report, wc_params ):
        wc_report = {}
        if wc_params['context_regexp'] != None:
            # re_context case
            print "Regular expression as context not implemented"
            return -1
        else:
            # context case
            if not (wc_params['context_type'] in report['tree_types']):
                print "Context type must be in the XPath query"
                return 0
            
            context_type_idx = report['tree_types'].index( wc_params['context_type'] )            

            if wc_params['count_regexp'] != None:
                if context_type_idx != len(report['tree_types']) - 1 :
                    print "Regexp match must be done on last context type."
                    return -1

                i = 0
                for tree in report['result_forest']:
                    context_region_id = self.get_id_for_idx( context_type_idx, report['tree_ids'][i] )
                    if None == context_region_id:
                        print "Error resolving region id from idx.  Crash and burn!!! ahhh"
                        return -1
                    
                    regexp = wc_params['count_regexp']
                    pattern = re.compile( regexp )
                    matches = pattern.findall( tree )
                    wc_report[ context_region_id ] = len( matches )
                    i = i + 1

            elif wc_params['count_type'] == 'builtin:byte':
                if context_type_idx != len(report['tree_types']) - 1 :
                    print "byte match must be done on last context type."
                    return -1

                i = 0
                for tree in report['result_forest']:
                    context_region_id = self.get_id_for_idx( context_type_idx, report['tree_ids'][i] )
                    if None == context_region_id:
                        print "Error resolving region id from idx.  Crash and burn!!! ahhh"
                        return -1
                    wc_report[ context_region_id ] = len(tree)  # for chars .decode('utf-8') assuming utf-8 input
                    i = i + 1

            elif wc_params['count_type'] == 'builtin:character':
                if context_type_idx != len(report['tree_types']) - 1 :
                    print "Character match must be done on last context type."
                    return 0

                i = 0
                for tree in report['result_forest']:
                    context_region_id = self.get_id_for_idx( context_type_idx, report['tree_ids'][i] )
                    if None == context_region_id:
                        print "Error resolving region id from idx.  Crash and burn!!! ahhh"
                        return -1
                    wc_report[ context_region_id ] = len(tree.decode('utf-8'))  #assuming unicode input
                    i = i + 1

            elif wc_params['count_type'] == 'builtin:word':
                if context_type_idx != len(report['tree_types']) - 1 :
                    print "Word match must be done on last context type."
                    return 0

                i = 0
                for tree in report['result_forest']:
                    context_region_id = self.get_id_for_idx( context_type_idx, report['tree_ids'][i] )
                    if None == context_region_id:
                        print "Error resolving region id from idx.  Crash and burn!!! ahhh"
                        return -1
                    words = tree.split(None)
                    wc_report[ context_region_id ] = len(words) 
                    i = i + 1
            
            #elif wc_params['count_type'] == 'builtin:line':
            #    if context_type_idx != len(report['tree_types']) - 1 :
            #        print "Regexp match must be done on last context type."
            #        sys.exit(0)
            #    print "Implement word counting here."
            
            elif wc_params['count_type'] in report['tree_types']:
                count_type_idx = report['tree_types'].index( wc_params['count_type'] )
                if count_type_idx < context_type_idx:
                    print "Count type " + wc_params['count_type'] + " is not contained in context type " + wc_params['context_type']
                    return -1
                counted_region_ids = self.get_ids_for_idx( count_type_idx, report['tree_ids'] )
                for counted_region_id in counted_region_ids:
                    context_region_id = self.get_id_for_idx( context_type_idx, counted_region_id )
                    if ( not context_region_id in wc_report.keys() ):
                        wc_report[ context_region_id ] = 0
                    wc_report[ context_region_id ] = wc_report[context_region_id] + 1
            else:
                print "Sorry we can't help you.  Stay tuned."
                return -1

        return wc_report

    ## Prune a parse-tree node ID to the provided level
    #  @param self
    #  @param[in] level     The level at which to report results
    #  @param[in] region_id The parse-tree node ID to prune
    #  @precondition If the level is larger than the number of levels
    #    in the region_id, then return None
    #  @return The parse-tree node ID pruned to a specified level
    #  @note This is usually called on elements of the 'tree_ids' list
    #    within the xugrep report.  
    def get_id_for_idx(self, level, region_id):
        p = region_id.split(".")
        if level > len(p) - 1:
            return None
        else:
            return ".".join( p[0:level + 1] )
    
    ## Prune a list of parse-tree node IDs to the provided level.
    #  @param self
    #  @param[in] level       The level at which to prune results
    #  @param[in] region_ids  The list of region_ids to prune
    #  @precondition If one of the region_ids cannot be pruned, then
    #    it will not be included in the result list
    #  @postcondition We return a set of valid IDs.  Therefore, two
    #    parse-tree node IDs that are originally distinct may prune to
    #    the same ID.  This same ID occurs only once in the return
    #    list.
    #  @return The pruned parse-tree node ids
    def get_ids_for_idx(self, level, region_ids):
        result = []
        for region_id in region_ids:
            new_id = self.get_id_for_idx( level, region_id )
            if new_id != None:
                if not new_id in result:
                    result.append( new_id )
        return result

## The XUDiff class implements xudiff. 
class XUDiff():
    
    ## Node-visitor action that sets the identifier of the parse-tree node
    #   to the position, as determined by a traversal.  The
    #   Zhang & Shasha Tree Editing Distance algorithm uses a 
    #   postorder traversal.
    #  @param[in] node    The parse-tree node to process
    #  @param[in] params  Parameters to update during the tree traversal.
    #  @return The updated node and parameters.  Really both node and
    #   params should turn into in,out parameters
    #  @note Do we ever use the 'id_attr' attribute elsewhere?  This
    #   may be unnecessary satellite data
    @staticmethod
    def set_position_as_id( node, params ):
        node['id_attr'] = node['id']
        node['id'] = params['pos']
    
        # The node value is either the id_attr or the line
        #  for Cisco IOS at least
        if 'value' in node.keys():
            node['label'] = node['value']
            del node['value']
        elif node['id_attr'] != None:
            node['label'] = node['id_attr']
        # we do not delete the id_attr node
        else:
            node['label'] = None
            
        params['pos'] = params['pos'] + 1
        return [ node, params ]
    
    ## Node-visitor action that computes a 'pos2type' mapping
    #   from a traversal position to a node type.  
    #  @param[in] node    The parse-tree node to process
    #  @param[in] params  Parameters to update during the tree
    #   traversal.  Here, we update params['pos2type'].
    #  @return The updated parameters.  The node is unaffected.  
    #   really, params should be an in,out parameter
    @staticmethod
    def compute_type_list( node, params ):
        if None != node['type']:
            params['pos2type'].append( node['type'] )
        else:
            params['pos2type'].append("")

        return [ node, params ]

    ## Node-visitor action that computes a reference string for
    #   every node in the parse tree.  This interface needs to be
    #   rethought.
    #  @param[in] node  The parse-tree node for which to generate a
    #     ref
    #  @param[in] params Parameters used to help compute the
    #   reference, in this case, we make use of the params['stack'] 
    #   satellite data in order to understand location within the
    #   parse tree
    #  @return The updated node, which now has 'ref' satellite data
    #   associated with it.  Params are also updated.  Really, both
    #   node and params should be in,out parameters.
    @staticmethod
    def compute_references( node, params ):
        refKey = params[ 'refKey' ]
        if None != node[ refKey ]:
            params['stack'].append( node[ refKey ] )
        else:
            params['stack'].append( "_" )

        node['ref'] = ".".join( params['stack'] )
        return [ node, params ]

    ## Node-visitor action that computes a 'pos2ref' mapping
    #   from a traversal position to a node type.
    #  @param[in] node    The parse-tree node whose 'ref' we grab.
    #  @param[in] params  The parameters used to update during the 
    #   tree traversal.  Here, we update params['pos2ref']
    #  @return The updated parameters.  The node is unaffected.
    #   Really, params should be an in,out parameter and we should 
    #   return None
    @staticmethod
    def compute_reference_list( node, params ):
        params['pos2ref'].append( node['ref'] )
        return [ node, params ]
    
    ## Method used to report an edit script from the dynamic
    #    programming matrices computed by Zhang and Shasha.  This edit
    #    script is annotated with grammar-specific information
    #
    #  @param[in] i The largest 'version 1' leaf position (postorder traversal)
    #  @param[in] j The largest 'version 2' leaf position (preorder traversal)
    #  @param[in] small_leaf1   
    #  @param[in] small_leaf2 
    #  @param[in] params Parameters necessary to output an edit script
    #  @details  params['pos2types0'] 
    #  @details  params['pos2types1']
    #  @details  params['pos2refs0']
    #  @details  params['pos2refs1']
    #  @return   An edit script to output
    #  @exception UnrecognizedEditOperation
    @staticmethod
    def output_edit_script( i, j, small_leaf1, small_leaf2, params ):
        update_script = []
        delete_script = []
        insert_script = []
        edit_script = [] 

        #        i = len( params['l0'] )
        #        j = len( params['l1'] )

        while True:
            if i == 0 or j == 0:
                break
            #            elif i == 0 and j != 0:
            #                i = 1
            #            elif i != 0 and j == 0:
            #    j = 1

            operation = params['edit_ops'][ i, j ]
            current_dist = params['forest_dist'][ i, j ]
            
            type1 = params['pos2types0'][0][i - 1]
            type2 = params['pos2types1'][0][j - 1]
            ref1 = params['pos2refs0'][0][i - 1]
            ref2 = params['pos2refs1'][0][j - 1]

            if operation == TD.UPDATE:
                edit_cost = params['update_edit_cost'][ i - 1, j - 1 ]
                edit_script.append( "U " + str([current_dist, edit_cost] )  + " " + ref1 + " (" + type1 + ") -> " + ref2 + " (" + type2 + ")" ) 
                i = i - 1
                j = j - 1
            elif operation == TD.DELETE:
                edit_cost = params['delete_edit_cost'][ i - 1, j - 1 ]
                edit_script.append( "D " + str([current_dist, edit_cost] )  + " " + ref1 + " (" + type1 + ")" )
                i = i - 1
            elif operation == TD.INSERT:
                edit_cost = params['insert_edit_cost'][ i - 1, j - 1 ]
                edit_script.append( "I " + str([current_dist, edit_cost] )  + " " + ref2 + " (" + type2 + ")" ) 
                j = j - 1
            else:
                print "Error displaying edit script"
                return -1

        #edit_script = delete_script + update_script + insert_script
        return edit_script
                
    ## Method used by the command-line interface
    #
    # @param[in] xpath The xupath query that specifies a result set to
    #   count
    # @param[in] file_paths The files to compare
    # @param[in] count_type The cost function to use when evaluating
    #   edit operations
    # @return parameters to output an edit script
    # @details  params['pos2types0'] 
    # @details  params['pos2types1']
    # @details  params['pos2refs0']
    # @details  params['pos2refs1']
    # @details  params['(update|delete|insert)_edit_cost']
    # @details  params['edit_ops']     Matrix of edit operations
    # @details  params['forest_dist']  Distance matrix between parse trees
    @staticmethod
    def xudiff_main( xpath, file_paths, count_type ):
        if len(file_paths) != 2:
            print "Error, must have two file paths!\n"
            return -1

        xud = XUDiff()
        reports = {}

        file_path0 = file_paths[0]
        file_path1 = file_paths[1]
        
        fp = open( file_path0, 'r' )
        text0 = fp.read()
        fp.close()

        fp = open( file_path1, 'r' )
        text1 = fp.read()
        fp.close()

        init_params = {}
        if count_type == "builtin:byte" or count_type == "builtin:character" or count_type == "builtin:word":
            init_params['gamma'] = TD.edit_distance_cost
            init_params['sequence_type'] = count_type
        else:
            init_params['gamma'] = TD.unit_cost

        report = {}
        report['result_forest_0'] = [ text0 ]
        report['result_parse_tree_0'] = []
        report['pos2types0'] = []
        report['pos2refs0'] = []

        report['result_forest_1'] = [ text1 ]
        report['result_parse_tree_1'] = []
        report['pos2types1'] = []
        report['pos2refs1'] = []

        params = xud.xudiff( xpath, report, init_params )
        return params

    ## Method that actually processes the xupath query and 
    #   generates a difference report
    #  @param self
    #  @param[in] xPath The xupath used to generate one parse tree
    #   from the files
    #  @param[in] report The xudiff report, should be in,out 
    #  @param[in] init_params   TBD
    #  @return the difference report
    def xudiff( self, xPath, report, init_params ):
        result = []
        parser = parsers.XPathParser()
        parses = parser.xPath.scanString( xPath )
        for p, s, e in parses:
            result.append(p)

        report = self.process_xpath( result[0].path, "", report )
        t0 = report['result_parse_tree_0'][0]
        t1 = report['result_parse_tree_1'][0]

        params = TD.compute_tree_dist( t0, t1, init_params )

        report['l0'] = params['l1']
        report['l1'] = params['l2']
        report['labels0'] = params['labels1']
        report['labels1'] = params['labels2']
        report['tree_dist'] = params['tree_dist']
        report['edit_ops'] = params['edit_ops']
        report['update_edit_cost'] = params['update_edit_cost']
        report['insert_edit_cost'] = params['insert_edit_cost']
        report['delete_edit_cost'] = params['delete_edit_cost']
        report['forest_dist'] = params['forest_dist']
        return report

    ## Node-visitor action that processes the node of type 'xpath'
    #   when generating an xudiff report.
    #  @param self
    #  @param[in] xpath The 'xpath' parse-tree node to visit
    #  @param[in] indent The current indentation level within the
    #     parse tree
    #  @param[in] report The current xudiff report.  This should
    #   really be an in,out param
    #  @return The xudiff report that contains an edit script between
    #   the parse trees that result from applying an xupath to the
    #   input files
    #  @precondition If the 'xpath' node is None or empty, then we've
    #   reached a base case on recursion.  Just return the report
    def process_xpath( self, xpath, indent, report ):
        if xpath == None or len(xpath) == 0:
            return
        report = self.process_step( xpath.current_step, indent + " ", report )
        report = self.process_next_steps( xpath.next_steps, indent + " ", report )
        return report

    ## Node-visitor action that processes the node of type 'step' to
    #   generate an xudiff report.
    #  @param self
    #  @param[in] step     The 'step' parse-tree node to visit
    #  @param[in] indent   The current indentation level within the
    #   parse tree
    #  @param[in] report   The current xudiff report.  This should
    #   really be an in,out param
    #  @return The xudiff report 
    #  @precondition If the 'step' node is None or empty, then we've
    #   reached a base case on recursion.  Just return the report.
    def process_step( self, step, indent, report ):
        if step == None or len(step) == 0:
            return report

        report = self.process_cf_match( step.cf_match, indent + " ", report )
        report = self.process_predicate( step.predicate, indent + " ", report )
        return report

    ## Node-visitor action that processes the node of type
    #   'next_steps' to generate an xudiff report.
    #  @param self
    #  @param[in] next_steps The 'next_steps' parse-tree node to visit
    #  @param[in] indent     The current indentation level in the
    #     parse tree.  Perhaps we should replace this with a depth param
    #  @param[in] report     The current xudiff report.  This should
    #     really be an in,out param
    #  @return The xudiff report
    #  @precondition If the 'next_steps' node is None or empty, then
    #   we've reached a base case on recursion.  Just return the report
    def process_next_steps( self, next_steps, indent, report ):
        if next_steps == None or len(next_steps) == 0:
            return report
        
        for step in next_steps:
            if step != '/' and step != '//':
                report = self.process_step( step, indent, report )
        return report
    
    ## Node-visitor action that processes the node of type
    #   'cf_match' to generate an xudiff report.  Here we apply the
    #   production associated with the reference in this cf_match node
    #   and compare the two parse trees using Zhang and Shasha's algorithm.
    #
    #  @param self
    #  @param[in] cf_match  The 'cf_match' parse-tree node to visit
    #  @param[in] indent    The current indentation level in the parse
    #     tree.  
    #  @param[in] report    The current xudiff report.  This should
    #     really be an in,out param
    #  @return The xudiff report
    #  @precondition If the 'cf_match' node is None or empty, then
    #     we've reached a base case on recursion.  Just return the report
    def process_cf_match( self, cf_match, indent, report ):
        if cf_match == None or len(cf_match) == 0:
            return report

        parser = None
        production = None
        [ gname, pname ] = cf_match[0].split(':')
        parser = self.get_parser( gname )
        production = parser.getGrammarForUnit( pname )

        new_result_forest_0 = []
        new_result_forest_1 = []
        
        text_tree_0 = report['result_forest_0'][0]
        params0 = { 'pos': 1, 'pos2type':[], 'pos2ref':[], 'stack':[], 'refKey':parser.refKey } 

        for parse_tree, s, e in production.scanString( text_tree_0 ):
            t0 = parser.normalizeParseTree( parse_tree.asList() )
            [ t0, params0 ] = TD.postorder_traverse( t0, params0, self.set_position_as_id )
            [ t0, params0 ] = TD.postorder_traverse( t0, params0, self.compute_type_list )
            [ t0, params0 ] = TD.preorder_traverse( t0, params0, self.compute_references )
            [ t0, params0 ] = TD.postorder_traverse( t0, params0, self.compute_reference_list )
            report['result_parse_tree_0'].append( t0 )
            report['pos2types0'].append( params0['pos2type'] )
            report['pos2refs0'].append( params0['pos2ref'] )
        
        text_tree_1 = report['result_forest_1'][0]
        params1 = { 'pos': 1, 'pos2type':[], 'pos2ref':[], 'stack':[], 'refKey':parser.refKey }

        for parse_tree, s, e in production.scanString( text_tree_1 ):
            t1 = parser.normalizeParseTree( parse_tree.asList() )
            [ t1, params1 ] = TD.postorder_traverse( t1, params1, self.set_position_as_id )
            [ t1, params1 ] = TD.postorder_traverse( t1, params1, self.compute_type_list )
            [ t1, params1 ] = TD.preorder_traverse( t1, params1, self.compute_references )
            [ t1, params1 ] = TD.postorder_traverse( t1, params1, self.compute_reference_list )            
            report['result_parse_tree_1'].append( t1 )
            report['pos2types1'].append( params1['pos2type'] )
            report['pos2refs1'].append( params1['pos2ref'] )

        return report

    ## Node-Visitor action to take on a parse tree node of type
    #   're_match' when we generate an xudiff report.  When we process
    #   a regular expression match, we just return the report
    #   currently this is meaningless.
    #
    # @param self
    # @param[in] re_match  The 're_match' parse-tree node to visit
    # @param[in] indent    The current indentation level in the parse tree
    # @param[in] report    The current xudiff report
    # @return The xudiff report, unaltered 
    def process_re_match( self, re_match, indent, report ):
        return report

    ## Node-visitor action to take on a parse tree node of type 
    #  'predicate' when we generate an xudiff report.  
    # 
    # @param self
    # @param[in] predicate The 'predicate' parse-tree node to visit
    # @param[in] indent    The current indentation level within the
    #   parse tree
    # @param[in] report    The current xudiff report.  This should
    #   really be an in,out param
    # @return The xudiff report that was input.  
    def process_predicate( self, predicate, indent, report ):
        if predicate == None or len(predicate) == 0:
            return report
        report = self.process_re_match( predicate.re_match, indent + " ", report )
        report = self.process_next_steps( predicate.next_steps, indent + " ", report )
        return report

    ## Retrieve a grammar by reference.  I think that this should
    #   really live in the Parser module.
    #  
    #  @param[in] gname This is the grammar reference
    #  @return the Parser for the given grammar reference
    #  @exception UnrecognizedGrammarRef the grammar reference is not
    #   recognized    
    def get_parser( self, gname ):
        if ( 'tei' == gname ):
            parser = parsers.TEILiteParser()
        elif ('ios' == gname ):
            parser = parsers.CiscoIOSParser()
        elif ('nvd' == gname ):
            parser = parsers.NVDParser()
        elif ('cspec' == gname ):
            parser = parsers.SubsetCParser()
        elif ('builtin' == gname ):
            parser = parsers.BuiltinParser()
        else:
            print "Parser not yet implemented!"        
            return -1
        return parser

