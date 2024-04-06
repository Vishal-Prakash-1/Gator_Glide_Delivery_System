# AVL tree implementation in Python


import sys

# Create a tree node
class TreeNode(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.height = 1
        self.left = None
        self.right = None

class AVLTree(object):
    def __init__(self):
        self.root = None

    def insert(self, key, value):
        if self.root is None:
            self.root = TreeNode(key, value)
        else:
            self.root = self._insert(self.root, key, value)

    # Function to insert a node
    def _insert(self, root, key, value):

        # Find the correct location and insert the node
        if not root:
            return TreeNode(key, value)
        elif key < root.key:
            root.left = self._insert(root.left, key, value)
        else:
            root.right = self._insert(root.right, key, value)

        root.height = 1 + max(self.getHeight(root.left),
                              self.getHeight(root.right))

        # Update the balance factor and balance the tree
        balanceFactor = self.getBalance(root)
        if balanceFactor > 1:
            if key < root.left.key:
                return self.rightRotate(root)
            else:
                root.left = self.leftRotate(root.left)
                return self.rightRotate(root)

        if balanceFactor < -1:
            if key > root.right.key:
                return self.leftRotate(root)
            else:
                root.right = self.rightRotate(root.right)
                return self.leftRotate(root)

        return root

    def delete(self, key):
        self.root = self._delete(self.root, key)

    # Function to delete a node
    def _delete(self, root, key):

        # Find the node to be deleted and remove it
        if not root:
            return root
        elif key < root.key:
            root.left = self._delete(root.left, key)
        elif key > root.key:
            root.right = self._delete(root.right, key)
        else:
            if root.left is None:
                temp = root.right
                root = None
                return temp
            elif root.right is None:
                temp = root.left
                root = None
                return temp
            temp = self.getMinValueNode(root.right)
            root.key = temp.key
            root.right = self._delete(root.right,
                                          temp.key)
        if root is None:
            return root

        # Update the balance factor of nodes
        root.height = 1 + max(self.getHeight(root.left),
                              self.getHeight(root.right))

        balanceFactor = self.getBalance(root)

        # Balance the tree
        if balanceFactor > 1:
            if self.getBalance(root.left) >= 0:
                return self.rightRotate(root)
            else:
                root.left = self.leftRotate(root.left)
                return self.rightRotate(root)
        if balanceFactor < -1:
            if self.getBalance(root.right) <= 0:
                return self.leftRotate(root)
            else:
                root.right = self.rightRotate(root.right)
                return self.leftRotate(root)
        return root

    # Function to perform left rotation
    def leftRotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self.getHeight(z.left),
                           self.getHeight(z.right))
        y.height = 1 + max(self.getHeight(y.left),
                           self.getHeight(y.right))
        return y

    # Function to perform right rotation
    def rightRotate(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self.getHeight(z.left),
                           self.getHeight(z.right))
        y.height = 1 + max(self.getHeight(y.left),
                           self.getHeight(y.right))
        return y

    # Get the height of the node
    def getHeight(self, root):
        if not root:
            return 0
        return root.height

    # Get balance factore of the node
    def getBalance(self, root):
        if not root:
            return 0
        return self.getHeight(root.left) - self.getHeight(root.right)

    def getMinValueNode(self, root):
        if root is None or root.left is None:
            return root
        return self.getMinValueNode(root.left)

    def preOrder(self, root):
        if not root:
            return
        print("{0} ".format(root.key), end="")
        self.preOrder(root.left)
        self.preOrder(root.right)

    # Print the tree
    def printHelper(self, currPtr, indent, last):
        if currPtr != None:
            sys.stdout.write(indent)
            if last:
                sys.stdout.write("R----")
                indent += "     "
            else:
                sys.stdout.write("L----")
                indent += "|    "
            print(currPtr.key)
            self.printHelper(currPtr.left, indent, False)
            self.printHelper(currPtr.right, indent, True)

    def search(self, node, key):
        if node is None or node.key == key:
            return node
        if key < node.key:
            return self.search(node.left, key)
        return self.search(node.right, key)

    def inorder_traversal(self, root):
        res = []
        if root:
            res = self.inorder_traversal(root.left)
            res.append(f"Order {root.value.order_id} has been delivered at time {root.key}")
            res = res + self.inorder_traversal(root.right)
        return res

    def get_orders_in_range(self, node, time1, time2):
        # This method collects orders with ETAs within the specified range
        if node is None:
            return []

        orders = []
        if time1 < node.key:
            orders += self.get_orders_in_range(node.left, time1, time2)

        if time1 <= node.key <= time2:
            orders.append(node.value)

        if time2 > node.key:
            orders += self.get_orders_in_range(node.right, time1, time2)

        return orders

    def find_previous_order(self, priority):
        current = self.root
        predecessor = None

        while current:
            if current.key < priority:
                # This node is a candidate for predecessor, go right to find a closer one
                predecessor = current
                current = current.right
            else:
                # Go left to find a smaller key
                current = current.left

        return predecessor.value if predecessor else None

    def get_rank_of_order(self, node, eta, rank):
        if not node:
            return 0
        if eta > node.key:
            left_count = self.count_number_of_nodes(node.left)
            rank[0] += 1 + left_count
            self.get_rank_of_order(node.right, eta, rank)
        elif eta < node.key:
            self.get_rank_of_order(node.left, eta, rank)
        else:
            left_count = self.count_number_of_nodes(node.left)
            rank[0] += left_count
        return rank

    def count_number_of_nodes(self, node):
        if not node:
            return 0
        return 1 + self.count_number_of_nodes(node.left) + self.count_number_of_nodes(node.right)

    def get_size(self, node):
        # If the node is None, then the size is 0
        if not node:
            return 0
        # Otherwise, return the size of the subtree
        return 1 + self.get_size(node.left) + self.get_size(node.right)

    def find_closest_higher_priority_order(self, order_priority, current_system_time):
        # This method starts the search from the root
        return self._find_closest_recursive(self.root, order_priority, current_system_time)

    def _find_closest_recursive(self, node, order_priority, current_system_time):
        if not node:
            return None

        # Assuming 'priority' and 'eta' are attributes of the order stored in the node
        if node.value.priority < order_priority and node.value.eta <= current_system_time:
            # Node meets criteria but might not be the closest, search right for a closer match
            right_search = self._find_closest_recursive(node.right, order_priority, current_system_time)
            return right_search if right_search else node.value
        else:
            # Node does not meet criteria, search left for a potential match
            return self._find_closest_recursive(node.left, order_priority, current_system_time)
    def find_in_order_successor(self, priority):
        current = self.root
        successor = None

        while current:
            if current.key > priority:
                # Current node is a potential successor. Go left to find a closer one if exists.
                successor = current
                current = current.left
            else:
                # Current node's key is not greater than the given priority, go right.
                current = current.right

        return successor

    def get_min_node(self, node):
        """
        Returns the node with the minimum key in the tree.
        The minimum key is found at the leftmost leaf node.
        """
        current = node
        while current.left is not None:
            current = current.left
        return current

    def get_next_larger_node(self, current_key):
        """
        Find the node with the smallest key that is greater than the given key.
        """
        current = self.root
        successor = None

        while current:
            if current.key > current_key:
                successor = current
                current = current.left  # Move left to find a smaller key that is still larger than current_key
            else:
                current = current.right  # Move right to find keys larger than current_key

        return successor

    def find_first_order(self, node):
        """
        Find the order with the earliest ETA (the leftmost node).
        """
        if node is None:
            return None  # Tree is empty

        current = node
        # Iteratively traverse to the leftmost node
        while current.left is not None:
            current = current.left
        return current
