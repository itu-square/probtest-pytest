"""Implementation of the randomized data structure skip list with injected bugs.
There are 8 bugs in total (see bottom of script). These can be injected one
by one by the global variable bug seen in line 14. 
Testing of the implementation can be run using pytest (however, one must import
this implementation instead as described in tests/test_skip_list.py).


Author: Katrine Christensen <katch@itu.dk>
"""
from typing import List, Union
from scipy.stats import bernoulli

global bug; bug=1

class Node:
    """Node in a skip list. Contains a key and two pointers: a next Node and a lower Node.
    A node only has a lower pointer if not in bottom layer of the skip list."""
    
    def __init__(self, key: int) -> None:
        """Initializes a node with the given key."""
        self.key = key
        self.next = None
        self.lower = None

    def __eq__(self, other) -> bool:
        """Returns whether two nodes are equal. In order to be equal, two nodes must 
        have the same key and the same pointers. 

        Called recursively to check equality of pointers.

        Args:
            other (Node): Other Node to compare this to.

        Returns:
            bool: Whether the two nodes are equal.
        """
        if self is None or other is None: return False
        elif self.key != other.key: return False
        else: return self.next == other.next and self.lower == other.lower

    def __equivalent__(self, other) -> bool:
        """Returns whether two nodes are equivalent. In order for this, two nodes must
        have the same keys, but not necessarily the same pointers.

        Args:
            other (Node): Other Node to compare this to.

        Returns:
            bool: Whether the two nodes are equivalent.
        """
        if self is None or other is None: return False
        else: return self.key == other.key

    def __str__(self) -> str:
        """String representation of a node. Returns the key and the key of its two pointers.
        E.g.: 1 (next: 2, lower: 1)

        When printing a node, this method is called.

        Returns:
            string: String representation of node.
        """
        if self.next == None and self.lower==None:                      # pragma: no mutate
            return str(self.key) + " (next: None, lower: None)"         # pragma: no mutate
        elif self.next == None:                                         # pragma: no mutate
            return str(self.key) + " (next: None, lower: "+str(self.lower.key)+")"  # pragma: no mutate
        elif self.lower == None:                                        # pragma: no mutate
            return str(self.key) + " (next: "+str(self.next.key)+", lower: None)"   # pragma: no mutate
        else:                                                           # pragma: no mutate
            return str(self.key) + " (next: "+str(self.next.key)+", lower: "+str(self.lower.key)+")"    # pragma: no mutate

