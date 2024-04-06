from avl import AVLTree
from priority_queue import MaxPriorityQueue


class Order:
    def __init__(self, order_id, current_system_time, order_value, delivery_time, priority):
        self.order_id = order_id
        self.current_system_time = current_system_time
        self.order_value = order_value
        self.delivery_time = delivery_time
        self.priority = priority
        self.eta = 0  # Will be calculated when the order is inserted


class OrderManagementSystem:
    def __init__(self):
        self.priority_tree = AVLTree()
        self.eta_tree = AVLTree()
        self.orders = {}
        self.history = []
        self.pq = MaxPriorityQueue()

    def calculate_order_priority(self, order_value, current_system_time):
        value_weight = 0.3
        time_weight = 0.7
        normalized_order_value = order_value / 50
        return value_weight * normalized_order_value - time_weight * current_system_time

    def create_order(self, order_id, current_system_time, order_value, delivery_time):
        print_list = []

        priority = self.calculate_order_priority(order_value, current_system_time)
        order = Order(order_id, current_system_time, order_value, delivery_time, priority)

        self.collect_orders_less_than_current_time(current_system_time)

        in_order_successor = self.priority_tree.find_in_order_successor(priority)
        out_for_delivery = self.get_out_for_delivery(current_system_time)
        new_order_eta = current_system_time + delivery_time
        if in_order_successor:
            new_order_eta = in_order_successor.value.eta + in_order_successor.value.delivery_time + delivery_time

        elif out_for_delivery and out_for_delivery.value.eta + out_for_delivery.value.delivery_time > new_order_eta:
            new_order_eta = out_for_delivery.value.eta + out_for_delivery.value.delivery_time + delivery_time
        else:
            if not self.pq.is_empty() and len(self.history) > 0:
                if not self.pq.is_empty():
                    last_order, _ = self.pq.peek()
                    new_order_eta = last_order.eta + last_order.delivery_time + delivery_time
                else:
                    last_order = self.history[0]
                    new_order_eta = last_order.eta + last_order.delivery_time + delivery_time
        order.eta = new_order_eta

        # Insert the new order into both AVL trees
        self.priority_tree.insert(order.priority, order)
        self.eta_tree.insert(order.eta, order)

        # Store the order in the orders dictionary
        self.orders[order_id] = order

        # Update ETAs of all orders with priority lower than the current order
        updated_etas = self.update_lower_priority_orders_eta(priority, order.eta, order.delivery_time,
                                                             current_system_time)

        # Create output string with the format specified
        print_list.append(f"Order {order_id} has been created - ETA: {order.eta}")
        if updated_etas:
            print_list.append(f"Updated ETAs: " + ", ".join(f"[{oid}: {new_eta}]" for oid, new_eta in updated_etas))

        print_list += self.flush_pq()
        return print_list

    def collect_orders_less_than_current_time(self, current_system_time):
        orders_list = []
        self.collect_delivered_orders_from_eta_tree(current_system_time, self.eta_tree.root, orders_list)
        for order in orders_list:
            self.pq.push(order, order.eta)
            self.eta_tree.delete(order.eta)
            self.priority_tree.delete(order.priority)
            del self.orders[order.order_id]

    def flush_pq(self):
        ret = []
        while not self.pq.is_empty():
            order, _ = self.pq.pop()
            ret.append(f"Order {order.order_id} has been delivered at time {order.eta}")
            self.history.append(order)
        return ret

    def collect_delivered_orders_from_eta_tree(self, current_system_time, eta_tree, orders_list):
        if eta_tree:
            self.collect_delivered_orders_from_eta_tree(current_system_time, eta_tree.left, orders_list)
            if eta_tree.key <= current_system_time:
                orders_list.append(eta_tree.value)
                self.collect_delivered_orders_from_eta_tree(current_system_time, eta_tree.right, orders_list)

    def deliver_orders(self, current_system_time):
        # Initialize an empty list to hold strings describing delivered orders
        delivered_orders_output = []
        last_delivered = None

        # Iterate through orders in the eta_tree to find and deliver orders
        nodes_to_remove = []
        if self.eta_tree.root:
            current_node = self.eta_tree.get_min_node(self.eta_tree.root)
            while current_node and current_node.key <= current_system_time:
                delivered_order = current_node.value
                last_delivered = delivered_order
                delivered_orders_output.append(
                    f"Order {delivered_order.order_id} has been delivered at time {delivered_order.eta}"
                )
                nodes_to_remove.append(current_node.key)
                current_node = self.eta_tree.get_next_larger_node(current_node.key)

            # Remove delivered orders from the system
            for key in nodes_to_remove:
                order_to_remove = self.eta_tree.search(self.eta_tree.root, key)
                if order_to_remove:
                    self.eta_tree.delete(key)
                    self.priority_tree.delete(order_to_remove.value.priority)
                    del self.orders[order_to_remove.value.order_id]

        return delivered_orders_output, last_delivered

    def cancel_order(self, order_id, current_system_time):
        ret = []
        if order_id not in self.orders:
            print(f"Cannot cancel. Order {order_id} does not exist.")
            return ret

        order_to_cancel = self.orders[order_id]

        # Check if the order is out for delivery or has already been delivered
        if order_to_cancel.eta <= current_system_time or current_system_time > order_to_cancel.eta - order_to_cancel.delivery_time:
            ret.append(f"Cannot cancel. Order {order_id} has already been delivered or is out for delivery.")
            return ret

        # Collect IDs and old ETAs of all lower priority orders before cancellation
        lower_priority_orders = self.collect_lower_priority_orders(self.priority_tree.root, order_to_cancel.priority,
                                                                   current_system_time)

        self.priority_tree.delete(order_to_cancel.priority)
        self.eta_tree.delete(order_to_cancel.eta)
        del self.orders[order_id]
        ret.append(f"Order {order_id} has been canceled")

        for order in lower_priority_orders:
            self.eta_tree.delete(order.eta)
            order.eta -= 2 * order_to_cancel.delivery_time
            self.eta_tree.insert(order.eta, order)

        ret.append(f"Updated ETAs: " + ", ".join(f"[{order.order_id}: {order.eta}]" for order in lower_priority_orders))
        return ret

    def update_time(self, order_id, current_system_time, new_delivery_time):
        ret = []

        if order_id not in self.orders:
            print(f"Cannot update. Order {order_id} does not exist.")
            return ret

        order_to_update = self.orders[order_id]

        # Check if the order has been delivered or is out for delivery
        if order_to_update.eta <= current_system_time:
            ret.append(f"Cannot update. Order {order_id} has already been delivered.")
            return ret

        # Calculate new priority in case it depends on the time
        new_priority = order_to_update.priority

        # Remove the order from both AVL trees with the old values
        self.eta_tree.delete(order_to_update.eta)

        # Update the order's delivery time and ETA

        new_order_eta = 0
        new_order_eta = order_to_update.eta + new_delivery_time - order_to_update.delivery_time
        order_to_update.delivery_time = new_delivery_time

        order_to_update.eta = new_order_eta
        # Re-insert the order with the new values

        self.eta_tree.insert(order_to_update.eta, order_to_update)

        # Update the ETAs for all orders with lower priority
        updated_etas = self.update_lower_priority_orders_eta(new_priority, order_to_update.eta, order_to_update.delivery_time,
                                              current_system_time)

        updated_etas.append((order_id, order_to_update.eta))
        ret.append(f"Updated ETAs: " + ", ".join(f"[{oid}: {new_eta}]" for oid, new_eta in updated_etas))
        return ret

    def update_lower_priority_orders_eta(self, new_priority, new_order_eta, new_d_t, current_system_time):
        # Initialize a list to hold the updated ETAs
        updated_etas = []

        # Collect all orders with priority lower than the new order and not yet out for delivery
        lower_priority_orders = self.collect_lower_priority_orders(self.priority_tree.root, new_priority,
                                                                   current_system_time)
        out_for_delivery = self.get_out_for_delivery(current_system_time)
        # Iterate over the collected orders to update their ETAs
        for order in lower_priority_orders:

            if out_for_delivery and out_for_delivery.value and out_for_delivery.value.order_id == order.order_id:
                continue
            # Calculate new ETA for each order
            eta_to_assign = new_order_eta + new_d_t + order.delivery_time
            new_order_eta = eta_to_assign  # Update the baseline ETA for the next order

            # Update the order's ETA in both the priority tree and eta tree
            self.eta_tree.delete(order.eta)
            self.eta_tree.insert(eta_to_assign, order)

            # Update the order's ETA property
            order.eta = eta_to_assign

            # Add to the list of updated ETAs
            updated_etas.append((order.order_id, order.eta))

        return updated_etas

    def collect_lower_priority_orders(self, node, priority, current_system_time):
        # Method to collect orders with priority lower than given and not yet out for delivery
        if node is None:
            return []

        orders = []
        if node.key < priority:
            orders.append(node.value)
            orders += self.collect_lower_priority_orders(node.left, priority, current_system_time)
            orders += self.collect_lower_priority_orders(node.right, priority, current_system_time)
        else:
            orders += self.collect_lower_priority_orders(node.left, priority, current_system_time)

        # If current node has lower priority and is not out for delivery
        # if node.key < priority and (node.value.eta > current_system_time) and (node != self.priority_tree.root):
        #     orders.append(node.value)

        # # Traverse left subtree for potential orders
        # orders += self.collect_lower_priority_orders(node.left, priority, current_system_time)
        # # Traverse right subtree for potential orders
        # orders += self.collect_lower_priority_orders(node.right, priority, current_system_time)

        return orders

    def print_orders(self, time1, time2):
        ret = []
        # Retrieve the root of the eta_tree and pass it to the get_orders_in_range function
        orders_in_range = self.eta_tree.get_orders_in_range(self.eta_tree.root, time1, time2)
        if orders_in_range:
            order_ids = [order.order_id for order in orders_in_range]
            ret.append(f"Orders to be delivered: {order_ids}")
        else:
            ret.append("There are no orders in that time period.")
        return ret

    def get_rank_of_order(self, order_id):
        print_list = []
        if order_id not in self.orders:
            print(f"Order {order_id} does not exist.")
            return print_list

        order = self.orders[order_id]
        priority = order.priority  # Assuming priority is stored in the Order object

        # Now call get_rank from the priority_tree without passing the node
        rank = [0]
        # rank = self.priority_tree.get_rank(priority)
        count = self.eta_tree.get_rank_of_order(self.eta_tree.root, order.eta, rank)
        print_list.append(f"Order {order_id} will be delivered after {count[0]} orders.")
        return print_list

    def quit(self):
        return self.eta_tree.inorder_traversal(self.eta_tree.root)

    def print_order(self, order_id):
        ret = []
        # Check if the order exists in the system
        if order_id in self.orders:
            order = self.orders[order_id]
            ret.append(
                f"[{order.order_id}, {order.current_system_time}, {order.order_value}, {order.delivery_time}, {order.eta}]")
        else:
            ret.append(f"Order {order_id} does not exist.")
        return ret

    def find_previous_order(self, order_priority, current_system_time):
        # First, try to find an order being delivered or about to be delivered
        previous_order_in_delivery = self.find_order_in_delivery(current_system_time)
        if previous_order_in_delivery:
            return previous_order_in_delivery

        # If no order is in delivery, find by closest higher priority
        return self.priority_tree.find_previous_order(order_priority)

    def find_order_in_delivery(self, current_system_time):
        node = self.eta_tree.root
        previous_order = None

        while node:
            # If the order's ETA is before or exactly at the current system time and it's the latest so far
            if node.key + node.value.delivery_time <= current_system_time:
                previous_order = node.value
                # Try to find a closer ETA that's still before current_system_time
                node = node.right
            else:
                # If this order's ETA is after the current_system_time, ignore it
                node = node.left

        return previous_order

    def get_out_for_delivery(self, current_system_time):

        find_first_order = self.eta_tree.find_first_order(self.eta_tree.root)
        # Check if there is an order and if it's out for delivery
        if find_first_order is not None and current_system_time > (
                find_first_order.value.eta - find_first_order.value.delivery_time):
            return find_first_order
        return None

# Note: The AVLTree class would need to be extended with methods like `get_orders_in_range` and `get_rank`, which
# require traversal and comparison logic based on the trees' ordering (by priority or ETA).
# This is a conceptual implementation, assuming such functionality is available or could be implemented in the AVLTree class.
