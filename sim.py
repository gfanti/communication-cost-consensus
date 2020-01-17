from node import *
import numpy as np

import random
import math
import config

class Sim(object):
    def __init__(self, n, p=0.6, ticks=100):
        # Initialize fraction p of nodes to be 1's, rest 0's
        cutoff = math.floor(n * p)
        # number of nodes
        self.n = n
        # 1/n
        self.n_inv = 1.0 / self.n
        # fraction of 1's
        self.p = p
        # maximum number of simulation events
        self.ticks = ticks
        # true bit
        self.majority = random.getrandbits(1)
        # converged?
        self.converged = False

        # initialize nodes
        self.nodes = [Node(self.majority) for i in range(cutoff)] + \
                     [Node(1-self.majority) for i in range(n)[cutoff:]]

        # number of total communications executed
        self.comms = 0

        # Initial belief counts
        self.belief_counts = {0:0, 1: 0}
        self.belief_count_timeseries = {0:[], 1:[]}
        self.update_belief_counts()



    def run_sim(self):
        ''' Run the simulation '''
        # for i in range(self.ticks):
        i = 0
        while i < self.ticks:
            i += 1
            node = random.choice(self.nodes)
            self.process_tick(node)
            if config.plot_timeseries:
                for k in self.belief_counts.keys():
                    self.belief_count_timeseries[k] += [self.belief_counts[k]]

            if (i % 10 == 0) and (self.is_finished()):
                # print("Current tick", i)
                # self.print_states()
                break
        if not self.converged:
            print("Did not converge in ", i, " ticks")

        # Compute the average time elapsed by computing the total number of ticks executed
        # divided by the rate of ticks (n ticks/sec)
        time_elapsed = (i + 1) / float(self.n)
        return (self.comms, self.converged, time_elapsed, self.belief_count_timeseries)

    def is_finished(self):
        self.check_convergence()
        if self.converged:
            return True

        # If not converged, did it converge to  the wrong bit?
        if self.belief_counts[1-self.majority] == self.n:
            return True
        return False

    def process_tick(self, node):
        ''' Process node's clock tick. Basic algorithm where you adopt polled node's value'''

        node.counter += 1
        node2 = self.meet(node)
        node.polled_states += [node2.state]
        if node.counter >= 3:
                majority = int(np.mean(node.polled_states) > 0.5)
                if node.state != majority:
                    self.belief_counts[majority] += 1
                    self.belief_counts[1-majority]-= 1
                    node.state = majority
                node.counter = 0

    def check_convergence(self):
        if self.belief_counts[self.majority] == self.n:
            self.converged = True
        else:
            self.converged = False

    def print_states(self):
        for node in self.nodes:
            print(node.state)

    def meet(self, node):
        node2 = node
        while (node2 == node):
            node2 = random.choice(self.nodes)
        self.comms += 1
        return node2

    def update_belief_counts(self):
        self.belief_counts = {0:0, 1:0}
        for node in self.nodes:
            self.belief_counts[node.state] += 1


