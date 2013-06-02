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
import numpy
import pprint
import sys
from xutools.parsers import PythonDictionaryParseTree

## @package xutools.distances
#    This module contains classes that measure distance within our XUTools.
#    Currently, this means that we have EditDistance and ZhangShashaTreeDist.  
#    Over time, other distance algorithms may be added.
#

## The EditDistance class may be used as a source of cost functions using 
#    productions associated with the 'builtin' grammar.  Even though byte, 
#    character, word, may not appear within the 'builtin' grammar currently,
#    we still use these as builtins.
class EditDistance():

    ## Constant associated with the DELETE edit operation.
    DELETE = 1
    ## Constant associated with the UPDATE edit operation.
    UPDATE = 2
    ## Constant associated with the INSERT edit operation.
    INSERT = 3

    b = None
    ## The dynamic-programming, edit-distance matrix
    c = None

    ## Helper method for compute_edit_distance.
    #  @param self
    #  @param[in] s1  The first string to compare
    #  @param[in] s2  The second string to compare
    #  @param[in] count_type  The way to tokenize the strings for comparison.
    #  @return the edit distance between the two strings
    #  @exception UnrecognizedTypeException  We may want to think
    #    about how this relates to an UnrecognizedProductionRef exception.
    def edit_distance( self, s1, s2, count_type ):
        
        if 'builtin:byte' == count_type:
            if s1 != None:
                X = s1.encode()
            if s2 != None:
                Y = s2.encode()
            j_str = ""
        elif 'builtin:character' == count_type:
            if s1 != None:
                X = s1
            if s2 != None:
                Y = s2
            j_str = ""
        elif 'builtin:word' == count_type:
            if s1 != None:
                X = s1.split()
            if s2 != None:
                Y = s2.split()
            j_str = " "
        else:
            print "Error, unrecognized option\n"
            sys.exit(-1)

        if s1 == None and s2 == None:
            return 0
        elif s1 == None:
            return len(Y)
        elif s2 == None:
            return len(X)

        m = len(X)
        n = len(Y)
        self.compute_edit_distance( X, Y )
        return int(self.c[m,n])
    
    ## Method used to compute the edit distance between
    #   two strings X and Y
    #  @param     self
    #  @param[in] X  
    #  @param[in] Y
    #  @return None
    #  @postcondition The edit distance between X and Y is stored in
    #   the matrix self.c
    def compute_edit_distance( self, X, Y ):
        m = len(X)
        n = len(Y)

        self.c = numpy.zeros([m+1,n+1])
        self.b = numpy.zeros([m+1,n+1])

        for i in range(1, m+1):
            self.c[i,0] = i
        for j in range(1, n+1):
            self.c[0,j] = j
        for i in range(1, m+1):
            for j in range(1, n+1):
                if X[i-1] == Y[j-1]:
                    update_cost = 0
                else:
                    update_cost = 1
                update_dist = self.c[i-1,j-1] + update_cost
                delete_dist = self.c[i-1,j] + 1
                insert_dist = self.c[i,j-1] + 1
                dists = [ delete_dist, update_dist, insert_dist ]
                self.c[i,j] = min( dists )
        return

