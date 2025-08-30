"""Test suite for the skip list implementation.

To run tests on implementation with bugs, comment out line 20
and uncomment line 21.

Can be run using pytest:
    cd case_studies/skip_list
    pytest
And with probtest (if installed):
    cd case_studies/skip_list
    pytest --probtest --minp 0.25 --N 3

Author: Katrine Christensen <katch@itu.dk>
"""

import random
import copy
import pytest
import sys
from pathlib import Path
sys.path.insert(1, './src')
# sys.path.insert(1, './src_bugs')

import skip_list as sl

@pytest.fixture(scope="session")
def setup():
    """Setup of test suite which is run once before all tests are run.
    Determines the set of random keys and passes on the set of keys and
    skip list parameters used for the test session. Each test can acquire
    the returned values by using them as arguments.
    """
    R = 3
    max_level = 3
    p = 0.5

    # Generates R different keys
    keys = []
    for _ in range(R):
        random_key=random.randint(0,100)
        while keys.__contains__(random_key): 
            random_key =random.randint(0,100)
        keys.append(random_key)
        
    # For debugging: enable by running pytest -s
    print("\n")
    print("Random keys:", keys)
    print("Skip list parameters: p=",p, ", max_level=",max_level )

    return keys, p, max_level

@pytest.fixture()
def keys(setup):
    return setup[0]

@pytest.fixture()
def p(setup):
    return setup[1]

@pytest.fixture()
def M(setup):
    return setup[2]

############################ Validity helper methods ##############################

def valid_no_layers(l):
    """The number of layers never exceeds the maximum number of layers."""
    return len(l.heads) <= l.max_level

def all_layers_ordered(l):
    """All layers are ordered."""
    if len(l.heads)==0: return True
    for h in l.heads:
        current_node = h
        while current_node.next != None:
            if current_node.key > current_node.next.key: return False
            current_node = current_node.next
    return True

def raised_nodes_has_lower_pointers(l: sl.skip_list):
    """All nodes in layers higher than the bottom layer has a pointer
    to a lower node with the same key."""
    if len(l.heads)<=1: return True
    layer = len(l.heads)-1
    while layer!=0:
        l1 = l._nodes_at_level(layer)
        l2 = l._nodes_at_level(layer-1)

        for n1 in l1:
            if n1.lower == None: return False
            else:
                if n1.lower.key != n1.key: return False
                if not l2.__contains__(n1.lower): return False
        layer -=1
    return True

def no_bottom_nodes_has_lower_pointers(l):
    """No nodes in bottom layers should have pointers to nodes below them."""
    if len(l.heads)==0: return True
    current_node = l.heads[0]
    while current_node != None:
        if current_node.lower != None: return False
        current_node = current_node.next
    return True

def layers_subset(l: sl.skip_list):
    """A layer in a skip list should be a subset of the layer beneath it.
    """
    if len(l.heads) <= 1: return True
    i = len(l.heads)-1
    while True:
        layer1 = set(l._keys_at_level(i))
        layer2 = set(l._keys_at_level(i-1))
        if not layer1.issubset(layer2): return False
        i-=1
        if i-1<=0: break
    return True

def all_inserted_nodes_in_bottom_layer(inserted_nodes,l: sl.skip_list):
    """The bottom layer must contain all inserted nodes."""
    return inserted_nodes == set(l.to_list())

####################################################################################
################################## Validity ########################################

def test_valid_insertion(keys, p, M):
    try:
        l = sl.skip_list(p,M)
        for key in keys:
            l.insert_node(sl.Node(key))

        valid_no_layers(l)
        all_layers_ordered(l)
        raised_nodes_has_lower_pointers(l)
        no_bottom_nodes_has_lower_pointers(l)
        layers_subset(l)
        all_inserted_nodes_in_bottom_layer(set(keys),l)

    except:
        pytest.skip()
    else:
        assert valid_no_layers(l)
        assert all_layers_ordered(l)
        assert raised_nodes_has_lower_pointers(l)
        assert no_bottom_nodes_has_lower_pointers(l)
        assert layers_subset(l)
        assert all_inserted_nodes_in_bottom_layer(set(keys),l)

