#%%
#Accuracy Test script
import numpy as np
from qiskit import IBMQ, BasicAer, Aer
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute
from qiskit.providers.ibmq import least_busy
import matplotlib.pyplot as plt
def oracle(maze, alice_room, bob_room, q_oracle, q_oracle_ancilla):
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
    maze.draw(output='mpl', filename='state_preparation_n')
    return maze, alice_room, bob_room, q_oracle, q_oracle_ancilla, c_alice, c_bob
def rendezvous(n_rooms, n_iteration, n_shots):
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
    accuracy = sum(winners) / n_shots
    print(counts)
    print("done!")
    print("number of iterations: ", n_iteration)
    print("accuracy: ", accuracy)
    maze.draw(output='mpl', filename='alice-bob_n')
    return counts, accuracy
def plot_counts(counts, n_rooms, n_iteration):
    count_value = [counts.get(k) for k in counts.keys()]
    count_label = [k for k in counts.keys()]
    x = np.arange(len(counts))
    plt.bar(x, height=count_value)
    plt.xticks(x, count_label)
    plt.title('Number of rooms for each pawn: ' + str(n_rooms) +
              ', Number of iterations: ' + str(n_iteration))

def plot_accuracy(n_range, n_shots):    
    iter_list = []
    accuracy_list = []
    for j in range(1, n_range):
        n_iteration = j
        n_rooms = 2
        n_shots = n_shots
        counts, accuracy = rendezvous(n_rooms, n_iteration, n_shots)
        iter_list.append(j)
        accuracy_list.append(accuracy)
    #plot_accuracy(counts, n_rooms, n_iteration)
    #plot_counts(counts, n_rooms, n_iteration)
    #counts_sorted = sorted(counts.values())
    #counts_sorted.reve rse()

# accuracy vs no of iterations
    x = np.arange(len(iter_list))
    plt.bar(x, height=accuracy_list)
    plt.xticks(x, iter_list)
    plt.title('Success Probability')    

plot_accuracy(21, 1024)
#%%
