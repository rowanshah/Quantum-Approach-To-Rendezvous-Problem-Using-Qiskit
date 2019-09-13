# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'

#%%
import logging
import numpy as np
import operator


#%%
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.qasm import pi

from qiskit.aqua import AquaError, Pluggable, PluggableType, get_pluggable_class
from qiskit.aqua.utils import get_subsystem_density_matrix
from qiskit.aqua.algorithms import QuantumAlgorithm
from qiskit.aqua.components.initial_states import Custom
from qiskit.aqua.circuits.gates import mct


#%%
logger = logging.getLogger(__name__)


#%%
"""Implementing Grover's search algorithm on Qiskit using their API docs"""
class Grover(QuantumAlgorithm):
    
    PROP_INCREMENTAL = 'incremental'
    PROP_NUM_ITERATIONS = 'num_iterations'
    PROP_MCT_MODE = 'mct_mode'

    CONFIGURATION = {
        'name': 'Grover',
        'description': "Grover's Search Algorithm",
        'input_schema': {
            '$schema': 'http://json-schema.org/schema#',
            'id': 'grover_schema',
            'type': 'object',
            'properties': {
                PROP_INCREMENTAL: {
                    'type': 'boolean',
                    'default': False
                },
                PROP_NUM_ITERATIONS: {
                    'type': 'integer',
                    'default': 1,
                    'minimum': 1
                },
                PROP_MCT_MODE: {
                    'type': 'string',
                    'default': 'basic',
                    'enum': [
                        'basic',
                        'basic-dirty-ancilla',
                        'advanced',
                        'noancilla',
                    ]
                },
            },
            'additionalProperties': False
        },
        'problems': ['search'],
        'depends': [
            {
                'pluggable_type': 'initial_state',
                'default': {
                    'name': 'CUSTOM',
                    'state': 'uniform'
                }
            },
            {
                'pluggable_type': 'oracle',
                'default': {
                     'name': 'LogicalExpressionOracle',
                },
            },
        ],
    }

    def __init__(self, oracle, init_state=None, incremental=False, num_iterations=1, mct_mode='basic'):
        """
        Args for the constructor:
            oracle (Oracle): the oracle pluggable component
            init_state (InitialState): the initial quantum state preparation
            incremental (bool): boolean flag for whether to use incremental search mode or not
            num_iterations (int): the number of iterations to use for amplitude amplification
        """
        self.validate(locals())
        super().__init__()
        self._oracle = oracle
        self._mct_mode = mct_mode
        self._init_state = init_state if init_state else Custom(len(oracle.variable_register), state='uniform')
        self._init_state_circuit = self._init_state.construct_circuit(mode='circuit', register=oracle.variable_register)
        self._init_state_circuit_inverse = self._init_state_circuit.inverse()

        self._diffusion_circuit = self._construct_diffusion_circuit()
        self._max_num_iterations = np.ceil(2 ** (len(oracle.variable_register) / 2))
        self._incremental = incremental
        self._num_iterations = num_iterations if not incremental else 1
        self.validate(locals())
        if incremental:
            logger.debug('Incremental mode specified, ignoring "num_iterations".')
        else:
            if num_iterations > self._max_num_iterations:
                logger.warning('The specified value {} for "num_iterations" might be too high.'.format(num_iterations))
        self._ret = {}
        self._qc_aa_iteration = None
        self._qc_amplitude_amplification = None
        self._qc_measurement = None

    def _construct_diffusion_circuit(self):
        qc = QuantumCircuit(self._oracle.variable_register)
        num_variable_qubits = len(self._oracle.variable_register)
        num_ancillae_needed = 0
        if self._mct_mode == 'basic' or self._mct_mode == 'basic-dirty-ancilla':
            num_ancillae_needed = max(0, num_variable_qubits - 2)
        elif self._mct_mode == 'advanced' and num_variable_qubits >= 5:
            num_ancillae_needed = 1

        # check oracle's existing ancilla and add more if necessary
        num_oracle_ancillae = len(self._oracle.ancillary_register) if self._oracle.ancillary_register else 0
        num_additional_ancillae = num_ancillae_needed - num_oracle_ancillae
        if num_additional_ancillae > 0:
            extra_ancillae = QuantumRegister(num_additional_ancillae, name='a_e')
            qc.add_register(extra_ancillae)
            ancilla = [q for q in extra_ancillae]
            if num_oracle_ancillae > 0:
                ancilla += [q for q in self._oracle.ancillary_register]
        else:
            ancilla = self._oracle.ancillary_register

        if self._oracle.ancillary_register:
            qc.add_register(self._oracle.ancillary_register)
        qc.barrier(self._oracle.variable_register)
        qc += self._init_state_circuit_inverse
        qc.u3(pi, 0, pi, self._oracle.variable_register)
        qc.u2(0, pi, self._oracle.variable_register[num_variable_qubits - 1])
        qc.mct(
            self._oracle.variable_register[0:num_variable_qubits - 1],
            self._oracle.variable_register[num_variable_qubits - 1],
            ancilla,
            mode=self._mct_mode
        )
        qc.u2(0, pi, self._oracle.variable_register[num_variable_qubits - 1])
        qc.u3(pi, 0, pi, self._oracle.variable_register)
        qc += self._init_state_circuit
        qc.barrier(self._oracle.variable_register)
        return qc


