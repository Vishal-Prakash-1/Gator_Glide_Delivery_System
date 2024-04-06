import heapq

class MaxPriorityQueue:
    def __init__(self):
        self.heap = []

    def push(self, item, priority):
        # The priority is inverted (negated) to simulate a max heap
        # The heap is organized based on the first element of the tuple
        heapq.heappush(self.heap, (-priority, item))

    def pop(self):
        # Remove and return the item with the highest priority (largest integer value)
        # Restore the item's original priority upon removal
        priority, item = heapq.heappop(self.heap)
        return item, -priority

    def peek(self):
        # Look at the next item without removing it, restoring its original priority
        if self.heap:
            priority, item = self.heap[0]
            return item, -priority
        return None, None

    def is_empty(self):
        return len(self.heap) == 0
