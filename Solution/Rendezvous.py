#Python script for the solution to a Quantum Approach to the Rendezvous problem

import numpy as np
from qiskit import IBMQ, BasicAer, Aer
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute
from qiskit.providers.ibmq import least_busy
import matplotlib.pyplot as plt


def oracle(maze, alice_room, bob_room, q_oracle, q_oracle_ancilla):
    ''' Oracle function defined for Grover's search algorithm '''
    n = int(alice_room.size/2)
    for i in range(n):
        maze.cx(alice_room[i], bob_room[i])
        maze.x(bob_room[i])
        maze.x(bob_room[i+1])
        maze.cx(alice_room[i+1], bob_room[i+1])
        maze.ccx(bob_room[i], bob_room[i+1], q_oracle[i])
    maze.barrier()
    maze.cx(q_oracle, q_oracle_ancilla)
    maze.barrier() # f inverse
    for i in range(n):
        maze.ccx(bob_room[i], bob_room[i+1], q_oracle[i])
        maze.cx(alice_room[i+1], bob_room[i+1])
        maze.x(bob_room[i])
        maze.cx(alice_room[i], bob_room[i])
        maze.x(bob_room[i+1])
    maze.barrier()
    

def phase_shift(maze, rooms):
    ''' Phase amplification function defined for Grover's search algorithm '''
    n = int(rooms.size / 2)
    maze.h(rooms)
    maze.x(rooms)
    for i in range(n):
        maze.h(rooms[i + 1])
        maze.cx(rooms[i], rooms[i + 1])
        maze.h(rooms[i + 1])
    maze.x(rooms)
    maze.h(rooms)
    maze.barrier()
    
    
def state_preparation(n):
    ''' State Preparation defined for Grover's search algorithm '''
    n_oracle = int(n/2)
    alice_room = QuantumRegister(n)
    bob_room = QuantumRegister(n)
    maze = QuantumCircuit(alice_room)
    maze.add_register(bob_room)
    maze.h(alice_room)
    maze.h(bob_room)
    q_oracle= QuantumRegister(n_oracle)
    q_oracle_ancilla = QuantumRegister(n_oracle)
    c_alice = ClassicalRegister(n)
    c_bob = ClassicalRegister(n)
    maze.add_register(q_oracle)
    maze.add_register(q_oracle_ancilla)
    maze.add_register(c_alice)
    maze.add_register(c_bob)
    maze.x(q_oracle_ancilla)
    maze.h(q_oracle_ancilla)
    maze.barrier()
    return maze, alice_room, bob_room, q_oracle, q_oracle_ancilla, c_alice, c_bob

    
def rendezvous(n_rooms, n_iteration, n_shots):
    ''' The main function to run the algorithm for the Rendezvous problem '''
    maze, alice_room, bob_room, q_oracle, q_oracle_ancilla, c_alice, c_bob = state_preparation(n_rooms)
    for i in range(n_iteration):
        oracle(maze, alice_room, bob_room, q_oracle, q_oracle_ancilla)
        phase_shift(maze, bob_room)
        oracle(maze, alice_room, bob_room, q_oracle, q_oracle_ancilla)
        phase_shift(maze, alice_room)
    maze.measure(alice_room, c_alice)
    maze.measure(bob_room, c_bob)

    # Load on real device
    # IBMQ.load_account()
    # provider = IBMQ.get_provider(hub='ibm-q')
    # backend = least_busy(provider.backends(simulator=True))
    # counts = execute(maze, backend).result().get_counts()

    counts = execute(maze, Aer.get_backend('qasm_simulator'), shots=n_shots). \
            result().get_counts()
    winners = [counts.get(k) for k in counts.keys() if k[:n_rooms] == k[n_rooms + 1:n_rooms * 2 + 1]]
    prob_success = sum(winners) / n_shots
    print(counts)
    print("done!")
    print("number of iterations: ", n_iteration)
    print("probability of success: ", prob_success)
    maze.draw(output='mpl', filename='alice-bob')
    return counts, prob_success


def plot_counts(counts, n_rooms, n_iteration):
    ''' The function defined to plot the result of our algorithm'''
    count_value = [counts.get(k) for k in counts.keys()]
    count_label = [k for k in counts.keys()]
    x = np.arange(len(counts))
    plt.bar(x, height=count_value)
    plt.xticks(x, count_label)
    plt.title('Number of rooms for each pawn: ' + str(n_rooms) +
              ', Number of iterations: ' + str(n_iteration))


# Script to run the algorithm              
n_iteration = 2
n_rooms = 2
n_shots = 1024
counts, prob_success = rendezvous(n_rooms, n_iteration, n_shots)
plot_counts(counts, n_rooms, n_iteration)