#%%
""" Constructing the quantum circuit on Qiskit using their API docs """
def construct_circuit(self, measurement=False):
        """
        Args:
            measurement (bool): Boolean flag to indicate if measurement should be included in the circuit.

        Returns:
            the QuantumCircuit object for the constructed circuit
        """
        if self._qc_amplitude_amplification is None:
            self._qc_amplitude_amplification = QuantumCircuit() + self.qc_amplitude_amplification_iteration
        qc = QuantumCircuit(self._oracle.variable_register, self._oracle.output_register)
        qc.u3(pi, 0, pi, self._oracle.output_register)  # x
        qc.u2(0, pi, self._oracle.output_register)  # h
        qc += self._init_state_circuit
        qc += self._qc_amplitude_amplification

        if measurement:
            measurement_cr = ClassicalRegister(len(self._oracle.variable_register), name='m')
            qc.add_register(measurement_cr)
            qc.measure(self._oracle.variable_register, measurement_cr)

        self._ret['circuit'] = qc
        return qc


def _run(self):
        if self._incremental:
            current_max_num_iterations, lam = 1, 6 / 5

            def _try_current_max_num_iterations():
                target_num_iterations = self.random.randint(current_max_num_iterations) + 1
                self._qc_amplitude_amplification = QuantumCircuit()
                for _ in range(target_num_iterations):
                    self._qc_amplitude_amplification += self.qc_amplitude_amplification_iteration
                return self._run_with_existing_iterations()

            while current_max_num_iterations < self._max_num_iterations:
                assignment, oracle_evaluation = _try_current_max_num_iterations()
                if oracle_evaluation:
                    break
                current_max_num_iterations = min(lam * current_max_num_iterations, self._max_num_iterations)
        else:
            self._qc_amplitude_amplification = QuantumCircuit()
            for i in range(self._num_iterations):
                self._qc_amplitude_amplification += self.qc_amplitude_amplification_iteration
            assignment, oracle_evaluation = self._run_with_existing_iterations()

        self._ret['result'] = assignment
        self._ret['oracle_evaluation'] = oracle_evaluation
        return self._ret



#%%
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute
n_rooms = 4
n = int(np.ceil(np.log2(n_rooms)))
alice_room = QuantumRegister(n)
bob_room = QuantumRegister(n)
maze =  QuantumCircuit(alice_room)
maze.add_register(bob_room)
def same_room_oracle(maze, alice_room, bob_room):
    q_room_number = QuantumRegister(alice_room.size)
    print(q_room_number.size)
    c_room_number = ClassicalRegister(alice_room.size)
    maze.add_register(q_room_number)
    maze.add_register(c_room_number)
    for i in range(n):
        maze.cx(alice_room[i], q_room_number[i])
        maze.cx(bob_room[i], q_room_number[i])
    maze.measure(q_room_number, c_room_number)
    print(maze)
same_room_oracle(maze, alice_room, bob_room)


#%%



