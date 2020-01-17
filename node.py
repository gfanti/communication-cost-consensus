ASPIRANT = 0
EXPERT_EST = 1
EXPERT_PUSH = 2
REGULAR = 3
TERMINAL = 4

class Node(object):
    def __init__(self, state):
        self.state = state
        self.counter = 0
        self.polled_states = []


class SimpleNode(Node):
    def __init__(self, state):
        super(SimpleNode, self).__init__(state)
        self.type = ASPIRANT
        self.num_expert_tuples = 0
        self.last_seen_bit = None