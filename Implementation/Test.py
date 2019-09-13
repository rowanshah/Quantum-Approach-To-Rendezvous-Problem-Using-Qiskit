#%%
import logging
import numpy as np
import operator
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute, Aer
from qiskit.tools.visualization import plot_histogram
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.qasm import pi
from qiskit.aqua import AquaError, Pluggable, PluggableType, get_pluggable_class
from qiskit.aqua.utils import get_subsystem_density_matrix
from qiskit.aqua.algorithms import QuantumAlgorithm
from qiskit.aqua.components.initial_states import Custom
from qiskit.aqua.circuits.gates import mct
from qiskit import IBMQ, BasicAer
from qiskit.providers.ibmq import least_busy
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute

def oracle(maze, alice_room, bob_room, q_oracle):
    maze.cx(alice_room[0], bob_room[0])
    maze.x(bob_room[1])
    maze.cx(alice_room[1], bob_room[1])
    maze.x(bob_room[0])
    maze.ccx(bob_room[0], bob_room[1], q_oracle[0])
    maze.barrier()
    maze.cx(q_oracle[0], q_oracle[1])
    maze.barrier() # f inverse
    maze.ccx(bob_room[0], bob_room[1], q_oracle[0])
    maze.x(bob_room[0])
    maze.cx(alice_room[1], bob_room[1])
    maze.x(bob_room[1])
    maze.cx(alice_room[0], bob_room[0])
    maze.barrier()
    #maze.draw(output='mpl', filename='oracle')

def phase_bob(maze, bob_room):
    maze.h(bob_room)
    maze.x(bob_room)
    maze.h(bob_room[1])
    maze.cx(bob_room[0], bob_room[1])
    maze.h(bob_room[1])
    maze.x(bob_room)
    #maze.z(bob_room[1])
    #maze.cz(bob_room[1], bob_room[0])
    maze.h(bob_room)
    maze.barrier()
    maze.draw(output='mpl', filename='bob_image')

def phase_alice(maze, alice_room):
    maze.h(alice_room)
    maze.x(alice_room)
    maze.h(alice_room[1])
    maze.cx(alice_room[0], alice_room[1])
    maze.h(alice_room[1])
    maze.x(alice_room)
    # maze.z(bob_room[1])
    # maze.cz(bob_room[1], bob_room[0])
    maze.h(alice_room)
    maze.barrier()
    maze.draw(output='mpl', filename='alice_image')

def state_preparation(n_rooms):
    n = int(np.ceil(np.log2(n_rooms)))
    alice_room = QuantumRegister(n)
    bob_room = QuantumRegister(n)
    maze = QuantumCircuit(alice_room)
    maze.add_register(bob_room)
    maze.h(alice_room)
    maze.h(bob_room)
    q_oracle = QuantumRegister(alice_room.size)
    c_alice = ClassicalRegister(n)
    c_bob = ClassicalRegister(n)
    maze.add_register(q_oracle)
    maze.add_register(c_alice)
    maze.add_register(c_bob)
    maze.x(q_oracle[1])
    maze.h(q_oracle[1])
    maze.barrier()
    #maze.draw(output='mpl', filename='state_preparation')
    return maze, alice_room, bob_room, q_oracle, c_alice, c_bob

def rendezvous(n_rooms, n_iteration):
    maze, alice_room, bob_room, q_oracle, c_alice, c_bob = state_preparation(n_rooms)
    for i in range(int(n_iteration/2)):
        oracle(maze, alice_room, bob_room, q_oracle)
        phase_bob(maze, bob_room)
        oracle(maze, alice_room, bob_room, q_oracle)
        phase_alice(maze, alice_room)
    maze.measure(alice_room, c_alice)
    maze.measure(bob_room, c_bob)
    maze.draw(output='mpl', filename='maze_last')
    # Load on real device
    IBMQ.load_account()
    provider = IBMQ.get_provider(hub='ibm-q')
    backend = least_busy(provider.backends(simulator=True))
    counts = execute(maze, backend).result().get_counts()
    print(counts)
    print("done!")
rendezvous(4,7)





#%%
