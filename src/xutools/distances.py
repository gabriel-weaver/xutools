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
import numpy
import sys

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
    def edit_distance(self, s1, s2, count_type):

        if 'builtin:byte' == count_type:
            if s1 != None:
                X = s1.encode()
            if s2 != None:
                Y = s2.encode()
        elif 'builtin:character' == count_type:
            if s1 != None:
                X = s1
            if s2 != None:
                Y = s2
        elif 'builtin:word' == count_type:
            if s1 != None:
                X = s1.split()
            if s2 != None:
                Y = s2.split()
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
        self.compute_edit_distance(X, Y)
        return self.c[m, n]

    ## Method used to compute the edit distance between
    #   two strings X and Y
    #  @param     self
    #  @param[in] X
    #  @param[in] Y
    #  @return None
    #  @postcondition The edit distance between X and Y is stored in
    #   the matrix self.c
    def compute_edit_distance(self, X, Y):
        m = len(X)
        n = len(Y)

        self.c = numpy.zeros([m + 1, n + 1])
        self.b = numpy.zeros([m + 1, n + 1])

        for i in range(1, m + 1):
            self.c[i, 0] = i
        for j in range(1, n + 1):
            self.c[0, j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if X[i - 1] == Y[j - 1]:
                    update_cost = 0
                else:
                    update_cost = 1
                update_dist = self.c[i - 1, j - 1] + update_cost
                delete_dist = self.c[i - 1, j] + 1
                insert_dist = self.c[i, j - 1] + 1
                dists = [delete_dist, update_dist, insert_dist]
                self.c[i, j] = min(dists)
        return


## The ZhangShashaTreeDist class implements the Zhang and Shasha tree
#   editing distance algorithm from their 1989 paper.
class ZhangShashaTreeDist():

    ## Constant associated with the DELETE edit operation
    DELETE = 1
    ## Constant associated with the UPDATE edit operation
    UPDATE = 2
    ## Constant associated with the INSERT edit operation
    INSERT = 3

    ## Factory method used to create a node in the canonical parse-tree
    #   representation.
    #  @param id       The node identifier    (postorder traversal position)
    #  @param label    The label of the node  (parse tree 'content')
    #  @param type     The production associated with the parse tree node
    #  @param children The children of the parse tree node
    #  @return the parse-tree node
    @staticmethod
    def create_node(id, label, type, children):
        node = {'id': id,
                 'label': label,
                 'type': type,
                 'children': children}
        return node

    ## Node-visitor action to set the ID of a parse-tree node, to its
    #    position as determined by some traversal.
    #  @param[in] node     The node being visited
    #  @param[in] params   The parameters used to set the id.
    #  @precondition   params['pos'] >= 0
    #  @return    The updated node and params['pos'].  Really, node
    #    and params should be in,out parameters and we should return None.
    @staticmethod
    def set_position_to_id(node, params):
        node['id'] = params['pos']
        params['pos'] = params['pos'] + 1
        return [node, params]

    ## Node-visitor action to compute a list of node labels indexed by
    #    node position as determined by some traversal.
    #  @param[in] node    The node being visited
    #  @param[in] params  The parameters used
    #  @precondition params['labels'] == []
    #  @return   The updated node and params['labels'].  Really, node
    #    and params should be in,out parameters and we should return None.
    @staticmethod
    def compute_labels(node, params):
        params['labels'].append(node['label'])
        return [node, params]

    ## Node-visitor action to compute the position of the leftmost
    #    descendant of each node within the parse tree.
    #  @param[in] node   The node being visited
    #  @param[in] params The parameters used
    #  @precondition params['l'] == []
    #  @return  The updated params.  The node is not updated.  Really,
    #    params should be in,out and we should return None or some
    #    code to the calling environment.
    #  @note Think about doing a time/space analysis for each of these
    #    functions and compare to Zhang and Shasha's paper.
    @staticmethod
    def compute_l(node, params):
        if 0 == len(node['children']):
            params['l'].append(node['id'])
        else:
            child_id = node['children'][0]['id']
            params['l'].append(params['l'][child_id - 1])

        return [node, params]

    ## Node-visitor action to compute the lr_keyroots (as defined in
    #   the Zhang-Shasha algorithm).  Any ancestor of these nodes do
    #   not share the same leftmost child as this node.
    #  @param[in] node  The node being visited
    #  @param[in] params The parameters for the Zhang/Shasha tree
    #     distance algorithm
    #  @return the modified params
    #  @precondition params['l'] != None and node['id'] is the
    #     position of the node in the parse tree given a postorder
    #     traversal
    #  @postcondition params['LR_keyroots'] is computed
    #  @note  Think about exceptions, for example the node may not
    #     have an ID
    @staticmethod
    def compute_lr_keyroots(node, params):
        l_value = params['l'][node['id'] - 1]
        params['LR_keyroots'][l_value] = node['id']

        return [node, params]

    ## Method to get the lr_keyroots from the root parse-tree node.
    #  @param[in] node     The root of the parse tree for which to get
    #    the lr_keyroots
    #  @param[in] params   The parameters for the Zhang/Shasha tree
    #    distance algorithm
    #  @return the lr_keyroots in params['LR_keyroots']
    #  @postcondition params['LR_keyroots'] is computed for the entire
    #    parse tree rooted at 'node'
    #  @note Think about exceptions, for example, 'LR_keyroots' may be
    #    in a weird state
    @staticmethod
    def get_lr_keyroots(node, params):
        [node, params] = ZhangShashaTreeDist.postorder_traverse(node, params, ZhangShashaTreeDist.compute_lr_keyroots)
        keys = params['LR_keyroots'].keys()
        keys.sort()
        roots = map(params['LR_keyroots'].get, keys)
        roots.sort()
        params['LR_keyroots'] = roots
        return [node, params]

    ## Method to do a postorder traverse of a parse tree
    #  @param[in] tree    The parse tree to traverse
    #  @param[in] params  The params to modify during traversal and
    #      parameters for the action method
    #  @param[in] action  The node-visitor action to take on a parse
    #      tree node.
    #  @return  The modified tree and params
    #  @note    Think about any exceptions here
    @staticmethod
    def postorder_traverse(tree, params, action):
        # visit all the children

        new_children = []
        for child in tree['children']:
            [new_child, params] = ZhangShashaTreeDist.postorder_traverse(child, params, action)
            new_children.append(new_child)
        tree['children'] = new_children

        # perform action upon the node
        [tree, params] = action(tree, params)
        return [tree, params]

    ## Method to do a preorder traverse of a parse tree
    #  @param[in] tree    The parse tree to traverse
    #  @param[in] params  The params to modify during traversal and
    #      parameters for the action method
    #  @param[in] action  The node-visitor action to take on a parse
    #      tree node.
    #  @return The modified tree and params
    #  @note   Think about any exceptions here
    @staticmethod
    def preorder_traverse(tree, params, action):
        # perform action upon the node (including a stack push)
        [tree, params] = action(tree, params)

        # visit all the children
        new_children = []
        for child in tree['children']:
            [new_child, params] = ZhangShashaTreeDist.preorder_traverse(child, params, action)
            new_children.append(new_child)
        tree['children'] = new_children

        if 'stack' in params.keys():
            params['stack'].pop()
        return [tree, params]

    ## Edit-cost function: Given an operation, compute the cost of
    #   that operation. In this cost function, deletes and inserts of
    #   nodes in tree 1 and tree 2 respectively cost 1.  Updates of a
    #   node may cost 0 iff the labels of the two nodes are identical,
    #   otherwise, cost is 1.
    #
    #  @param i  The position of the node to compare in tree 1
    #  @param j  The position of the node to compare in tree 2
    #  @param operation  The operation for which to compute the cost
    #  @return   The cost of the edit operation
    #  @note  Think about exceptions here
    @staticmethod
    def unit_cost(i, j, operation, params):
        idx = i - 1
        jdx = j - 1

        cost = 0
        if ZhangShashaTreeDist.DELETE == operation or ZhangShashaTreeDist.INSERT == operation:
            cost = 1
        elif (ZhangShashaTreeDist.UPDATE == operation):
            label1 = params['labels1'][idx]
            label2 = params['labels2'][jdx]
            if label1 == None or label2 == None:
                if label1 != label2:
                    cost = 1
            elif label1.strip() != label2.strip():
                cost = 1
        return cost

    ## Edit-cost function: Given an operation, compute the cost of
    #   that operation.  In this cost function, deletes cost the
    #   length (measured in tokens as defined by
    #   params['sequence_type']) of the label of node i.  Inserts
    #   cost the length of the label of node j.  Update cost is the
    #   string edit distance between the labels of node i and node j.
    #
    #  @param i  The position of the node to compare in tree 1
    #  @param j  The position of the node to compare in tree 2
    #  @param operation  The operation for which to compute the cost
    #  @return  The cost of the edit operation
    #  @exception  UnrecognizedTypeException is thrown when we don't
    #    have a 'sequence_type' that tells us how to tokenize node labels
    @staticmethod
    def edit_distance_cost(i, j, operation, params):
        idx = i - 1
        jdx = j - 1

        cost = 0
        edit_distance = EditDistance()
        if 'sequence_type' in params.keys():
            sequence_type = params['sequence_type']
        else:
            print "Must have 'sequence_type' key in params for edit_distance_cost!\n"
            sys.exit(-1)

        if ZhangShashaTreeDist.UPDATE == operation:
            label1 = params['labels1'][idx]
            label2 = params['labels2'][jdx]
            cost = edit_distance.edit_distance(label1, label2, sequence_type)
        elif ZhangShashaTreeDist.INSERT == operation:
            label1 = params['labels1'][idx]
            label2 = params['labels2'][jdx]
            cost = edit_distance.edit_distance(None, label2, sequence_type)
            if cost == 0:
                cost += 0.001
        elif ZhangShashaTreeDist.DELETE == operation:
            label1 = params['labels1'][idx]
            label2 = params['labels2'][jdx]
            cost = edit_distance.edit_distance(label1, None, sequence_type)
            if cost == 0:
                cost += 0.001
        else:
            print "Should never happen in edit_distance_cost!"
            sys.exit(-1)

        return cost

    ## Computes the tree distance matrix between the subtree rooted at
    #    node i in tree 1 and node j in tree 2.
    #
    #  @param i   The position of the last node in subtree 1
    #    (position defined by postorder traversal)
    #  @param i   The position of the last node in subtree 2
    #    (position defined by postorder traversal)
    #  @param params Parameters required by Zhang-Shasha
    #  @precondition params['gamma'] != None as this is a function
    #    pointer to the edit-operation cost function.
    #  @precondition params['update_edit_cost'] != None as this
    #    contains our edit costs associated with updating the label
    #    of node i' to the label of node j'.
    #  @precondition params['insert_edit_cost'] != None
    #  @precondition params['delete_edit_cost'] != None
    #  @precondition params['tree_dist'] != None, this is the tree
    #    distance matrix that we update in the Zhang Shasha Algorithm
    #    as we iterate through the LR_keyroots in each parse tree
    #  @precondition params['edit_ops'] != None
    #  @precondition params['forest_dist'] != None.  This contains the
    #    distance between the forest induced by all nodes whose
    #    positions <= i and the forest induced by all nodes whose
    #    positions are <= j
    #  @return Updated params mentioned above.  Most notably, the tree
    #    distance between the subtrees rooted at nodes i and j.
    #  @note  Think about exceptions carefully...
    @staticmethod
    def treedist(i, j, params):

        # remember to include an extra row, col for the null set
        num_rows = i - params['l1'][i - 1] + 1 + 1
        num_cols = j - params['l2'][j - 1] + 1 + 1

        # forestdist, edit_ops, edit_cost are all indexed by node position
        forestdist = numpy.zeros([num_rows, num_cols])
        edit_ops = numpy.zeros([num_rows, num_cols])

        forestdist[0, 0] = 0

        l_i = params['l1'][i - 1]
        l_j = params['l2'][j - 1]

        # i1 is a position of a node in the subtree rooted at i
        for i1 in range(l_i, i + 1):
            t1_node_pos = i1
            t1_node_idx = i1 - l_i + 1

            t2_node_pos = 1
            t2_node_idx = 0
            delete_cost = params['gamma'](t1_node_pos, t2_node_pos, ZhangShashaTreeDist.DELETE, params)

            forestdist[t1_node_idx, t2_node_idx] = forestdist[t1_node_idx - 1, t2_node_idx] + delete_cost
            edit_ops[t1_node_idx, t2_node_idx] = ZhangShashaTreeDist.DELETE

        for j1 in range(l_j, j + 1):
            t1_node_pos = 1
            t1_node_idx = 0

            t2_node_pos = j1
            t2_node_idx = j1 - l_j + 1

            insert_cost = params['gamma'](t1_node_pos, t2_node_pos, ZhangShashaTreeDist.INSERT, params)

            forestdist[t1_node_idx, t2_node_idx] = forestdist[t1_node_idx, t2_node_idx - 1] + insert_cost
            edit_ops[t1_node_idx, t2_node_idx] = ZhangShashaTreeDist.INSERT

        for i1 in range(l_i, i + 1):
            for j1 in range(l_j, j + 1):
                t1_node_pos = i1
                t2_node_pos = j1

                t1_node_idx = i1 - l_i + 1
                t2_node_idx = j1 - l_j + 1

                l_i1 = params['l1'][t1_node_pos - 1]
                l_j1 = params['l2'][t2_node_pos - 1]

                if (l_i1 == l_i) and (l_j1 == l_j):
                    delete_cost = params['gamma'](t1_node_pos, t2_node_pos, ZhangShashaTreeDist.DELETE, params)
                    delete_dist = forestdist[t1_node_idx - 1, t2_node_idx] + delete_cost

                    insert_cost = params['gamma'](t1_node_pos, t2_node_pos, ZhangShashaTreeDist.INSERT, params)
                    insert_dist = forestdist[t1_node_idx, t2_node_idx - 1] + insert_cost

                    update_cost = params['gamma'](t1_node_pos, t2_node_pos, ZhangShashaTreeDist.UPDATE, params)
                    update_dist = forestdist[t1_node_idx - 1, t2_node_idx - 1] + update_cost

                    costs = [delete_cost, update_cost, insert_cost]
                    dists = [delete_dist, update_dist, insert_dist]

                    min_idx = dists.index(min(dists))

                    forestdist[t1_node_idx, t2_node_idx] = dists[min_idx]
                    edit_ops[t1_node_idx, t2_node_idx] = min_idx + 1

                    # tree dist is indexed from 0 to num nodes - 1
                    params['update_edit_cost'][t1_node_pos - 1, t2_node_pos - 1] = costs[ZhangShashaTreeDist.UPDATE - 1]
                    params['insert_edit_cost'][t1_node_pos - 1, t2_node_pos - 1] = costs[ZhangShashaTreeDist.INSERT - 1]
                    params['delete_edit_cost'][t1_node_pos - 1, t2_node_pos - 1] = costs[ZhangShashaTreeDist.DELETE - 1]
                    params['tree_dist'][t1_node_pos - 1, t2_node_pos - 1] = forestdist[t1_node_idx, t2_node_idx]
                else:
                    delete_cost = params['gamma'](t1_node_pos, t2_node_pos, ZhangShashaTreeDist.DELETE, params)
                    delete_dist = forestdist[t1_node_idx - 1, t2_node_idx] + delete_cost

                    insert_cost = params['gamma'](t1_node_pos, t2_node_pos, ZhangShashaTreeDist.INSERT, params)
                    insert_dist = forestdist[t1_node_idx, t2_node_idx - 1] + insert_cost

                    # tree dist is indexed from 0 to num nodes - 1.  The cost to update the current node pair
                    costs = [params['delete_edit_cost'][t1_node_pos - 1, t2_node_pos - 1],
                              params['update_edit_cost'][t1_node_pos - 1, t2_node_pos - 1],
                              params['insert_edit_cost'][t1_node_pos - 1, t2_node_pos - 1]]
                    update_cost = min(costs)
                    update_cost = params['update_edit_cost'][t1_node_pos - 1, t2_node_pos - 1]

                    # plus the forestdist of the previous node pair
                    l_i1_idx = l_i1 - l_i + 1
                    l_j1_idx = l_j1 - l_j + 1
                    update_dist = forestdist[l_i1_idx - 1, l_j1_idx - 1] + params['tree_dist'][t1_node_pos - 1, t2_node_pos - 1]

                    costs = [delete_cost, update_cost, insert_cost]
                    dists = [delete_dist, update_dist, insert_dist]
                    min_idx = dists.index(min(dists))

                    forestdist[t1_node_idx, t2_node_idx] = dists[min_idx]
                    edit_ops[t1_node_idx, t2_node_idx] = min_idx + 1

        params['edit_ops'] = edit_ops
        params['forest_dist'] = forestdist
        return params

    ## Compute the tree edit distance between tree 1 and tree 2
    #
    #  @param t1  First parse tree to compare (in canonical tree representation)
    #  @param t2  Second parse tree to compare (in canonical tree
    #     representation)
    #  @param init_params  TBD
    #  @return some parameters
    #  @details  params['labels1'] position-ordered list of node
    #    labels for tree 1 (t1)
    #  @details  params['labels2'] position-ordered list of node
    #    labels for tree 2 (t2)
    #  @details  params['l1']  positions of tree 1 leaf nodes
    #  @details  params['l2']  positions of tree 2 leaf nodes
    #  @details  params['tree_dist']  The distance between subtree
    #     at node w/ position i and node w/ position j
    #  @details  params['update_edit_cost'] Edit costs associated with
    #     updating the label of node i' to the label of node j'
    #  @details  params['insert_edit_cost'],
    #     params['delete_edit_cost']
    #  @details  params['edit_ops'] The edit operation to be taken at
    #     that (i',j') step (based upon what we did when we filled in the
    #     entry (i',j') in the tree dist matrix
    #  @note  Think about whether there are any exceptions
    @staticmethod
    def compute_tree_dist(t1, t2, init_params):

        # preprocessing
        params1 = {'LR_keyroots': {},
                    'l': [],
                    'labels': [],
                    'pos': 1}

        params2 = {'LR_keyroots': {},
                    'l': [],
                    'labels': [],
                    'pos': 1}

        #-- Compute labels
        [t1, params1] = ZhangShashaTreeDist.postorder_traverse(t1, params1, ZhangShashaTreeDist.compute_labels)
        [t2, params2] = ZhangShashaTreeDist.postorder_traverse(t2, params2, ZhangShashaTreeDist.compute_labels)

        #-- Compute l
        [t1, params1] = ZhangShashaTreeDist.postorder_traverse(t1, params1, ZhangShashaTreeDist.set_position_to_id)
        [t1, params1] = ZhangShashaTreeDist.postorder_traverse(t1, params1, ZhangShashaTreeDist.compute_l)

        [t2, params2] = ZhangShashaTreeDist.postorder_traverse(t2, params2, ZhangShashaTreeDist.set_position_to_id)
        [t2, params2] = ZhangShashaTreeDist.postorder_traverse(t2, params2, ZhangShashaTreeDist.compute_l)

        #-- Compute LR_keyroots
        [t1, params1] = ZhangShashaTreeDist.get_lr_keyroots(t1, params1)
        [t2, params2] = ZhangShashaTreeDist.get_lr_keyroots(t2, params2)

        # Setup the parameters
        Tree_dist = numpy.zeros([t1['id'], t2['id']])
        Node_uedit_cost = numpy.zeros([t1['id'], t2['id']])
        Node_iedit_cost = numpy.zeros([t1['id'], t2['id']])
        Node_dedit_cost = numpy.zeros([t1['id'], t2['id']])

        params = init_params
        params['labels1'] = params1['labels']
        params['labels2'] = params2['labels']
        params['l1'] = params1['l']
        params['l2'] = params2['l']
        params['tree_dist'] = Tree_dist
        params['update_edit_cost'] = Node_uedit_cost
        params['insert_edit_cost'] = Node_iedit_cost
        params['delete_edit_cost'] = Node_dedit_cost
        params['edit_ops'] = []

        for i_prime_idx in range(0, len(params1['LR_keyroots'])):
            for j_prime_idx in range(0, len(params2['LR_keyroots'])):
                i = params1['LR_keyroots'][i_prime_idx]
                j = params2['LR_keyroots'][j_prime_idx]
                params = ZhangShashaTreeDist.treedist(i, j, params)

        return params

    ## Method used to report an edit script from the dynamic
    #   programming matrices computed by Zhang and Shasha.
    #  @param[in] i  The largest 'version1' leaf position
    #  @param[in] j  The largest 'version2' leaf position
    #  @param[in] small_leaf1
    #  @param[in] small_leaf2
    #  @param[in] params  Parameters necessary to output an edit
    #     script
    #  @return An edit script to output
    #  @exception UnrecognizedEditOperation
    #  @note  We want to revisit the base cases for this when we
    #   refactor.  This is a secondary method to the output method in
    #   the XUDiff class.
    @staticmethod
    def output_edit_script(i, j, small_leaf1, small_leaf2, params):
        update_script = []
        delete_script = []
        insert_script = []
        edit_script = []

        while True:
            if i == 0 and j == 0:
                break
            elif i == 0 and j != 0:
                i = 1
            elif i != 0 and j == 0:
                j = 1

            operation = params['edit_ops'][i, j]
            current_dist = params['forest_dist'][i, j]

            if operation == ZhangShashaTreeDist.UPDATE:
                edit_cost = params['update_edit_cost'][i - 1, j - 1]
                update_script.append("U (" + str([current_dist, edit_cost]) + ") T1[" + str(i) + "]->T2[" + str(j) + "]")
                i = i - 1
                j = j - 1
            elif operation == ZhangShashaTreeDist.DELETE:
                edit_cost = params['delete_edit_cost'][i - 1, j - 1]
                delete_script.append("D (" + str([current_dist, edit_cost]) + ") T1[" + str(i) + "]")
                i = i - 1
            elif operation == ZhangShashaTreeDist.INSERT:
                edit_cost = params['insert_edit_cost'][i - 1, j - 1]
                insert_script.append("I (" + str([current_dist, edit_cost]) + ") T2[" + str(j) + "]")
                j = j - 1
            else:
                print "\nError displaying edit script " + str(operation) + str([i, j]) + "\n"
                sys.exit(-1)

        edit_script = delete_script + update_script + insert_script
        return edit_script
