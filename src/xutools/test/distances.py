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
import codecs
import numpy
import pprint
import unittest
from xutools.distances import EditDistance
from xutools.distances import ZhangShashaTreeDist as TD

## @package test
#    This module contains classes that test the various distance
#    algorithms used by our XUTools.  

## These are test cases for our EditDistance class.  In general,
#    we should think carefully about test cases for Unicode as that
#    is how we shall test the difference between byte-based edit
#    costs and character-based edit costs.
class TestEditDistance( unittest.TestCase ):
    
    def test_compute_edit_distance(self):
        s1v1 = "ip address 129.170.9.157 255.255.255.255"
        s1v2 = "ip address 129.170.9.195 255.255.255.255"

        # process these as a sequence of unicode bytes
        edit_distance = EditDistance()
        X = s1v1.encode()
        Y = s1v2.encode()
        m = len(X)
        n = len(Y)
        self.assertEqual( m, 40 )
        self.assertEqual( n, 40 )
        edit_distance.compute_edit_distance( X, Y )
        self.assertEqual( edit_distance.c[m,n], 2 )        

        # process these as a sequence of chars
        edit_distance = EditDistance()
        X = s1v1
        Y = s1v2
        m = len(X)
        n = len(Y)
        self.assertEqual( m, 40 )
        self.assertEqual( n, 40 )
        edit_distance.compute_edit_distance( X, Y )
        self.assertEqual( edit_distance.c[m,n], 2 )        

        # process these as a sequence of words
        edit_distance = EditDistance()
        X = s1v1.split()
        Y = s1v2.split()
        m = len(X)
        n = len(Y)
        self.assertEqual( m, 4 )
        self.assertEqual( n, 4 )
        edit_distance.compute_edit_distance( X, Y )
        self.assertEqual( edit_distance.c[m,n], 1 )        
        
    def test_edit_distance(self):
        s1v1 = "ip address 129.170.9.157 255.255.255.255"
        s1v2 = "ip address 129.170.9.195 255.255.255.255"
        
        edit_distance = EditDistance()

        # test byte
        dist = edit_distance.edit_distance( s1v1, s1v2, "builtin:byte" )
        self.assertEqual( dist, 2 )

        dist = edit_distance.edit_distance( s1v1, s1v2, "builtin:character" )
        self.assertEqual( dist, 2 )

        dist = edit_distance.edit_distance( s1v1, s1v2, "builtin:word" )
        self.assertEqual( dist, 1 )

        dist = edit_distance.edit_distance( None, s1v2, "builtin:word" )
        self.assertEqual( dist, 4 )

        dist = edit_distance.edit_distance( s1v1, None, "builtin:byte" )
        self.assertEqual( dist, 40 )

