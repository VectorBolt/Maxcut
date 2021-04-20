from qiskit import *
import networkx as nx

# Hamiltonians
def create_cost_unitary(graph, gamma):
    """Implement the cost unitary on a quantum circuit"""

    cost_unitary = QuantumCircuit(len(graph.nodes), name="Cost Unitary")
    weights = nx.get_edge_attributes(graph, 'weight').values() # Get weights from graph

    # Add corresponding gates for each edge
    for edge, weight in zip(graph.edges, weights):
        cost_unitary.cx(int(edge[0]), int(edge[1]))
        cost_unitary.rz(2*gamma*weight, int(edge[1]))
        cost_unitary.cx(int(edge[0]), int(edge[1]))
        cost_unitary.barrier() # Visually the unitary for each edge
    #cost_unitary.to_gate()
    return cost_unitary

def create_mixer_unitary(graph, beta):
    """Implement the mixer unitary on a quantum circuit"""
    mixer_unitary = QuantumCircuit(len(graph.nodes), name="Mixer Unitary")

    # Apply unitary for each node
    for node in graph.nodes:
        mixer_unitary.rx(2*beta, int(node))
        mixer_unitary.to_gate()
    return mixer_unitary

def create_qaoa_circuit(graph, params):
    """Create the full QAOA circuit for the graph with the given parameters."""
    num_of_iterations = int(len(params)/2)
    gammas = params[:num_of_iterations] # Let the first half of the params list be gamma parameters
    betas = params[num_of_iterations:] # Let the second half of the params list be beta parameters

    # Initialize Circuit
    qr = QuantumRegister(len(graph.nodes))
    cr = ClassicalRegister(len(graph.nodes))
    circuit = QuantumCircuit(qr, cr)

    # Put all qubits in superposition with hadamard gates
    circuit.h(qr)
    for iteration in range(num_of_iterations):
        # Get Cost and Mixer Unitaries
        cost_unitary = create_cost_unitary(graph, gammas[iteration])
        mixer_unitary = create_mixer_unitary(graph, betas[iteration])
        circuit.append(cost_unitary, qr)
        circuit.append(mixer_unitary, qr)

    circuit.measure(qr, cr)

    return circuit

def get_expectation(graph, counts):
    """Return the weighted average of the results of the quantum circuit."""
    energy = 0
    total_executions = 0
    for bit_string, frequency in counts.items():
        energy += frequency * graph.get_cut_size(bit_string)
        total_executions += frequency
    return energy / total_executions # Return the average