class skip_list:
    """Randomized data structure for fast insert, search and delete.
    
    Consists of layered ordered linked lists where nodes have lower pointers that points
    to a node with the same key in a linked list below the current one.

    All (public) methods except insert are deterministic. When inserting a node, a coin
    is tossed for whether it should also be inserted in (or raised to) the layer above.
    If a node is being raised, the coin is tossed again and so on.

    Class variables:
        heads: A list of pointers to nodes. Each pointer is a head of an ordered linked list.
        p: The probability of raising a node after inserting it in the skip list.
        max_level: The maximum number of levels in the skip list.
    """

    def __init__(self, p: float, max_level: int) -> None:
        """Initializes a skip list with the given parameters."""
        self.p = p
        self.heads = []
        self.max_level = max_level

    def __eq__(self,other) -> bool:
        """For two lists to be equal, all pointers and nodes must be the same.

        First checks whether the two lists has the same parameters (p and max_level) and the same list of heads.
        When checking the lists of heads, it checks that the Node elements they contain are the same 
        (using eq on nodes).

        Args:
            other (skip_list): The other skip list to compare this to.

        Returns:
            bool: Whether the two skip lists are equal.
        """
        return self.p == other.p and self.max_level==other.max_level and self.heads==other.heads
    
    def __equivalent__(self,other) -> bool:
        """Equivalence relation on skip lists.

        For two lists to be equivalent, they must have the same parameters and nodes inserted,
        but may differ in shape.

        Args:
            other (skip_list): The other skip list to compare this to.

        Returns:
            bool: Whether the two skip lists are equivalent.
        """
        return self.p == other.p and self.max_level==other.max_level and self.to_list()==other.to_list()

    def __str__(self) -> str:
        """String representation of a skip list. Does not show the lower pointers."""
        final_s = ""                            # pragma: no mutate
        if self.heads == []: return "None"      # pragma: no mutate
        else:                                   # pragma: no mutate
            for h in reversed(self.heads):      # pragma: no mutate
                s = ""                          # pragma: no mutate
                while h!=None:                  # pragma: no mutate
                    s+= str(h.key) + " -> "     # pragma: no mutate
                    h = h.next                  # pragma: no mutate
                final_s += s + " None\n"        # pragma: no mutate
        return final_s                          # pragma: no mutate
        
    def search(self, key: int) -> Union[Node,None]:
        """Searches for a node with the given key in the skip list. 
        Returns the found node or None.

        Args:
            key (int): The key we are searching for.
        
        Returns:
            Node | None: A node with the given key (at the bottom layer) if it exists in the list. 
            Or None if it does not exist.
        """
        if not isinstance(key,int): # pragma: no mutate 
            raise ValueError("The key must be of type int") # pragma: no mutate

        if len(self.heads)==0: return None
        _,_,node = self._search_from_node(key, self.heads[len(self.heads)-1], None, len(self.heads)-1)
        return node 

    def delete_node(self,key: int) -> None:
        """Deletes node with specified key if it exists in the skip list.

        Args:
            key (int): The key for which node we are trying to delete.
        """
        if not isinstance(key,int): # pragma: no mutate
            raise ValueError("The key must be of type int") # pragma: no mutate

        # if the list is empty, we stop
        if len(self.heads)==0: return
        
        # Find the highest node with the given key
        level, prev_node, node = self._search_from_node(key,self.heads[len(self.heads)-1],None,len(self.heads)-1)

        if node == None: return #if no node found or reached level 0, we are done
        elif prev_node == None: #if the found node is a head, we update the head pointer
            self.heads[level] = node.next
            if node.next == None: self.heads.remove(None)
        else:
            prev_node.next = node.next
        return self.delete_node(key)
        
    def contains_node(self,node: Node) -> bool:
        """Returns whether the given node exists in the skip list.

        Calls the helper method search_from_node to find the first occurrence (if any) of the given node,
        starting the search from the top.

        Args:
            node (Node): The node we are searching for.

        Returns:
            bool: Whether the skip list contains the given node.
        """
        if not isinstance(node.key,int): # pragma: no mutate
            raise ValueError("The key must be of type int") # pragma: no mutate

        if len(self.heads)==0: return False

        _,_,found_node = self._search_from_node(node.key,self.heads[len(self.heads)-1],None,len(self.heads)-1)
        return found_node != None
    
    def level_of_node(self,key: int) -> int:
        """Returns the level of a node, i.e. the highest layer at which it appears.
        Returns -1 if the node does not appear in the list.

        Args:
            key (int): The key we are searching for.

        Returns:
            int: The level of the given node.
        """
        if not isinstance(key,int): # pragma: no mutate
            raise ValueError("The key must be of type int") # pragma: no mutate

        if len(self.heads)==0: return -1
        level,_,node = self._search_from_node(key,self.heads[len(self.heads)-1],None,len(self.heads)-1)
        if node != None: return level
        else: return -1
        
    def insert_node(self,node: Node) -> None: 
        """Inserts the given node in the skip list.

        If the node already exists in the list, nothing is done.

        Calls the helper method insert_node_from to recursively find the correct place for insertion.
        Starts the search from the top of the list.

        Args:
            node (Node): The node to be inserted.
        """
        if not isinstance(node.key,int): # pragma: no mutate
            raise ValueError("The key must be of type int") # pragma: no mutate

        if len(self.heads)==0: self._insert_node_after_node(node,None,0) #if empty list, we simply insert the node
        elif self.contains_node(node): return #if already exists, we shouldn't put it in twice
        else: self._insert_node_from(node,None,self.heads[len(self.heads)-1],len(self.heads)-1)

    def to_list(self) -> List[int]:
        """Returns a list of the keys in the list (i.e. the bottom layer of nodes).

        Returns:
            List[int]: A list of the keys in the list.
        """
        return self._keys_at_level(0)
    
    def _nodes_at_level(self, level: int) -> List[Node]:
        """Returns a list with all the nodes at the given level.

        Args:
            level (int): The level of the list we are looking at.
        """
        if level >= self.max_level or level<0: 
            return ValueError("The given level does not exist.") # pragma: no mutate
        if level >= len(self.heads): return []
        l = []
        current_node = self.heads[level]
        while current_node != None:
            l.append(current_node)
            current_node = current_node.next
        return l
    
    def _keys_at_level(self, level: int) -> List[int]:
        """Returns a list with all the keys at the given level.

        Args:
            level (int): The level of the list we are looking at.
        """
        if level >= self.max_level or level<0: 
            return ValueError("The given level does not exist.") # pragma: no mutate

        l_nodes = self._nodes_at_level(level)
        l_keys = []
        for n in l_nodes:
            l_keys.append(n.key)
        return l_keys

    def _insert_node_from(self, node: Node, prev_node: Node, from_node: Node, level: int) -> None:
        """Recursive function to find the correct place for insertion of the given node.
        Once found, inserts the node using helper methods insert_node_after_node.

        Args:
            node (Node): The node for insertion.
            prev_node (Node): The previous node we looked at.
            from_node (Node): The current node we are comparing the given node to.
            level (int): The current level we are searching in.
        """
        # if we have reached the end without inserting it anywhere, we insert it
        if level==0 and from_node==None: return self._insert_node_after_node(node,prev_node,level)
        elif node.key < from_node.key:
            #we go left and down if possible, otherwise we have found the place to insert it
            if level > 0:
                if prev_node == None: #then we are at the head, so we go down to the next layer
                    return self._insert_node_from(node,None,self.heads[level-1],level-1)
                else: #otherwise we go down by the node to the left
                    return self._insert_node_from(node,None,prev_node.lower,level-1)
            else:
                if prev_node == None: return self._insert_node_after_node(node,None,level)
                else: return self._insert_node_after_node(node,prev_node,level)
        else:
            if from_node.next != None or level == 0: 
                return self._insert_node_from(node,from_node,from_node.next,level) # we go right
            else: return self._insert_node_from(node,None,from_node.lower,level-1) # we go down

    def _search_from_node(self, key: int, node: Node, prev_node: Node, level: int
                          ) -> Union[tuple[int,Node,Node],None]:
        """Recursive function that searches for a node with the given key in a skip list.
        Starts the search at the given node with possibility to go left via prev_node if specified.

        Args:
            key (int): The key we are searching for.
            node (Node): The current node we are looking at.
            prev_node (Node): The previous node we looked at. If not None, then prev_node.next == node.
            level (int): The current level we are searching in.

        Returns:
            Node | None: If Node, the node will have the key that we have searched for.
        """
        if key == node.key: return (level, prev_node, node)
        elif key < node.key:
            # we go left and down if possible
            if prev_node != None:
                if prev_node.lower != None: return self._search_from_node(key, prev_node.lower, None, level-1)
                else:
                    if level > 0: return self._search_from_node(key,self.heads[level-1],None, level-1)
                    else: return (level, prev_node, None)
            else: #go down a layer from heads if possible
                if level > 0: return self._search_from_node(key,self.heads[level-1],None, level-1)
                else: return (level, prev_node, None)
        else:
            # we go to the right if possible or down a layer (from the head) if possible
            if node.next != None: return self._search_from_node(key,node.next, node, level)
            else: 
                if level > 0: return self._search_from_node(key,self.heads[level-1],None, level-1)
                else: return (level, prev_node, None)

    def _insert_node_after_node(self,node: Node,after_node: Node,level: int) -> None:
        """Inserts the given node after the other node at the given level.
        If the second node is None, the node is inserted at the head of the given level.
        Then flips a coin for whether the newly inserted coin should be raised.

        Example: Inserting 9 after 8 in 8 -> 10 results in 8 -> 9 -> 10

        Args:
            node (Node): The node to be inserted.
            after_node (Node): The node for which the inserted node must be inserted after.
            level (int): The level at which we are inserting (used for the potential call of raise_node_to_level)
        """
        if after_node==None: #insert at head
            if level > len(self.heads)-1:
                self.heads.append(node)
            else:
                node.next = self.heads[level]
                self.heads[level] = node
        else:
            node.next = after_node.next
            after_node.next = node

        if bernoulli(self.p).rvs()==1: self._raise_node_to_level(node,level+1)

    def _raise_node_to_level(self,node: Node,level: int) -> None:
        """Raises the given node to the given level.

        Creates a new node n1 with the same key as the given node and sets n1's lower to the given node.
        Then finds the correct placement of the new node n1 and inserts it in the list by calling
        insert_node_after_node (which may raise the node recursively).

        Args:
            node (Node): The node to be raised.
            level (int): The level at which we are raising the node to.
        """
        if level<=0: raise ValueError("Cannot raise a node to bottom layer or layers below this.") # pragma: no mutate

        if level>= self.max_level: return

        new_node = Node(node.key)
        new_node.lower = node

        # if the level does not already exist, we create it by creating a new head pointer:
        if level > len(self.heads)-1: self._insert_node_after_node(new_node,None,level)
        else:
            current = self.heads[level]
            if current.key > node.key: self._insert_node_after_node(new_node,None,level)
            else:
                current = self.heads[level]
                if current.next != None:
                    while current.next.key < node.key:
                        if current.next.next == None:
                            current = current.next
                            break
                        current = current.next
                self._insert_node_after_node(new_node,current,level)

    ################################## Injected bugs ###########################################

    ### BUG 1 ###
    if bug==1:
        def delete_node(self,key: int):
            if not isinstance(key,int): # pragma: no mutate
                raise ValueError("The key must be of type int") # pragma: no mutate

            # if the list is empty, we stop
            if len(self.heads)==0: return
            
            # Find the highest node with the given key
            level, prev_node, node = self._search_from_node(key,self.heads[len(self.heads)-1],None,len(self.heads)-1)

            if level == self.max_level-1: return # <- bug

            if node == None: return #if no node found or reached level 0, we are done
            elif prev_node == None: #if the found node is a head, we update the head pointer
                self.heads[level] = node.next
                if node.next == None: self.heads.remove(None)
            else:
                prev_node.next = node.next
            return self.delete_node(key)

    ### BUG 2 ###
    if bug==2:
        def _raise_node_to_level(self,node: Node,level: int):
            if level<=0: raise ValueError("Cannot raise a node to bottom layer or layers below this.") # pragma: no mutate

            if level>= self.max_level: return

            new_node = Node(node.key)
            new_node.lower = node

            # if the level does not already exist, we create it by creating a new head pointer:
            if level > len(self.heads)-1: self._insert_node_after_node(new_node,None,level)
            else:
                current = self.heads[level]
                if current.key > node.key: self._insert_node_after_node(new_node,None,level)
                else:
                    current = self.heads[level]
                    if current.next != None:
                        while current.next.key < node.key:
                            if current.next.next == None:
                                current = current.next
                                break
                            current = current.next
                    self._insert_node_after_node(new_node,current,level)

            # injected bug:
            if level>1:
                bottom_layer_node = self.search(node.key)
                while bottom_layer_node.lower != None:
                    bottom_layer_node = bottom_layer_node.lower
                bottom_layer_node.lower = Node(node.key)


    ### BUG 3 ###
    if bug==3:
        def insert_node(self,node: Node) -> None: 
            if not isinstance(node.key,int): # pragma: no mutate
                raise ValueError("The key must be of type int") # pragma: no mutate

            if len(self.heads)==0: self._insert_node_after_node(node,None,0) #if empty list, we simply insert the node
            elif self.contains_node(node): return #if already exists, we shouldn't put it in twice
            else: self._insert_node_from(node,None,self.heads[len(self.heads)-1],len(self.heads)-1)

            # bug:
            if len(self._keys_at_level(self.max_level-1))>=2:
                self.heads[self.max_level-1] = None
                self.heads.remove(None)

    ### BUG 4 ###
    if bug==4:
        def search(self, key: int) -> Union[Node,None]:
            if not isinstance(key,int): # pragma: no mutate 
                raise ValueError("The key must be of type int") # pragma: no mutate

            if len(self.heads)==0: return None
            level,_,node = self._search_from_node(key, self.heads[len(self.heads)-1], None, len(self.heads)-1)

            if level>0:
                if len(self._keys_at_level(level))>=2:
                    node.key -= 1
            return node 

    ### BUG 5 ###            
    if bug==5:
        def level_of_node(self,key: int) -> int:
            if not isinstance(key,int): # pragma: no mutate
                raise ValueError("The key must be of type int") # pragma: no mutate

            if len(self.heads)==0: return -1
            level,_,node = self._search_from_node(key,self.heads[len(self.heads)-1],None,len(self.heads)-1)

            if level==self.max_level-1 and len(self._keys_at_level(self.max_level-1))>=3:
                return 0

            if node != None: return level
            else: return -1

    ### BUG 6 ###
    if bug==6:
        def insert_node(self,node: Node) -> None: 
            if not isinstance(node.key,int): # pragma: no mutate
                raise ValueError("The key must be of type int") # pragma: no mutate

            if len(self.heads)==0: self._insert_node_after_node(node,None,0) #if empty list, we simply insert the node
            elif self.contains_node(node): return #if already exists, we shouldn't put it in twice
            else: self._insert_node_from(node,None,self.heads[len(self.heads)-1],len(self.heads)-1)

            if len(self._nodes_at_level(0))>=3:
                levels = set()
                for key in self.to_list():
                    levels.add(self.level_of_node(key))
                if len(levels)==1:
                    level = levels.pop()
                    for node in self._nodes_at_level(level):
                        self._raise_node_to_level(node,level+1)

    ### BUG 7 ###
    if bug==7:
        def search(self, key: int) -> Union[Node,None]:
            if not isinstance(key,int): # pragma: no mutate 
                raise ValueError("The key must be of type int") # pragma: no mutate

            if len(self.heads)==0: return None
            level,_,node = self._search_from_node(key, self.heads[len(self.heads)-1], None, len(self.heads)-1)
            if level==self.max_level-1 and len(self._nodes_at_level(self.max_level-1))>=4:
                return node.next
            return node 

    ### BUG 8 ###
    if bug==8:
        def search(self, key: int) -> Union[Node,None]:
            if not isinstance(key,int): # pragma: no mutate 
                raise ValueError("The key must be of type int") # pragma: no mutate

            if len(self.heads)==0: return None
            level,prev_node,node = self._search_from_node(key, self.heads[len(self.heads)-1], None, len(self.heads)-1)
            if level>0 and len(self.to_list())>=4 and prev_node==None:
                return None
            return node 