def test_valid_delete(keys, p,M):
    try:
        l = sl.skip_list(p,M)
        for key in keys:
            l.insert_node(sl.Node(key))
        
        random_key_to_delete = keys[random.randint(0,len(keys)-1)]
        S = set(keys)
        S.remove(random_key_to_delete)
        l.delete_node(random_key_to_delete)

        valid_no_layers(l)
        all_layers_ordered(l)
        raised_nodes_has_lower_pointers(l)
        no_bottom_nodes_has_lower_pointers(l)
        layers_subset(l)
        all_inserted_nodes_in_bottom_layer(S,l)
    except:
        pytest.skip()
    else:
        assert valid_no_layers(l)
        assert all_layers_ordered(l)
        assert raised_nodes_has_lower_pointers(l)
        assert no_bottom_nodes_has_lower_pointers(l)
        assert layers_subset(l)
        assert all_inserted_nodes_in_bottom_layer(S,l)

def test_valid_delete_all(keys, p, M):
    try:
        l = sl.skip_list(p,M)
        for key in keys:
            l.insert_node(sl.Node(key))

        #Delete all nodes in random order
        keys_remaining_to_delete = copy.deepcopy(keys)
        for _ in range(len(keys)):
            random_key_to_delete = keys_remaining_to_delete[
                random.randint(0,len(keys_remaining_to_delete)-1)
            ]
            keys_remaining_to_delete.remove(random_key_to_delete)
            l.delete_node(random_key_to_delete)
    
        valid_no_layers(l)
        all_layers_ordered(l)
        raised_nodes_has_lower_pointers(l)
        no_bottom_nodes_has_lower_pointers(l)
        layers_subset(l)
        all_inserted_nodes_in_bottom_layer(set(),l)
    except:
        pytest.skip()
    else:
        assert valid_no_layers(l)
        assert all_layers_ordered(l)
        assert raised_nodes_has_lower_pointers(l)
        assert no_bottom_nodes_has_lower_pointers(l)
        assert layers_subset(l)
        assert all_inserted_nodes_in_bottom_layer(set(),l)

def test_valid_search(keys, p, M):
    try:
        l = sl.skip_list(p,M)
        for key in keys:
            l.insert_node(sl.Node(key))

        l.search(keys[len(keys)-1])

        valid_no_layers(l)
        all_layers_ordered(l)
        raised_nodes_has_lower_pointers(l)
        no_bottom_nodes_has_lower_pointers(l)
        layers_subset(l)
        all_inserted_nodes_in_bottom_layer(set(keys),l)

    except:
        pytest.skip()
    else:
        assert valid_no_layers(l)
        assert all_layers_ordered(l)
        assert raised_nodes_has_lower_pointers(l)
        assert no_bottom_nodes_has_lower_pointers(l)
        assert layers_subset(l)
        assert all_inserted_nodes_in_bottom_layer(set(keys),l)

# ####################################################################################
# ###################################### Postconditions ##############################

def test_post_insertion_search(keys, p, M):
    try:
        l = sl.skip_list(p,M)

        # Inserts all keys in keys except the last one
        for key in keys:
            if key==keys[len(keys)-1]: break
            l.insert_node(sl.Node(key))

        # Inserts the last key and searches for this
        key_to_search_for = keys[len(keys)-1]
        node_to_search_for = sl.Node(key_to_search_for)
        l.insert_node(node_to_search_for)

        l.search(key_to_search_for).key == key_to_search_for

    except:
        pytest.skip()
    else:
        assert l.search(key_to_search_for).key == key_to_search_for

def test_post_deletion_search(keys, p, M):
    try:
        l = sl.skip_list(p,M)
        
        for key in keys:
            l.insert_node(sl.Node(key))

        l.delete_node(keys[len(keys)-1])

        l.search(keys[len(keys)-1]) == None
    except:
        pytest.skip()
    else:
        assert l.search(keys[len(keys)-1]) == None

