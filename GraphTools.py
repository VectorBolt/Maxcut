import networkx as nx
import random
import math
import numpy as np

# DWave imports
from collections import defaultdict
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

# Qiskit imports
from MyQAOA import *
from scipy.optimize import minimize


class MyGraph(nx.Graph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def weights(self):
        return nx.get_edge_attributes(self, "weight").values()

    @property
    def bitstrings(self):
        """A list of all possible bit strings that can represent the partitioning of the graph instance"""
        num_of_bits = len(list(self.nodes))
        bin_arr = range(0, int(math.pow(2,num_of_bits)))
        bin_arr = [bin(i)[2:] for i in bin_arr]

        # Prepending 0's to binary strings
        max_len = len(max(bin_arr, key=len))
        bin_arr = [i.zfill(max_len) for i in bin_arr]

        return bin_arr

    def get_cut_size(self, bitstring):
        """
        This function calculates the value of the cut associated with a given bitstring,
        meaning the weighted sum of all of the edges connecting two nodes belonging to opposite subsets.
        Since the classical optimizer is designed to compute a minimum instead of a maximum,
        we multiply our cut size by negative one.
        """
        cut_size = 0

        for edge, weight in zip(self.edges, self.weights):
            start_node = int(edge[0])
            end_node = int(edge[1])
            if bitstring[start_node] != bitstring[end_node]:
                """Since the classical optimizer is designed to compute a minimum instead of a maximum,
                decrement the cut size instead of incrementing it.
                """
                cut_size -= 1*weight
        return cut_size

    def solve_maxcut_classical(self):
        """Solve the Max Cut Problem for the graph classically"""
        all_possible_energies = {}
        for bitstring in self.bitstrings: 
            all_possible_energies[bitstring] = self.get_cut_size(bitstring)

        actual_solution = min(all_possible_energies, key=all_possible_energies.get)
        #actual_solution_cut_value = -1*self.get_cut_size(actual_solution) # Multiply by one to get a positive result
        
        return actual_solution

    def solve_maxcut_dwave(self, return_runtime = False):
        """Solve the Max Cut Problem for the graph using DWave"""
        Q = defaultdict(int)

        # Update Q matrix for every edge in the graph
        for edge, weight in zip(self.edges, self.weights):
            Q[(edge[0], edge[0])] += -1*weight
            Q[(edge[1], edge[1])] += -1*weight
            Q[(edge[0], edge[1])] += 2*weight

        # ------- Run our QUBO on the QPU -------
        # Set up QPU parameters
        chainstrength = 8
        numruns = 10
        # Run the QUBO on the solver from your config file
        sampler = EmbeddingComposite(DWaveSampler())

        response = sampler.sample_qubo(Q,
                               chain_strength=chainstrength,
                               num_reads=numruns,
                               label='Example - Maximum Cut')

        solution = list(response.first.sample.values())

        solution_bitstring = ""
        for i in solution:
            solution_bitstring += str(i)

        qpu_access_time = str(response.info["timing"]["qpu_access_time"]) + " microseconds"

        if return_runtime:
            return solution_bitstring, qpu_access_time
        else:
            return solution_bitstring

    def solve_maxcut_qiskit(self, depth):

        def objective(params):
            """Objective function for optimizer to minimize"""
            backend = Aer.get_backend("qasm_simulator")
            circuit = create_qaoa_circuit(self, params)
            counts = execute(circuit, backend).result().get_counts()
            counts = {key[::-1]:value for key, value in counts.items()} # Invert bitstrings because Qiskit uses different order
            return get_expectation(self, counts)

        init_params = [random.uniform(0,np.pi) for i in range(2*depth)]
        solution = minimize(objective, init_params, method = "COBYLA")

        # Rerun circuit with optimal params
        backend = Aer.get_backend("qasm_simulator")
        optimized_params = solution['x']
        optimal_circuit = create_qaoa_circuit(self, optimized_params)
        counts = execute(optimal_circuit, backend).result().get_counts()
        counts = {key[::-1]:value for key, value in counts.items()} # Invert bitstrings because Qiskit uses different order

        return max(counts, key=counts.get)

        
    def draw_original(self, pos):
        nx.draw(self, pos, with_labels = True, font_weight = 'bold')
        labels = nx.get_edge_attributes(self, 'weight')
        nx.draw_networkx_edge_labels(self, pos, edge_labels = labels)

    def draw_cut(self, pos, bitstring):
        S0 = [node for node in self.nodes if bitstring[node] == "0"]
        S1 = [node for node in self.nodes if bitstring[node] == "1"]

        cut_edges = [edge for edge in self.edges if bitstring[edge[0]] != bitstring[edge[1]]]
        uncut_edges = [edge for edge in self.edges if bitstring[edge[0]] == bitstring[edge[1]]]

        labels = nx.get_edge_attributes(self, 'weight')

        nx.draw_networkx_nodes(self, pos, nodelist=S0, node_color='r')
        nx.draw_networkx_nodes(self, pos, nodelist=S1, node_color='c')
        nx.draw_networkx_edges(self, pos, edgelist=cut_edges, style='dashdot', alpha=0.5, width=3)
        nx.draw_networkx_edges(self, pos, edgelist=uncut_edges, style='solid', width=3)
        nx.draw_networkx_labels(self, pos)
        nx.draw_networkx_edge_labels(self, pos, edge_labels=labels)



def generate_random_connected_graph(num_nodes, max_weight, num_edges=None):
    """Generate a connected networkx graph with a random number of nodes, edges, and weights"""

    # Use a random number of edges if no number is specified
    if num_edges is None:
        num_edges = random.randint(num_nodes-1, math.floor(num_nodes*(num_nodes-1)/2)) # Randomly choose the number of edges

    # Create a list of numbers up to the number of nodes, and shuffle it
    nodes = list(range(num_nodes))
    random.shuffle(nodes)

    edges = [] # A list of unweighted edges
    # Create randomly connected graph with the minimum number of edges
    for i in range(num_nodes-1):
        edges.append([nodes[i], nodes[i+1]])
        num_edges -= 1 # Decrement the total number of edges that haven't been generated yet

    # Randomly generate extra edges
    for i in range(num_edges):
        # Loop until a valid edge is found
        while True:
            start_node = random.randint(0, num_nodes)
            end_node = random.randint(0, num_nodes)
            # Must be a unique edge between two distinct points
            if (start_node != end_node and [start_node, end_node] not in edges):
                edges.append([start_node, end_node])
                break

    # Create graph from edges
    G = MyGraph()
    for edge in edges:
        rand_weight = round(random.uniform(0, max_weight), 2) # Weights can be floats. Round to the nearest hundredth
        G.add_edge(edge[0], edge[1], weight = rand_weight)
    return G

