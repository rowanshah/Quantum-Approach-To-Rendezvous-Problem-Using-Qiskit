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

#%%
def same_room_oracle(maze, alice_room, bob_room):
    maze.h(alice_room)
    maze.h(bob_room)
    maze.barrier()
    q_room_number = QuantumRegister(alice_room.size)
    print(q_room_number.size)
    c_room_number = ClassicalRegister(n_rooms)
    maze.add_register(q_room_number)
    maze.add_register(c_room_number)
    maze.cx(alice_room, q_room_number)
    maze.cx(bob_room, q_room_number)
    maze.barrier()
    maze.x(q_room_number)
    maze.h(bob_room[0])
    maze.ccx(q_room_number[0], q_room_number[1], bob_room[0])
    maze.h(bob_room[0])
    maze.barrier()
    maze.h(bob_room)
    maze.x(bob_room)
    maze.cz(bob_room[0], bob_room[1])
    maze.x(bob_room)
    maze.h(bob_room)
    maze.barrier()
    print(maze)
    #maze.measure(q_room_number, c_room_number)
    #maze.draw(output="mpl", filename='maze')
    maze.draw(output="mpl")
    
#%%
n_rooms = 4
n = int(np.ceil(np.log2(n_rooms)))
alice_room = QuantumRegister(n)
bob_room = QuantumRegister(n)
maze = QuantumCircuit(alice_room)
maze.add_register(bob_room)
same_room_oracle(maze, alice_room, bob_room)


#%%
"""
backend = BasicAer.get_backend('qasm_simulator')
shots = 1024
results = execute(maze, backend=backend, shots=shots).result()
answer = results.get_counts()
plot_histogram(answer)
"""