class SimpleSim(Sim):
    def __init__(self, n, p=0.6, ticks=100, C=10):
        # Initialize fraction p of nodes to be 1's, rest 0's
        cutoff = math.floor(n * p)
        # number of nodes
        self.n = n
        # 1/n
        self.n_inv = 1.0 / self.n
        # fraction of 1's
        self.p = p
        # true bit
        self.majority = random.getrandbits(1)
        # number of simulation events
        self.ticks = ticks
        # log n
        self.logn = math.log2(self.n)
        # converged?
        self.converged = False
        # C
        self.C = C

        # initialize nodes
        self.nodes = [SimpleNode(self.majority) for i in range(cutoff)] + \
                     [SimpleNode(1-self.majority) for i in range(n)[cutoff:]]

        # number of total communications
        self.comms = 0

        # type and belief counts
        self.type_counts = {ASPIRANT:0, EXPERT_EST: 0,
                            EXPERT_PUSH: 0, REGULAR:0, TERMINAL: 0}
        self.belief_counts = {0:0, 1: 0}
        self.update_type_counts()
        print("type counts",  self.type_counts)

        self.type_count_timeseries = {ASPIRANT:[self.type_counts[ASPIRANT]],
                                      EXPERT_EST: [self.type_counts[EXPERT_EST]],
                                      EXPERT_PUSH: [self.type_counts[EXPERT_PUSH]],
                                      REGULAR: [self.type_counts[REGULAR]],
                                      TERMINAL: [self.type_counts[TERMINAL]]}

        self.belief_count_timeseries = {0:[self.belief_counts[0]],
                                        1:[self.belief_counts[1]]}

        self.num_experts = 0

    def run_sim(self):
        ''' Run the simulation '''
        i = 0
        while i < self.ticks:
            i += 1
            node = random.choice(self.nodes)
            self.process_tick(node)
            # if i % 1000 == 0:
            #     print("i ", i)

            if config.plot_timeseries:
                for k in self.type_counts.keys():
                    self.type_count_timeseries[k] += [self.type_counts[k]]

                for k in self.belief_counts.keys():
                    self.belief_count_timeseries[k] += [self.belief_counts[k]]

            if (i % 300 == 0) and (self.is_finished()):
                break
        if not self.converged:
            print("Did not converge in ", i, " ticks")
            print("Final type counts", self.type_counts)
            print("Final belief counts", self.belief_counts)

        # Compute the average time elapsed by computing the total number of ticks executed
        # divided by the rate of ticks (n ticks/sec)
        time_elapsed = (i + 1) / float(self.n)
        return (self.comms, self.converged, time_elapsed,
                self.belief_count_timeseries,
                self.type_count_timeseries)

    def print_states(self):
        print("Current node types:")
        for node in self.nodes:
            print(node.type, node.state)

    def process_tick(self, node):
        ''' Process node's clock tick. Simple upper bound from paper'''
        # Expert selection phase
        if node.type == ASPIRANT:
            node2 = self.meet(node)
            if node.last_seen_bit == 0 and node2.state == 1:
                # Add one to the number of expert tuples
                node.num_expert_tuples += 1
                node.last_seen_bit = None
                # Check if passed threshold
                if node.num_expert_tuples >= math.log2(self.logn):
                    # An expert is born
                    node.type = EXPERT_EST
                    # Update types
                    self.type_counts[EXPERT_EST] += 1
                    self.type_counts[ASPIRANT] -= 1
                    self.num_experts += 1
            elif node.last_seen_bit == 1 and node2.state == 0:
                node.type = REGULAR
                # Update types
                self.type_counts[REGULAR] += 1
                self.type_counts[ASPIRANT] -= 1
                node.last_seen_bit = None
            elif node.last_seen_bit == node2.state:
                node.last_seen_bit = None
            elif node.last_seen_bit == None:
                node.last_seen_bit = node2.state
            else:
                print("ERROR")

        elif node.type == REGULAR:
            node.counter += 1
            if node.counter >= self.logn:
                node2 = self.meet(node)
                if node2.type == TERMINAL:
                    if node.state != node2.state:
                        self.belief_counts[node2.state] += 1
                        self.belief_counts[node.state] -= 1
                    node.state = node2.state

                    node.type = TERMINAL
                    # Update types
                    self.type_counts[TERMINAL] += 1
                    self.type_counts[REGULAR] -= 1

                node.counter = 0

        elif node.type == EXPERT_EST:
            node.counter += 1
            node2 = self.meet(node)
            node.polled_states += [node2.state]
            if node.counter >= self.C * self.logn:
                majority = int(np.mean(node.polled_states) > 0.5)
                if node.state != majority:
                    self.belief_counts[majority] += 1
                    self.belief_counts[node.state] -= 1
                    node.state = majority
                node.type = EXPERT_PUSH
                # Update types
                self.type_counts[EXPERT_PUSH] += 1
                self.type_counts[EXPERT_EST] -= 1

                node.counter = 0


        elif node.type == EXPERT_PUSH:
            node.counter += 1
            node2 = self.meet(node)
            if node2.type != TERMINAL:
                if node2.state != node.state:
                    self.belief_counts[node.state] += 1
                    self.belief_counts[node2.state] -= 1
                    node2.state = node.state


                # Update types
                self.type_counts[TERMINAL] += 1
                self.type_counts[node2.type] -= 1
                node2.type = TERMINAL

            if node.counter >= self.logn:
                node.type = TERMINAL
                # Update types
                self.type_counts[TERMINAL] += 1
                self.type_counts[EXPERT_PUSH] -= 1


    def is_finished(self):
        ''' Check if the simulation is done, either due to
        convergence or because convergence is now impossible'''
        self.check_convergence()
        if self.converged:
            return True

        # If not converged, did it converge to  the wrong bit?
        if self.belief_counts[1-self.majority] == self.n:
            return True

        # If still not converged, are the nodes all terminal or all regular?
        if (self.type_counts[TERMINAL] == self.n) or \
            (self.type_counts[REGULAR] == self.n):
            return True

        return False

    def update_type_counts(self):
        ''' Count the number of nodes in each type'''
        self.type_counts = {ASPIRANT:0, EXPERT_EST: 0,
                            EXPERT_PUSH: 0, REGULAR:0, TERMINAL: 0}
        for node in self.nodes:
            self.type_counts[node.type] += 1
            self.belief_counts[node.state] += 1


