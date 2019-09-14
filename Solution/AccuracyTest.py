#%%
#Test script
import numpy as np
from qiskit import IBMQ, BasicAer
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute
from qiskit.providers.ibmq import least_busy
import matplotlib.pyplot as plt
from qiskit.tools.visualization import plot_histogram
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
    #maze.z(alice_room[1])
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
    for i in range(n_iteration):
        oracle(maze, alice_room, bob_room, q_oracle)
        phase_bob(maze, bob_room)
        oracle(maze, alice_room, bob_room, q_oracle)
        phase_alice(maze, alice_room)
    maze.measure(alice_room, c_alice)
    maze.measure(bob_room, c_bob)
    maze.draw(output='mpl', filename='maze_last')
    #Testing on local device
    backend = BasicAer.get_backend('qasm_simulator')
    shots = 1024
    counts = execute(maze, backend=backend, shots=shots).result().get_counts()
    print(counts)
    print("done!")
    print("number of iterations: ", n_iteration)
    return counts
for i in range(3):
    n_iteration = i
    counts = rendezvous(4, n_iteration)
    count_value = [counts.get(k) for k in counts.keys()]
    count_label = [k for k in counts.keys()]
    x = np.arange(len(counts))
    plt.bar(x, height=count_value)
    plt.xticks(x, count_label)
    plt.title('Number of iterations: '+str(n_iteration))




#%%