class ZhangShashaTreeDist():

    # Edit operation constants
    DELETE = 1
    UPDATE = 2
    INSERT = 3
    
    # Cost function constants
    UNIT_COST = "unit_cost"
    WORD_EDIST_COST = "word_edist_cost"
    CHARACTER_EDIST_COST = "char_edist_cost"

    t1 = None
    t2 = None
    gamma = None
    field = None

    leftmost_descendants_t1 = None
    leftmost_descendants_t2 = None

    lr_keyroots_t1 = None
    lr_keyroots_t2 = None

    tree_node_list = None

    tree_dist = None

    # mapping stuff
    S = None
    M = None

    # Assume that we just have raw trees, no positions
    # 
    @staticmethod
    def create(t1, t2, gamma_name, cost_corpus_element_field):
        td2 = ZhangShashaTreeDist()

        # Basic instance variable instantiations
        td2.t1 = t1
        td2.t2 = t2

        td2.field = cost_corpus_element_field
        if td2.UNIT_COST == gamma_name:
            td2.gamma = td2.unit_cost
        elif td2.WORD_EDIST_COST == gamma_name:
            td2.gamma = td2.word_edit_distance_cost
        elif td2.CHARACTER_EDIST_COST == gamma_name:
            td2.gamma = td2.character_edit_distance_cost
        else:
            print "Unrecognized cost function"
            sys.exit(-1)
        
        # Postorder Labeling 
        action_params = {}
        action_params['position'] = 1
        td2.t1.postorder_traverse( PythonDictionaryParseTree.set_position_as_index, action_params )
        action_params['position'] = 1
        td2.t2.postorder_traverse( PythonDictionaryParseTree.set_position_as_index, action_params )

        # Preprocessing for Distance and Mapping
        td2.leftmost_descendants_t1 = td2.compute_leftmost_descendants(t1)
        td2.leftmost_descendants_t2 = td2.compute_leftmost_descendants(t2)
        td2.lr_keyroots_t1 = td2.compute_lr_keyroots(t1)
        td2.lr_keyroots_t2 = td2.compute_lr_keyroots(t2)

        # Preprocessing for Cost Functions
        td2.tree_node_list_t1 = td2.compute_tree_node_list(t1)
        td2.tree_node_list_t2 = td2.compute_tree_node_list(t2)

        # Initialize treedist array
        i = td2.t1.tree_size()
        j = td2.t2.tree_size()
        td2.tree_dist = [[0 for j2 in range(j)] for i in range(i)]

        return td2

    def compute_mapping(self):
        self.S = []
        self.M = []

        i = self.t1.tree_size()
        j = self.t2.tree_size()
        self.compute_treedist()
        self.S.append( (i, j) )

        while ( len(self.S) > 0 ):
            (m, n) = self.S.pop()
            forestdist = self.treedist(m, n)
            self.mapping(m, n, forestdist)
        return self.M

    def mapping(self, m, n, forestdist):
        lm = self.leftmost_descendants_t1[ m - 1 ]
        ln = self.leftmost_descendants_t2[ n - 1 ]
        i = m
        j = n

        while ( i >= lm ) and (j >= ln ):
            i_idx = i - lm + 1
            j_idx = j - ln + 1
            delete = forestdist[i_idx - 1][j_idx] + self.gamma(i, 0, self.DELETE)
            insert = forestdist[i_idx][j_idx - 1] + self.gamma(0, j, self.INSERT)
            
            li = self.leftmost_descendants_t1[ i - 1 ]
            lj = self.leftmost_descendants_t2[ j - 1 ]
            li_idx = li - lm + 1
            lj_idx = lj - ln + 1

            if ( li == lm ) and ( lj == ln ):
                update = forestdist[i_idx-1][j_idx-1] + self.gamma(i, j, self.UPDATE)
            else:
                update = forestdist[li_idx-1][lj_idx-1] + self.tree_dist[i - 1][j - 1]
            if (delete == min( [ delete, insert, update ] )):
                self.M.append( (i, 0, self.gamma(i, 0, self.DELETE), delete) )
                i = i - 1
            elif ( insert == min( [ delete, insert, update ] )):
                self.M.append( (0, j, self.gamma(0, j, self.INSERT), insert) )
                j = j - 1
            else:
                if ( li == lm ) and ( lj == ln ):
                    self.M.append( (i, j, self.gamma(i, j, self.UPDATE), update) )
                    i = i - 1
                    j = j - 1
                else:
                    self.S.append( (i, j) )
                    i = li - 1
                    j = lj - 1

    def get_cost_str(self, op, subtree_cost, node_cost ):
        cost_str = "\t".join( [op, str(subtree_cost), str(node_cost) ] )
        cost_str = cost_str + "\t"
        return cost_str

    def get_t1_field_values(self, i, output_fields ):
        values = []
        for field in output_fields:
            value = str(self.tree_node_list_t1[i - 1][field]).replace("\n","\\n")
            if field == 'type':
                value = "(" + value + ")"
            values.append(value)
        return " ".join(values)

    def get_t2_field_values(self, j, output_fields ):
        values = []
        for field in output_fields:
            value = str(self.tree_node_list_t2[j - 1][field]).replace("\n","\\n")
            if field == 'type':
                value = "(" + value + ")"
            values.append(value)
        return " ".join(values)

    def output_mapping(self, outfile, output_fields):
        m = self.t1.tree_size()
        n = self.t2.tree_size()

        # Print out the updates and deletions in preorder
        action_params = {}
        action_params['field'] = "index"
        action_params['indices'] = []
        self.t1.preorder_traverse( PythonDictionaryParseTree.get_field_value, action_params )
        
        preordered_indices = action_params['indices']
        for idx in range(m):
            node1_index = preordered_indices[idx]
            (i,j,c,t) = [ (i,j,c,t) for i,j,c,t in self.M if i == node1_index ][0]
            
            if j == 0:
                value_str_1 = self.get_t1_field_values( i, output_fields )
                cost_str = self.get_cost_str( "D", t, c )
                outfile.write( cost_str + "%-50s ===> %-50s \n" % (value_str_1, "^") )
            else:
                value_str_1 = self.get_t1_field_values( i, output_fields )
                value_str_2 = self.get_t2_field_values( j, output_fields )
                cost_str = self.get_cost_str( "U", t, c )
                outfile.write( cost_str + "%-50s ===> %-50s \n" % (value_str_1, value_str_2 ) )

        # print out all insertions in preorder too
        action_params['indices'] = []
        self.t2.preorder_traverse( PythonDictionaryParseTree.get_field_value, action_params )
        preordered_indices = action_params['indices']
        for idx in range(n):
            node2_index = preordered_indices[idx]
            (i,j,c,t) = [ (i,j,c,t) for i,j,c,t in self.M if j == node2_index][0]
            if i == 0:
                value_str_2 = self.get_t2_field_values( j, output_fields )
                cost_str = self.get_cost_str( "I", t, c )
                outfile.write(cost_str + "%-50s ===> %-50s \n" % ("^", value_str_2) )

                
    def compute_treedist(self):
        m = self.t1.tree_size()
        n = self.t2.tree_size()
        self.tree_dist = [[0 for j2 in range(n)] for i in range(m)]

        for i2 in range( len(self.lr_keyroots_t1) ):
            for j2 in range( len(self.lr_keyroots_t2) ):
                i = self.lr_keyroots_t1[i2]
                j = self.lr_keyroots_t2[j2]
                self.treedist(i, j)
        return self.tree_dist

    # 
    # Computes distance between T[i] and T[j]
    # @param[in] i  The root node of t1
    # @param[in] j  The root node of t2
    def treedist(self, i, j):
        li = self.leftmost_descendants_t1[ i - 1 ]
        lj = self.leftmost_descendants_t2[ j - 1 ]

        nrows = i - li + 1 + 1
        ncols = j - lj + 1 + 1

        forestdist = [[0 for j2 in range(ncols)] for i2 in range(nrows) ]
        # row,col 0 are empty set
        forestdist[0][0] = 0
        
        for i1 in range(li,i+1):
            i1_idx = i1 - li + 1
            forestdist[i1_idx][0] = forestdist[i1_idx - 1][0] + self.gamma(i1, 0, self.DELETE)
        
        for j1 in range(lj,j+1):
            j1_idx = j1 - lj + 1
            forestdist[0][j1_idx] = forestdist[0][j1_idx - 1] + self.gamma(0, j1, self.INSERT)

        for i1 in range(li,i+1):
            for j1 in range(lj,j+1):
                li1 = self.leftmost_descendants_t1[ i1 - 1 ]
                lj1 = self.leftmost_descendants_t2[ j1 - 1 ]
                
                if (li1 == li) and (lj1 == lj):
                    i1_idx = i1 - li + 1
                    j1_idx = j1 - lj + 1
                    delete = forestdist[i1_idx - 1][j1_idx] + self.gamma(i1, 0, self.DELETE)
                    insert = forestdist[i1_idx][j1_idx - 1] + self.gamma(0, j1, self.INSERT)
                    update = forestdist[i1_idx-1][j1_idx-1] + self.gamma(i1, j1, self.UPDATE) 
                    forestdist[i1_idx][j1_idx] = min( [ delete, insert, update ] )
                    self.tree_dist[i1 - 1][j1 - 1] = forestdist[i1_idx][j1_idx]
                else:
                    i1_idx = i1 - li + 1
                    j1_idx = j1 - lj + 1
                    li1_idx = li1 - li + 1
                    lj1_idx = lj1 - lj + 1

                    delete = forestdist[i1_idx - 1][j1_idx] + self.gamma(i1, 0, self.DELETE)
                    insert = forestdist[i1_idx][j1_idx - 1] + self.gamma(0, j1, self.INSERT)
                    update = forestdist[li1_idx-1][lj1_idx-1] + self.tree_dist[i1 - 1][j1 - 1]
                    forestdist[i1_idx][j1_idx] = min( [ delete, insert, update ] )
        return forestdist

    def compute_lr_keyroots(self, t):
        lr_keyroots = [ t.root['index'] ]

        action_params = {}
        action_params['lr_keyroots'] = []
        
        t.preorder_traverse( ZhangShashaTreeDist.find_lr_keyroots, action_params )
        lr_keyroots = lr_keyroots + action_params['lr_keyroots']
        lr_keyroots.sort()
        return lr_keyroots

    @staticmethod
    def find_lr_keyroots( tree_node, action_params ):
        children = tree_node['children']
        if len(children) > 1:
            # if not a leftmost child, add as a keyroot
            for child in children[1:]:
                action_params['lr_keyroots'].append( child['index'] )

    def compute_leftmost_descendants(self, t):
        action_params = {}
        action_params['l'] = []
        t.postorder_traverse( ZhangShashaTreeDist.find_leftmost_descendants, action_params )
        leftmost_descendants = action_params['l']
        return leftmost_descendants
        
    @staticmethod
    def find_leftmost_descendants( tree_node, action_params ):
        index = tree_node['index']
        children = tree_node['children']
        if 0 == len(children):
            action_params['l'].append(index)
        else:
            leftmost_child_index = children[0]['index'] 
            action_params['l'].append( action_params['l'][leftmost_child_index - 1] )

    def compute_tree_node_list(self, t):
        action_params = {}
        action_params['tree_node_list'] = []
        t.postorder_traverse( ZhangShashaTreeDist.get_tree_node_list, action_params )
        tree_node_list = action_params['tree_node_list']
        return tree_node_list

    @staticmethod
    def get_tree_node_list( tree_node, action_params ):
        action_params['tree_node_list'].append( tree_node )
    
    ##
    #  Cost functions
    ##
    def unit_cost( self, i, j, operation ):
        idx = i - 1
        jdx = j - 1

        cost = None
        if self.DELETE == operation or self.INSERT == operation:
            cost = 1
        elif self.UPDATE == operation:
            value1 = self.tree_node_list_t1[idx][self.field]
            value2 = self.tree_node_list_t2[jdx][self.field]
            if value1 == None or value2 == None:
                if value1 != value2:
                    cost = 1
            elif value1.strip() != value2.strip():
                cost = 1
            else:
                cost = 0
        else:
            print "Unrecognized operation error!"
            sys.exit(-1)
        return cost

    ##
    #   Edit distance costs
    ##
    def word_edit_distance_cost( self, i, j, operation ):
        idx = i - 1
        jdx = j - 1

        cost = None
        edit_distance = EditDistance()
        
        value1 = self.tree_node_list_t1[idx][self.field]
        value2 = self.tree_node_list_t2[jdx][self.field]
        
        if self.UPDATE == operation:
            cost = edit_distance.edit_distance( value1, value2, "builtin:word" )
        elif self.INSERT == operation:
            cost = edit_distance.edit_distance( None, value2, "builtin:word" )
        elif self.DELETE == operation:
            cost = edit_distance.edit_distance( value1, None, "builtin:word" )
        
        return cost
    

    def character_edit_distance_cost( self, i, j, operation ):
        idx = i - 1
        jdx = j - 1

        cost = None
        edit_distance = EditDistance()
        
        value1 = self.tree_node_list_t1[idx][self.field]
        value2 = self.tree_node_list_t2[jdx][self.field]
        
        if self.UPDATE == operation:
            cost = edit_distance.edit_distance( value1, value2, "builtin:character" )
        elif self.INSERT == operation:
            cost = edit_distance.edit_distance( None, value2, "builtin:character" )
        elif self.DELETE == operation:
            cost = edit_distance.edit_distance( value1, None, "builtin:character" )
        
        return cost

