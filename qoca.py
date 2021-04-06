from typing import Optional, List

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate, Parameter
from qiskit.qasm import pi
from qiskit.extensions import UnitaryGate

from qiskit.aqua import aqua_globals
from qiskit.aqua.components.initial_states import InitialState, Custom
from qiskit.aqua.components.variational_forms import VariationalForm
from qiskit.aqua.operators.evolutions import MatrixEvolution

from qiskit.chemistry.fermionic_operator import FermionicOperator
from qiskit.aqua.operators import WeightedPauliOperator, Z2Symmetries

from g import GGate
from zx import ZXGate
from zy import ZYGate

import numpy as np

class QOCA(VariationalForm):
    def __init__(self,
        ferm_operator: Optional[FermionicOperator] = None,
        num_qubits: Optional[int] = 4,
        reps: int = 1,
        initial_state: Optional[InitialState] = None,
        qubit_mapping: str = 'jordan_wigner') -> None:
        
        super().__init__()

        self._num_qubits = num_qubits
        self._reps = reps
        if initial_state is None:
            self._initial_state = Custom(num_qubits, state='uniform')
        else:
            self._initial_state = initial_state
        self._support_parameterized_circuit = True

        self._num_parameters = 2 * self._num_qubits * self._reps
        self.parameters = []
        [self.parameters.append(0) for i in range(self._num_parameters)]
        parameters = self.parameters
        self._bounds = [(-np.pi, np.pi) for _ in range(self._num_parameters)]

        if ferm_operator is None:
            self._ferm_operator = FermionicOperator(h1=None, h2=None)
        else:
            self._ferm_operator = ferm_operator

    def add_hamiltonian_layer(self, circuit: QuantumCircuit, fermionic_operator: FermionicOperator):
        
        qubitOp = self._ferm_operator.mapping(map_type = "jordan_wigner", threshold=0.00000001)
        evol = MatrixEvolution().convert(operator = qubitOp)
        circuit.append(UnitaryGate(qubitOp, label = None),[0,qubitOp.num_qubits],[])

        return circuit
    
    def add_drive_layer(self, circuit: QuantumCircuit, layer_params: List[Parameter]):
        
        circuit.ry(layer_params[0],0)
        circuit.rx(layer_params[1],0)

        for i in range(self._num_qubits-1):
            circuit.append(ZYGate(layer_params[(2*i)+2]),[i,i+1],[])
            circuit.append(ZXGate(layer_params[(2*i)+3]),[i,i+1],[])
            circuit.cx(i,i+1)
        
        for i in range(self._num_qubits-2, 0, -1):
            circuit.cx(i-1,i)
        
        return circuit

    def construct_circuit(self, parameters: List[Parameter] = None, q: Optional[QuantumRegister] = None):

        if q is None:
            q = QuantumRegister(self._num_qubits,name='q')
        
        circuit = QuantumCircuit(q)

        if parameters is None:
            parameters = []
            [parameters.append(0) for i in range(self._num_parameters)]

        for layer in range(self._reps):
            layer_end_index = int(self._num_parameters/self._reps)
            layer_params = parameters[(layer*layer_end_index):((layer+1)*layer_end_index)]
            self.add_hamiltonian_layer(circuit, self._ferm_operator)
            self.add_drive_layer(circuit, layer_params)

        return circuit