## Methods to test our implementation of the 
#   ZhangShashaTreeDistance algorithm
#
#  In the future, we should think about the specifics of this 
#    tree-distance algorithm versus the whitebox tests
#    for a tree-distance algorithm interface.  For example, we should
#    design the tool so that a parallel variant of the 
#    Zhang Shasha tree distance algorithm can be swapped out for 
#    a regular version.
class TestZhangShashaTreeDist( unittest.TestCase ):
    
    # Example 4 T1 and T2
    a1 = TD.create_node( None, "a", None, [] )
    b1 = TD.create_node( None, "b", None, [] )
    c1 = TD.create_node( None, "c", None, [ b1 ] )
    d1 = TD.create_node( None, "d", None, [ a1, c1 ] )
    e1 = TD.create_node( None, "e", None, [] )
    f1 = TD.create_node( None, "f", None, [ d1, e1 ] )
    t1 = f1

    a2 = TD.create_node( None, "a", None, [] )
    b2 = TD.create_node( None, "b", None, [] )
    d2 = TD.create_node( None, "d", None, [ a2, b2 ] )
    c2 = TD.create_node( None, "c", None, [ d2 ] )
    e2 = TD.create_node( None, "e", None, [] )
    f2 = TD.create_node( None, "f", None, [ c2, e2 ] )
    t2 = f2

    # Another example based upon a TEI parse tree
    a3 = TD.create_node( None, "a", None, [] )
    b3 = TD.create_node( None, "b", None, [] )
    c3 = TD.create_node( None, "c", None, [] )
    d3 = TD.create_node( None, "d", None, [] )
    e3 = TD.create_node( None, "e", None, [ c3, d3 ] )
    f3 = TD.create_node( None, "f", None, [] )
    g3 = TD.create_node( None, "g", None, [] )
    h3 = TD.create_node( None, "h", None, [] )
    i3 = TD.create_node( None, "i", None, [ f3, g3, h3 ] )
    j3 = TD.create_node( None, "j", None, [ a3, b3, e3, i3 ] )
    t3 = j3

    a4 = TD.create_node( None, "a", None, [] )
    b4 = TD.create_node( None, "b", None, [] )
    f4 = TD.create_node( None, "f", None, [] )
    g4 = TD.create_node( None, "g", None, [] )
    h4 = TD.create_node( None, "h", None, [] )
    i4 = TD.create_node( None, "i", None, [ f4, g4, h4 ] )
    j4 = TD.create_node( None, "j", None, [ a4, b4, i4 ] )
    t4 = j4

    # Another example based upon a Cisco IOS parse tree
    l1v1 = TD.create_node( None, "b", None, [] )
    l2v1 = TD.create_node( None, "c", None, [] )
    l3v1 = TD.create_node( None, "d", None, [] )
    l4v1 = TD.create_node( None, "e", None, [] )
    l5v1 = TD.create_node( None, "f", None, [] )
    l6v1 = TD.create_node( None, "g", None, [] )
    l7v1 = TD.create_node( None, "h", None, [] )
    ios_ifv1 = TD.create_node( None, "a", None, [ l1v1, l2v1, l3v1, l4v1, l5v1, l6v1, l7v1 ] )

    l1v2 = TD.create_node( None, "b", None, [] )
    l2v2 = TD.create_node( None, "c", None, [] )
    l3v2 = TD.create_node( None, "d", None, [] )
    l4v2 = TD.create_node( None, "f", None, [] )
    l5v2 = TD.create_node( None, "g", None, [] )
    l6v2 = TD.create_node( None, "h", None, [] )
    l7v2 = TD.create_node( None, "i", None, [] )
    ios_ifv2 = TD.create_node( None, "a", None, [ l1v2, l2v2, l3v2, l4v2, l5v2, l6v2, l7v2 ] )

    def test_postorder_traverse(self):

        # first we want to do a postorder_traverse that sets IDs as postorder position
        params1 = { 'pos':1 }
        [ self.t1, params1 ] = TD.postorder_traverse( self.t1, params1, TD.set_position_to_id )
        self.assertEqual( params1['pos'], 7 )
        self.assertEqual( self.t1['id'], 6 )
        self.assertEqual( self.t1['label'], "f" )

        # children of f
        self.assertEqual( len( self.t1['children'] ), 2 )
        self.assertEqual( self.t1['children'][0]['id'], 4 )
        self.assertEqual( self.t1['children'][0]['label'], "d" )
        self.assertEqual( self.t1['children'][1]['id'], 5 )
        self.assertEqual( self.t1['children'][1]['label'], "e" )
        
        # children of D
        self.assertEqual( len(self.t1['children'][0]['children']), 2 ) 
        self.assertEqual( self.t1['children'][0]['children'][0]['id'], 1 )
        self.assertEqual( self.t1['children'][0]['children'][0]['label'], "a" )
        self.assertEqual( self.t1['children'][0]['children'][1]['id'], 3 )
        self.assertEqual( self.t1['children'][0]['children'][1]['label'], "c" )

        # children of A
        self.assertEqual( len(self.t1['children'][0]['children'][0]['children']) , 0 )
        
        # children of C
        self.assertEqual( len(self.t1['children'][0]['children'][1]['children']), 1 )
        self.assertEqual( self.t1['children'][0]['children'][1]['children'][0]['id'], 2 )
        self.assertEqual( self.t1['children'][0]['children'][1]['children'][0]['label'], "b" )

        # children of B
        self.assertEqual( len(self.t1['children'][0]['children'][1]['children'][0]['children']), 0 )

        params2 = { 'pos':1 }
        [ self.t2, params2 ] = TD.postorder_traverse( self.t2, params2, TD.set_position_to_id )
        self.assertEqual( params2['pos'], 7 )
        self.assertEqual( self.t2['id'], 6 )
        self.assertEqual( self.t2['label'], "f" )

        # children of f
        self.assertEqual( len( self.t2['children'] ), 2 )
        self.assertEqual( self.t2['children'][0]['id'], 4 )
        self.assertEqual( self.t2['children'][0]['label'], "c" )
        self.assertEqual( self.t2['children'][1]['id'], 5 )
        self.assertEqual( self.t2['children'][1]['label'], "e" )
        
        # children of c
        self.assertEqual( len(self.t2['children'][0]['children']), 1 )
        self.assertEqual( self.t2['children'][0]['children'][0]['id'], 3 )
        self.assertEqual( self.t2['children'][0]['children'][0]['label'], "d" )
        
        # children of e
        self.assertEqual( len(self.t2['children'][1]['children']), 0 )

        # children of d
        self.assertEqual( len(self.t2['children'][0]['children'][0]['children']), 2 )
        self.assertEqual( self.t2['children'][0]['children'][0]['children'][0]['id'], 1 )
        self.assertEqual( self.t2['children'][0]['children'][0]['children'][0]['label'], "a" )
        self.assertEqual( self.t2['children'][0]['children'][0]['children'][1]['id'], 2 )
        self.assertEqual( self.t2['children'][0]['children'][0]['children'][1]['label'], "b" )
        
        # children of a
        self.assertEqual( len(self.t2['children'][0]['children'][0]['children'][0]['children']), 0 )        
        # children of b
        self.assertEqual( len(self.t2['children'][0]['children'][0]['children'][1]['children']), 0 )        

        # SECOND EXAMPLE
        params3 = { 'pos':1 }
        [ self.t3, params3 ] = TD.postorder_traverse( self.t3, params3, TD.set_position_to_id )
        self.assertEqual( params3['pos'], 11 )
        self.assertEqual( self.t3['id'], 10 )
        self.assertEqual( self.t3['label'], "j" )
        self.assertEqual( len( self.t3['children'] ), 4 )

        params4 = { 'pos':1 }
        [ self.t4, params4 ] = TD.postorder_traverse( self.t4, params4, TD.set_position_to_id )
        self.assertEqual( params4['pos'], 8 )
        self.assertEqual( self.t4['id'], 7 )
        self.assertEqual( self.t4['label'], "j" )
        self.assertEqual( len( self.t4['children'] ), 3 )

    def test_preorder_traverse(self):
        
        # first we want to do a preorder_traverse that sets IDs as preorder position
        params1 = { 'pos':1 }
        [ self.t1, params1 ] = TD.preorder_traverse( self.t1, params1, TD.set_position_to_id )
        self.assertEqual( params1['pos'], 7 )
        self.assertEqual( self.t1['id'], 1 )
        self.assertEqual( self.t1['label'], "f" )
        
        # children of f
        self.assertEqual( len( self.t1['children'] ), 2 )
        self.assertEqual( self.t1['children'][0]['id'], 2 )
        self.assertEqual( self.t1['children'][0]['label'], "d" )
        self.assertEqual( self.t1['children'][1]['id'], 6 )
        self.assertEqual( self.t1['children'][1]['label'], "e" )

        # children of D
        self.assertEqual( len( self.t1['children'][0]['children'] ), 2 )
        self.assertEqual( self.t1['children'][0]['children'][0]['id'], 3 )
        self.assertEqual( self.t1['children'][0]['children'][0]['label'], "a" )
        
        self.assertEqual( self.t1['children'][0]['children'][1]['id'], 4 )
        self.assertEqual( self.t1['children'][0]['children'][1]['label'], "c" )

        # children of C
        self.assertEqual( len( self.t1['children'][0]['children'][1]['children'] ), 1 )
        self.assertEqual( self.t1['children'][0]['children'][1]['children'][0]['id'], 5 )
        self.assertEqual( self.t1['children'][0]['children'][1]['children'][0]['label'], "b" )
    
    def test_compute_labels(self):
        params1 = { 'labels':[] }
        params2 = { 'labels':[] }
        [ self.t1, params1 ] = TD.postorder_traverse( self.t1, params1, TD.compute_labels )
        [ self.t2, params2 ] = TD.postorder_traverse( self.t2, params2, TD.compute_labels )

        labels1_actual = params1['labels']
        labels2_actual = params2['labels']
        self.assertEqual( len( labels1_actual ), 6 )
        self.assertEqual( len( labels2_actual ), 6 )

        labels1_expected = [ "a", "b", "c", "d", "e", "f" ]
        labels2_expected = [ "a", "b", "d", "c", "e", "f" ]

        for i in range( 0, 6 ):
            self.assertEqual( labels1_actual[i], labels1_expected[i] )
            self.assertEqual( labels2_actual[i], labels2_expected[i] )
        
        # SECOND EXAMPLE
        params3 = { 'labels':[] }
        params4 = { 'labels':[] }
        [ self.t3, params3 ] = TD.postorder_traverse( self.t3, params3, TD.compute_labels )
        [ self.t4, params4 ] = TD.postorder_traverse( self.t4, params4, TD.compute_labels )

        labels3_actual = params3['labels']
        labels4_actual = params4['labels']
        self.assertEqual( len( labels3_actual ), 10 )
        self.assertEqual( len( labels4_actual ), 7 )

        labels3_expected = [ "a", "b", "c", "d", "e", "f", "g", "h", "i", "j" ]
        labels4_expected = [ "a", "b", "f", "g", "h", "i", "j" ]

        for i in range( 0, 10 ):
            self.assertEqual( labels3_actual[i], labels3_expected[i] )
        for i in range( 0, 7 ):
            self.assertEqual( labels4_actual[i], labels4_expected[i] )


    def test_compute_l(self):
        params1 = { 'l':[], 'pos':1 }
        params2 = { 'l':[], 'pos':1 }
        
        [ self.t1, params1 ] = TD.postorder_traverse( self.t1, params1, TD.set_position_to_id )        
        [ self.t1, params1 ] = TD.postorder_traverse( self.t1, params1, TD.compute_l )
        [ self.t2, params2 ] = TD.postorder_traverse( self.t2, params2, TD.set_position_to_id )
        [ self.t2, params2 ] = TD.postorder_traverse( self.t2, params2, TD.compute_l )
        
        l1_actual = params1['l']
        l2_actual = params2['l']
        self.assertEqual( len( l1_actual ) , 6 )
        self.assertEqual( len( l2_actual ) , 6 )

        l1_expected = [ 1, 2, 2, 1, 5, 1 ]
        l2_expected = [ 1, 2, 1, 1, 5, 1 ]
        
        for i in range(0, 6):
            self.assertEqual( l1_actual[i], l1_expected[i] )
            self.assertEqual( l2_actual[i], l2_expected[i] )

        # SECOND EXAMPLE
        params3 = { 'l':[], 'pos': 1 }
        params4 = { 'l':[], 'pos': 1 }

        [ self.t3, params3 ] = TD.postorder_traverse( self.t3, params3, TD.set_position_to_id )
        [ self.t3, params3 ] = TD.postorder_traverse( self.t3, params3, TD.compute_l )
        [ self.t4, params4 ] = TD.postorder_traverse( self.t4, params4, TD.set_position_to_id )
        [ self.t4, params4 ] = TD.postorder_traverse( self.t4, params4, TD.compute_l )

        l3_actual = params3['l']
        l4_actual = params4['l']
        self.assertEqual( len( l3_actual ), 10 )
        self.assertEqual( len( l4_actual ), 7 )

        l3_expected = [ 1, 2, 3, 4, 3, 6, 7, 8, 6, 1 ]
        l4_expected = [ 1, 2, 3, 4, 5, 3, 1 ]
        
        for i in range(0, 10):
            self.assertEqual( l3_actual[i], l3_expected[i] )
        for i in range(0, 7):
            self.assertEqual( l4_actual[i], l4_expected[i] )


    def test_get_lr_keyroots(self):
        params1 = { 'LR_keyroots':{},
                    'l':[] }
        params2 = { 'LR_keyroots':{},
                    'l':[] }

        [ self.t1, params1 ] = TD.postorder_traverse( self.t1, params1, TD.compute_l )
        [ self.t1, params1 ] = TD.get_lr_keyroots( self.t1, params1 )

        [ self.t2, params2 ] = TD.postorder_traverse( self.t2, params2, TD.compute_l )
        [ self.t2, params2 ] = TD.get_lr_keyroots( self.t2, params2 )
        
        kr1_actual = params1['LR_keyroots']
        kr1_expected = [ 3, 5, 6 ]
        kr2_actual = params2['LR_keyroots']
        kr2_expected = [ 2, 5, 6 ]

        for i in range(0, 3):
            self.assertEqual( kr1_actual[i], kr1_expected[i] )
            self.assertEqual( kr2_actual[i], kr2_expected[i] )

        # SECOND EXAMPLE
        params3 = { 'LR_keyroots':{},
                    'l':[] }
        params4 = { 'LR_keyroots':{},
                    'l':[] }
        
        [ self.t3, params3 ] = TD.postorder_traverse( self.t3, params3, TD.compute_l )
        [ self.t4, params4 ] = TD.postorder_traverse( self.t4, params4, TD.compute_l )


        [ self.t3, params3 ] = TD.get_lr_keyroots( self.t3, params3 )
        [ self.t4, params4 ] = TD.get_lr_keyroots( self.t4, params4 )

        kr3_actual = params3['LR_keyroots']
        kr3_expected = [ 2, 4, 5, 7, 8, 9, 10 ]
        kr4_actual = params4['LR_keyroots']
        kr4_expected = [ 2, 4, 5, 6, 7 ] 
        
        for i in range(0, 7):
            self.assertEqual( kr3_actual[i], kr3_expected[i] )
        for i in range(0, 5):
            self.assertEqual( kr4_actual[i], kr4_expected[i] )


    def test_compute_treedist(self):
        
        # Preprocessing
        params1 = { 'LR_keyroots':{},
                    'l':[],
                    'labels':[] }
        params2 = { 'LR_keyroots':{},
                    'l':[],
                    'labels':[] }

        #-- Compute labels
        [ self.t1, params1 ] = TD.postorder_traverse( self.t1, params1, TD.compute_labels )
        [ self.t2, params2 ] = TD.postorder_traverse( self.t2, params2, TD.compute_labels )

        #-- Compute l
        [ self.t1, params1 ] = TD.postorder_traverse( self.t1, params1, TD.compute_l )
        [ self.t2, params2 ] = TD.postorder_traverse( self.t2, params2, TD.compute_l )
        
        #-- Compute LR_keyroots
        [ self.t1, params1 ] = TD.get_lr_keyroots( self.t1, params1 )
        [ self.t2, params2 ] = TD.get_lr_keyroots( self.t2, params2 )
        
        # First loop of example
        i_prime = 1
        j_prime = 1
        i = params1['LR_keyroots'][i_prime - 1]
        j = params2['LR_keyroots'][j_prime - 1]
        self.assertEqual(i, 3)
        self.assertEqual(j, 2)

        Tree_dist = numpy.zeros( [self.t1['id'], self.t2['id']] )

        params = {}
        params['update_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['insert_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['delete_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )

        params['gamma'] = TD.unit_cost
        params['labels1'] = params1['labels']
        params['labels2'] = params2['labels']
        params['l1'] = params1['l']
        params['l2'] = params2['l']
        params['tree_dist'] = Tree_dist

        params = TD.treedist( i, j, params )
        self.assertEqual( params['tree_dist'][ 2 - 1, 2 - 1 ], 0 )
        #self.assertEqual( params['edit_ops'][ 2 - 1, 2 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 2 - 1, 2 - 1], 0 )
        
        self.assertEqual( params['tree_dist'][ 3 - 1, 2 - 1 ], 1 )
        #self.assertEqual( params['edit_ops'][ 3 - 1, 2 - 1 ], TD.delete )
        #self.assertEqual( params['edit_cost'][ 3 - 1, 2 - 1 ], 1 )
        
        # Second loop of example
        i_prime = 1
        j_prime = 2
        i = params1['LR_keyroots'][i_prime - 1]
        j = params2['LR_keyroots'][j_prime - 1]
        self.assertEqual(i, 3)
        self.assertEqual(j, 5)

        params['update_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['insert_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['delete_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params = TD.treedist( i, j, params )
        self.assertEqual( params['tree_dist'][ 2 - 1, 5 - 1 ], 1 )
        #        self.assertEqual( params['edit_ops'][ 2 - 1, 5 - 1 ], TD.update )
        #        self.assertEqual( params['edit_cost'][ 2 - 1, 5 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 3 - 1, 5 - 1 ], 2 )
        #self.assertEqual( params['edit_ops'][ 3 - 1, 5 - 1 ], TD.delete )
        #self.assertEqual( params['edit_cost'][ 3 - 1, 5 - 1 ], 1 )

        # Third loop of example
        i_prime = 1
        j_prime = 3
        i = params1['LR_keyroots'][i_prime - 1]
        j = params2['LR_keyroots'][j_prime - 1]
        self.assertEqual(i, 3)
        self.assertEqual(j, 6)

        params['update_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['insert_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['delete_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params = TD.treedist( i, j, params )
        self.assertEqual( params['tree_dist'][ 2 - 1, 1 - 1 ], 1 )
        #self.assertEqual( params['edit_ops'][ 2 - 1, 1 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 2 - 1, 1 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 2 - 1, 3 - 1 ], 2 )
        #self.assertEqual( params['edit_ops'][ 2 - 1, 3 - 1 ], TD.insert )
        #self.assertEqual( params['edit_cost'][ 2 - 1, 3 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 2 - 1, 4 - 1 ], 3 )
        #self.assertEqual( params['edit_ops'][ 2 - 1, 4 - 1 ], TD.insert )
        #self.assertEqual( params['edit_cost'][ 2 - 1, 4 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 2 - 1, 6 - 1 ], 5 )
        #self.assertEqual( params['edit_ops'][ 2 - 1, 6 - 1 ], TD.insert )
        #self.assertEqual( params['edit_cost'][ 2 - 1, 6 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 3 - 1, 1 - 1 ], 2 )
        #self.assertEqual( params['edit_ops'][ 3 - 1, 1 - 1 ], TD.delete )
        #self.assertEqual( params['edit_cost'][ 3 - 1, 1 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 3 - 1, 3 - 1 ], 2 )
        #self.assertEqual( params['edit_ops'][ 3 - 1, 3 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 3 - 1, 3 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 3 - 1, 4 - 1 ], 2 )
        #self.assertEqual( params['edit_ops'][ 3 - 1, 4 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 3 - 1, 4 - 1 ], 0 )

        self.assertEqual( params['tree_dist'][ 3 - 1, 6 - 1 ], 4 )
        #self.assertEqual( params['edit_ops'][ 3 - 1, 6 - 1 ], TD.insert )
        #self.assertEqual( params['edit_cost'][ 3 - 1, 6 - 1 ], 1 )

        # Fourth loop of example
        i_prime = 2
        j_prime = 1
        i = params1['LR_keyroots'][i_prime - 1]
        j = params2['LR_keyroots'][j_prime - 1]
        self.assertEqual(i, 5)
        self.assertEqual(j, 2)

        params['update_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['insert_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['delete_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params = TD.treedist( i, j, params )
        self.assertEqual( params['tree_dist'][ 5 - 1, 2 - 1 ], 1 )
        #self.assertEqual( params['edit_ops'][ 5 - 1, 2 - 1], TD.update )
        #self.assertEqual( params['edit_cost'][ 5 - 1, 2 - 1 ], 1 )

        # Fifth loop of example
        i_prime = 2
        j_prime = 2
        i = params1['LR_keyroots'][i_prime - 1]
        j = params2['LR_keyroots'][j_prime - 1]
        self.assertEqual(i, 5)
        self.assertEqual(j, 5)

        params['update_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['insert_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['delete_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params = TD.treedist( i, j, params )
        self.assertEqual( params['tree_dist'][ 5 - 1, 5 - 1 ], 0 )
        #self.assertEqual( params['edit_ops'][ 5 - 1, 5 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 5 - 1, 5 - 1 ], 0 )

        # Sixth loop of example
        i_prime = 2
        j_prime = 3
        i = params1['LR_keyroots'][i_prime - 1]
        j = params2['LR_keyroots'][j_prime - 1]
        self.assertEqual(i, 5)
        self.assertEqual(j, 6)

        params['update_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['insert_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['delete_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params = TD.treedist( i, j, params )
        self.assertEqual( params['tree_dist'][ 5 - 1, 1 - 1 ], 1 )
        #self.assertEqual( params['edit_ops'][ 5 - 1, 1 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 5 - 1, 1 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 5 - 1, 3 - 1 ], 3 )
        #self.assertEqual( params['edit_ops'][ 5 - 1, 3 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 5 - 1, 3 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 5 - 1, 4 - 1 ], 4 )
        #self.assertEqual( params['edit_ops'][ 5 - 1, 4 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 5 - 1, 4 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 5 - 1, 6 - 1 ], 5 )
        #self.assertEqual( params['edit_ops'][ 5 - 1, 6 - 1 ], TD.insert )
        #self.assertEqual( params['edit_cost'][ 5 - 1, 6 - 1 ], 1 )

        # Seventh loop of example
        i_prime = 3
        j_prime = 1
        i = params1['LR_keyroots'][i_prime - 1]
        j = params2['LR_keyroots'][j_prime - 1]
        self.assertEqual(i, 6)
        self.assertEqual(j, 2)

        params['update_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['insert_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['delete_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params = TD.treedist( i, j, params )
        self.assertEqual( params['tree_dist'][ 1 - 1, 2 - 1 ], 1 )
        #self.assertEqual( params['edit_ops'][ 1 - 1, 2 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 1 - 1, 2 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 4 - 1, 2 - 1 ], 3 )
        #self.assertEqual( params['edit_ops'][ 4 - 1, 2 - 1 ], TD.delete )
        #self.assertEqual( params['edit_cost'][ 4 - 1, 2 - 1 ], 1 )
        
        self.assertEqual( params['tree_dist'][ 6 - 1, 2 - 1 ], 5 )
        #self.assertEqual( params['edit_ops'][ 6 - 1, 2 - 1 ], TD.delete )
        #self.assertEqual( params['edit_cost'][ 6 - 1, 2 - 1 ], 1 )

        # Eighth loop of example
        i_prime = 3
        j_prime = 2
        i = params1['LR_keyroots'][i_prime - 1]
        j = params2['LR_keyroots'][j_prime - 1]
        self.assertEqual(i, 6)
        self.assertEqual(j, 5)

        params['update_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['insert_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['delete_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params = TD.treedist( i, j, params )
        self.assertEqual( params['tree_dist'][ 1 - 1, 5 - 1 ], 1 )
        #self.assertEqual( params['edit_ops'][ 1 - 1, 5 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 1 - 1, 5 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 4 - 1, 5 - 1 ], 4 )
        #self.assertEqual( params['edit_ops'][ 4 - 1, 5 - 1 ], TD.delete )
        #self.assertEqual( params['edit_cost'][ 4 - 1, 5 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 6 - 1, 5 - 1 ], 5 )
        #self.assertEqual( params['edit_ops'][ 6 - 1, 5 - 1 ], TD.delete )
        #self.assertEqual( params['edit_cost'][ 6 - 1, 5 - 1 ], 1 )
        
        # Ninth loop of example
        i_prime = 3
        j_prime = 3
        i = params1['LR_keyroots'][i_prime - 1]
        j = params2['LR_keyroots'][j_prime - 1]
        self.assertEqual(i, 6)
        self.assertEqual(j, 6)

        params['update_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['insert_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params['delete_edit_cost'] = numpy.zeros( [self.t1['id'], self.t2['id']] )
        params = TD.treedist( i, j, params )
        self.assertEqual( params['tree_dist'][ 1 - 1, 1 - 1 ], 0 )
        #self.assertEqual( params['edit_ops'][ 1 - 1, 1 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 1 - 1, 1 - 1 ], 0 )

        self.assertEqual( params['tree_dist'][ 4 - 1, 1 - 1 ], 3 )
        #self.assertEqual( params['edit_ops'][ 4 - 1, 1 - 1 ], TD.delete )
        #self.assertEqual( params['edit_cost'][ 4 - 1, 1 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 6 - 1, 1 - 1 ], 5 )
        #self.assertEqual( params['edit_ops'][ 6 - 1, 1 - 1 ], TD.delete )
        #self.assertEqual( params['edit_cost'][ 6 - 1, 1 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 1 - 1, 3 - 1 ], 2 )
        #self.assertEqual( params['edit_ops'][ 1 - 1, 3 - 1 ], TD.insert )
        #self.assertEqual( params['edit_cost'][ 1 - 1, 3 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 4 - 1, 3 - 1 ], 1 )
        #self.assertEqual( params['edit_ops'][ 4 - 1, 3 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 4 - 1, 3 - 1 ], 0 )

        self.assertEqual( params['tree_dist'][ 6 - 1, 3 - 1 ], 3 )
        #self.assertEqual( params['edit_ops'][ 6 - 1, 3 - 1 ], TD.delete )
        #self.assertEqual( params['edit_cost'][ 6 - 1, 3 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 1 - 1, 4 - 1 ], 3 )
        #self.assertEqual( params['edit_ops'][ 1 - 1, 4 - 1 ], TD.insert )
        #self.assertEqual( params['edit_cost'][ 1 - 1, 4 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 4 - 1, 4 - 1 ], 2 )
        #self.assertEqual( params['edit_ops'][ 4 - 1, 4 - 1 ], TD.insert )
        #self.assertEqual( params['edit_cost'][ 4 - 1, 4 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 6 - 1, 4 - 1 ], 3 )
        #self.assertEqual( params['edit_ops'][ 6 - 1, 4 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 6 - 1, 4 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 1 - 1, 6 - 1 ], 5 )
        #self.assertEqual( params['edit_ops'][ 1 - 1, 6 - 1 ], TD.insert )
        #self.assertEqual( params['edit_cost'][ 1 - 1, 6 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 4 - 1, 6 - 1 ], 4 )
        #self.assertEqual( params['edit_ops'][ 4 - 1, 6 - 1 ], TD.insert )
        #self.assertEqual( params['edit_cost'][ 4 - 1, 6 - 1 ], 1 )

        self.assertEqual( params['tree_dist'][ 6 - 1, 6 - 1 ], 2 )
        #self.assertEqual( params['edit_ops'][ 6 - 1, 6 - 1 ], TD.update )
        #self.assertEqual( params['edit_cost'][ 6 - 1, 6 - 1 ], 0 )

        expected_tree_dist = numpy.zeros( [self.t1['id'], self.t2['id']] )
        expected_tree_dist[0,:] = [ 0, 1, 2, 3, 1, 5 ]
        expected_tree_dist[1,:] = [ 1, 0, 2, 3, 1, 5 ]
        expected_tree_dist[2,:] = [ 2, 1, 2, 2, 2, 4 ]
        expected_tree_dist[3,:] = [ 3, 3, 1, 2, 4, 4 ]
        expected_tree_dist[4,:] = [ 1, 1, 3, 4, 0, 5 ]
        expected_tree_dist[5,:] = [ 5, 5, 3, 3, 5, 2 ]

        for i in range(0, self.t1['id']):
            for j in range(0, self.t2['id']):
                self.assertEqual( params['tree_dist'][i,j], expected_tree_dist[i,j] )


    def test_compute_tree_dist(self):
        init_params = { 'gamma':TD.unit_cost }
        params = TD.compute_tree_dist( self.t1, self.t2, init_params )
        self.assertEqual( params['tree_dist'][ 6 - 1, 6 - 1 ] , 2 )

        i = len( params['l1'] )
        j = len( params['l2'] )
        self.assertEqual( i, 6 )
        self.assertEqual( j, 6 )

        actual_edit_script = TD.output_edit_script( i, j, 1, 1, params )
        self.assertEqual( params['tree_dist'][ i - 1, j - 1 ], 2.0 )
        expected_edit_script = [ "D ([1.0, 1.0]) T1[3]",
                                 "U ([2.0, 0.0]) T1[6]->T2[6]",
                                 "U ([2.0, 0.0]) T1[5]->T2[5]",
                                 "U ([1.0, 0.0]) T1[4]->T2[3]",
                                 "U ([0.0, 0.0]) T1[2]->T2[2]",
                                 "U ([0.0, 0.0]) T1[1]->T2[1]" ,
                                 "I ([2.0, 1.0]) T2[4]"]
        for i in range( 0, len( expected_edit_script ) ):
            self.assertEqual( actual_edit_script[i], expected_edit_script[i] )
            
        # SECOND EXAMPLE
        init_params = { 'gamma':TD.unit_cost }
        params = TD.compute_tree_dist( self.t3, self.t4, init_params )
        i = len( params['l1'] )
        j = len( params['l2'] )
        self.assertEqual( i, 10 )
        self.assertEqual( j, 7 )
        actual_edit_script = TD.output_edit_script( i, j, 1, 1, params )
        self.assertEqual( params['tree_dist'][ i - 1, j - 1 ], 3.0 )
        expected_edit_script = [ "D ([3.0, 1.0]) T1[5]",
                                 "D ([2.0, 1.0]) T1[4]",
                                 "D ([1.0, 1.0]) T1[3]",
                                 "U ([3.0, 0.0]) T1[10]->T2[7]",
                                 "U ([3.0, 0.0]) T1[9]->T2[6]",
                                 "U ([3.0, 0.0]) T1[8]->T2[5]",
                                 "U ([3.0, 0.0]) T1[7]->T2[4]",
                                 "U ([3.0, 0.0]) T1[6]->T2[3]",
                                 "U ([0.0, 0.0]) T1[2]->T2[2]",
                                 "U ([0.0, 0.0]) T1[1]->T2[1]"]

        for i in range( 0, len( expected_edit_script ) ):
            self.assertEqual( actual_edit_script[i], expected_edit_script[i] )

        # THIRD EXAMPLE
        init_params = { 'gamma':TD.unit_cost }
        params = TD.compute_tree_dist( self.ios_ifv1, self.ios_ifv2, init_params )
        i = len( params['l1'] )
        j = len( params['l2'] )
        actual_edit_script = TD.output_edit_script( i, j, 1, 1, params )
        self.assertEqual( params['tree_dist'][ i - 1, j - 1 ], 2.0 )
        expected_edit_script = [ "D ([1.0, 1.0]) T1[4]",
                                 "U ([2.0, 0.0]) T1[8]->T2[8]",
                                 "U ([1.0, 0.0]) T1[7]->T2[6]",
                                 "U ([1.0, 0.0]) T1[6]->T2[5]",
                                 "U ([1.0, 0.0]) T1[5]->T2[4]",
                                 "U ([0.0, 0.0]) T1[3]->T2[3]",
                                 "U ([0.0, 0.0]) T1[2]->T2[2]",
                                 "U ([0.0, 0.0]) T1[1]->T2[1]",
                                 "I ([2.0, 1.0]) T2[7]" ]
        for i in range( 0, len( expected_edit_script ) ):
            self.assertEqual( actual_edit_script[i], expected_edit_script[i] )