def test_post_level_of_nodes_unchanged_after_insertion(keys, p, M):
    try:
        l = sl.skip_list(p,M)

        # Inserts all keys except last one
        for i in range(len(keys)):
            if i==len(keys)-1: break
            l.insert_node(sl.Node(keys[i]))
        
        levels_before = []
        for i in range(len(keys)):
            if i==len(keys)-1: break
            levels_before += [l.level_of_node(keys[i])]

        l.insert_node(sl.Node(keys[len(keys)-1]))

        levels_after = []
        for i in range(len(keys)):
            if i==len(keys)-1: break
            levels_after += [l.level_of_node(keys[i])]

        levels_before==levels_after
    except:
        pytest.skip()
    else:
        assert levels_before==levels_after

def test_post_level_of_nodes_unchanged_after_search(keys, p, M):
    try:
        l = sl.skip_list(p,M)

        # Inserts all keys 
        for i in range(len(keys)):
            l.insert_node(sl.Node(keys[i]))
        
        levels_before = []
        for i in range(len(keys)):
            levels_before += [l.level_of_node(keys[i])]

        l.search(keys[len(keys)-1])

        levels2_after = []
        for i in range(len(keys)):
            levels2_after += [l.level_of_node(keys[i])]

        levels_before==levels2_after
    except:
        pytest.skip()
    else: 
        assert levels_before==levels2_after

def test_post_level_of_other_nodes_unchanged_after_deletion(keys, p, M):
    try:
        l = sl.skip_list(p,M)

        # Inserts all keys except last one
        for i in range(len(keys)):
            if i==len(keys)-1: break
            l.insert_node(sl.Node(keys[i]))
        
        if l.contains_node(sl.Node(keys[len(keys)-1])):
            pytest.skip()
        else: l.insert_node(sl.Node(keys[len(keys)-1]))

        levels_before = []
        for i in range(len(keys)):
            if i==len(keys)-1: break
            levels_before += [l.level_of_node(keys[i])]

        l.delete_node(keys[len(keys)-1])

        levels_after = []
        for i in range(len(keys)):
            if i==len(keys)-1: break
            levels_after += [l.level_of_node(keys[i])]

        levels_before==levels_after
    except:
        pytest.skip()
    else:
        assert levels_before==levels_after

def test_post_level_of_deleted_nodes_changed_after_deletion(keys, p, M):
    try:
        l = sl.skip_list(p,M)

        # Inserts all keys 
        for i in range(len(keys)):
            l.insert_node(sl.Node(keys[i]))
        
        level_before = l.level_of_node(keys[len(keys)-1])

        l.delete_node(keys[len(keys)-1])

        level_after = l.level_of_node(keys[len(keys)-1])

        level_before != level_after
    except:
        pytest.skip()
    else:
        assert level_before != level_after

####################################################################################
############################# Metamorphic properties ###############################

def test_meta_insertion_order(keys, p, M):
    if len(keys)>1:
        try:
            l1 = sl.skip_list(p,M)
            l2 = sl.skip_list(p,M)

            # Inserts all nodes except the last two in keys
            for i in range(len(keys)):
                if i==len(keys)-2: break
                l1.insert_node(sl.Node(keys[i]))
                l2.insert_node(sl.Node(keys[i]))

            # Inserts the last two nodes in different orders
            key1 = keys[len(keys)-2]
            key2 = keys[len(keys)-1]

            l1.insert_node(sl.Node(key1))
            l1.insert_node(sl.Node(key2))
            
            l2.insert_node(sl.Node(key2))
            l2.insert_node(sl.Node(key1))

            l1.__equivalent__(l2)
        except:
            pytest.skip()
        else:
            assert l1.__equivalent__(l2)

