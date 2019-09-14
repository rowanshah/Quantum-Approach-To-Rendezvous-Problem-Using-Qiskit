# Quantum Approach to the Rendezvous Problem using Qiskit
This is the repository for Team Rendezvous at the Qiskit Camp 2019 taking place in Mürren, Switzerland. 

## Qiskit Camp 
Qiskit is an open-source quantum computing framework for leveraging today's quantum processors in research, education, and business. Qiskit Camp is a community event organised by IBM where experts in Quantum Computing, students, artists and people from all walks of life come together to have fun and do some quantum together.

Here is a pictures of the the beautiful city of Mürren:

![Murren1](Miscallaneous/Murren1.jpg)

Here is a picture of our team hard at work: 

![Team](Miscallaneous/Team.jpg)

A picture of the team after the algorithm worked! 

![Team2](Miscallaneous/Team2.jpg)

## The Classical Rendezvous Conundrum 
The aim is to build on a quantum advantage by using Grover's algorithm to the Rendezvous Problem. The problem is as follows: Alice & Bob, agree to meet at a park. The only details they have before hand is the date and time of their meeting and a pre-agreed strategy on how they'll find each other within this park. Once Alice and Bob arive at the park, they have no means of communicating with each other. The connundrum they face is which route would lead to the best possible probability of finding the other? How much time would that take? Should they wait before they start or wait at any point during their search?

This problem was first introduced in this [research paper](https://epubs.siam.org/doi/10.1137/S0363012993249195) by Steve Alpern in 1979.

## Our Problem
After seeing that it was going to be very limiting to attack the classical problem with no communication since it would have prevented us from using entangled qubits, we decided to pivot and adapt the problem even further to the quantum setting. Instead of creating an algorithm which two parties could independently apply in a maze to find each other, we now introduce a god with access to a quantum computer who will apply and algorithm to bring these two quantum parties together.
Our maze in this case was the complete graph on four vertices, K<sub>4</sub> and after spawning Alice and Bob at two different spots on K<sub>4</sub> it was the god's job to make sure they end up in the same spot with some definite probability.

The picture below illustrates the set up of the problem.

![problem](Miscallaneous/problem.png)

## The Implementation
This circuit below shows visually what our algorithm is in terms of quantum gates.
![circuit](Solution/maincircuit.png)
We start by putting Alice and Bob in a superposition over the whole graph, preparing them for iterations of Grover's Search.

We then apply Grover's Search where our oracle takes the input state and marks the states where the two registers are together, a phase is then applied to amplify these cases. This has to be carried out over each register and creates a special case of Grover's where the number of iterations has to be #I = π/4 times sqrt(N), rounded up, where N is the number of nodes on the graph. 

Therefore to achieve the states we want, these iterations are applied on Alice and Bob's registers, giving #I/2 for each participant. We also found that the order of these iterations is irrelevant.

## Results

Our solution was implemented in the python script - Rendezvous.py in the Solution folder. 

Below you see the result given for 1024 shots over different numbers of iterations of our algorithm, at the end giving a comparison of the likelihood that the algorithm is successfull in producing maximally entangled states.
![2Iterations](Solution/Plots/2iterations.png)

![8Iterations](Solution/Plots/8iterations.png)

![SuccessProbability](Solution/SuccessProbability.png)

This shows that if the algorithm is applied #I times on each register we return to the initial product state.

## Future Work and Applications

Whilst our method is currently specific to complete Graphs we can generalise to classes which are not by making use of a time evolution operator based on the adjacency matrix of the graph, i.e. e<sup>iAt</sup>.  Our algorithm produces **maximally entangled states** giving it the ability to be used in state preparation for state preparation in contexts where this required such as cryptography.


## Thanks

A special shoutout to the Qiskit team for all the support throughout this event. Another special mention to the [Qiskit textbook](https://community.qiskit.org/textbook/) which gave us a starting point to build a circuit implementing Grover's search algorithm.