def test_meta_insertion_order_same_key(keys, p, M):
    try:
        l1 = sl.skip_list(p,M)

        # Inserts all nodes except the last in keys
        for i in range(len(keys)):
            if i==len(keys)-1: break
            l1.insert_node(sl.Node(keys[i]))

        l1.insert_node(sl.Node(keys[len(keys)-1]))
        l2 = copy.deepcopy(l1)
        l1.insert_node(sl.Node(keys[len(keys)-1]))

        l1 == l2
    except:
        pytest.skip()
    else:
        assert l1 == l2

def test_meta_delete_insert_order(keys, p, M):
    if len(keys)>1:
        try:
            key1 = keys[len(keys)-2]
            key2 = keys[len(keys)-1]

            l1 = sl.skip_list(p,M)
            l2 = sl.skip_list(p,M)

            # Inserts all nodes except the last two in keys
            for i in range(len(keys)):
                if i==len(keys)-2: break
                l1.insert_node(sl.Node(keys[i]))
                l2.insert_node(sl.Node(keys[i]))

            l1.insert_node(sl.Node(key1))
            l1.delete_node(key1)
            l1.insert_node(sl.Node(key2))

            l2.insert_node(sl.Node(key1))
            l2.insert_node(sl.Node(key2))
            l2.delete_node(key1)

            l1.__equivalent__(l2)
        except:
            pytest.skip()
        else:
            assert l1.__equivalent__(l2)

def test_meta_insert_delete_same_node_order(keys, p, M):
    try:
        l1 = sl.skip_list(p,M)
        l2 = sl.skip_list(p,M)

        # Inserts all nodes except the last in keys
        for i in range(len(keys)):
            if i==len(keys)-1: break
            l1.insert_node(sl.Node(keys[i]))
            l2.insert_node(sl.Node(keys[i]))

        key = keys[len(keys)-1]

        l1.delete_node(key)
        l1.insert_node(sl.Node(key))
        
        l2.insert_node(sl.Node(key))

        l1.__equivalent__(l2)
    except:
        pytest.skip()
    else:
        assert l1.__equivalent__(l2)

def test_meta_delete_delete_order(keys, p, M):
    if len(keys)>1:
        try:
            key1 = keys[len(keys)-2]
            key2 = keys[len(keys)-1]

            l1 = sl.skip_list(p,M)

            # Inserts all nodes
            for i in range(len(keys)):
                l1.insert_node(sl.Node(keys[i]))

            l2 = copy.deepcopy(l1)

            l1.delete_node(key1)
            l1.delete_node(key2)

            l2.delete_node(key2)
            l2.delete_node(key1)

            l1 == l2
        except:
            pytest.skip()
        else: 
            assert l1 == l2

def test_meta_delete_same_node_twice(keys, p, M):
    try:
        l1 = sl.skip_list(p,M)

        # Inserts all nodes
        for i in range(len(keys)):
            l1.insert_node(sl.Node(keys[i]))

        l2 = copy.deepcopy(l1)

        key = keys[len(keys)-1]

        l1.delete_node(key)
        l1.delete_node(key)

        l2.delete_node(key)

        l1 == l2
    except:
        pytest.skip()
    else:
        assert l1 == l2

def test_meta_insertion_search_delete(keys, p, M):
    try:
        l = sl.skip_list(p,M)

        # Inserts all nodes
        for i in range(len(keys)):
            l.insert_node(sl.Node(keys[i]))

        key = keys[len(keys)-1]
        search_result1 = l.search(key)
        l.delete_node(key)
        search_result2 = l.search(key)

        search_result1 != search_result2
    except:
        pytest.skip()
    else:
        assert search_result1 != search_result2

def test_meta_search_insertion_delete(keys, p, M):
    try:
        l = sl.skip_list(p,M)

        # Inserts all nodes except last one in keys
        for i in range(len(keys)):
            if i==len(keys)-1: break
            l.insert_node(sl.Node(keys[i]))

        key = keys[len(keys)-1]

        search_result1 = l.search(key)
        l.insert_node(sl.Node(key))

        l.delete_node(key)
        search_result2 = l.search(key)

        search_result1 == search_result2
    except:
        pytest.skip()
    else:
        assert search_result1 == search_result2

####################################################################################
################################ Equivalence preservation ##########################

# Testing equality between skip lists

def test_eq_inserts_break_eq(keys, p, M):
    try:
        l1 = sl.skip_list(p,M)

        # Inserts all nodes except the last in keys
        for i in range(len(keys)):
            if i==len(keys)-1: break
            l1.insert_node(sl.Node(keys[i]))

        l2 = copy.deepcopy(l1)
        l1.insert_node(sl.Node(keys[len(keys)-1]))

        l1 != l2
    except:
        pytest.skip()
    else:
        assert l1 != l2

def test_eq_delete_break_eq(keys, p, M):
    try:
        l1 = sl.skip_list(p,M)

        for i in range(len(keys)):
            l1.insert_node(sl.Node(keys[i]))

        l2 = copy.deepcopy(l1)

        key = keys[len(keys)-1]
        l2.delete_node(key)
        
        l1 != l2
    except:
        pytest.skip()
    else:
        assert l1 != l2

def test_eq_delete(keys, p, M):
    try:
        l1 = sl.skip_list(p,M)

        for i in range(len(keys)):
            l1.insert_node(sl.Node(keys[i]))

        l2 = copy.deepcopy(l1)

        key = keys[len(keys)-1]
        l1.delete_node(key)
        l2.delete_node(key)
        
        l1 == l2
    except:
        pytest.skip()
    else:
        assert l1 == l2

def test_eq_search(keys, p, M):
    try:
        l1 = sl.skip_list(p,M)

        # Inserts all nodes 
        for i in range(len(keys)):
            l1.insert_node(sl.Node(keys[i]))

        l2 = copy.deepcopy(l1)

        l1.search(keys[len(keys)-1])

        l1 == l2
    except:
        pytest.skip()
    else:
        assert l1 == l2

# Testing equivalence relation of skip lists

def test_equiv_insert(keys, p, M):
    try:
        l1 = sl.skip_list(p,M)
        l2 = sl.skip_list(p,M)
        
        for i in range(len(keys)):
            l1.insert_node(sl.Node(keys[i]))
            l2.insert_node(sl.Node(keys[i]))

        l1.__equivalent__(l2)
    except:
        pytest.skip()
    else:
        assert l1.__equivalent__(l2)

def test_equiv_inserts_break_equiv(keys, p, M):
    try:
        l1 = sl.skip_list(p,M)
        l2 = sl.skip_list(p,M)

        # Inserts all keys except last one
        for i in range(len(keys)):
            if i==len(keys)-1: break
            l1.insert_node(sl.Node(keys[i]))

        l1.insert_node(sl.Node(keys[len(keys)-1]))

        not l1.__equivalent__(l2)
    except:
        pytest.skip()
    else:
        assert not l1.__equivalent__(l2)

def test_equiv_delete_break_equiv(keys, p, M):
    try:
        l1 = sl.skip_list(p,M)
        l2 = sl.skip_list(p,M)

        for i in range(len(keys)):
            l1.insert_node(sl.Node(keys[i]))
            l2.insert_node(sl.Node(keys[i]))

        key = keys[len(keys)-1]
        l2.delete_node(key)

        not l1.__equivalent__(l2)
    except:
        pytest.skip()
    else:
        assert not l1.__equivalent__(l2)

def test_equiv_delete(keys, p, M):
    try:
        l1 = sl.skip_list(p,M)
        l2 = sl.skip_list(p,M)

        for i in range(len(keys)):
            l1.insert_node(sl.Node(keys[i]))
            l2.insert_node(sl.Node(keys[i]))

        key = keys[len(keys)-1]
        l1.delete_node(key)
        l2.delete_node(key)

        l1.__equivalent__(l2)
    except:
        pytest.skip()
    else:
        assert l1.__equivalent__(l2)
