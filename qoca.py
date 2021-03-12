from typing import Optional, Union, List, Tuple

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate, Parameter
from qiskit.circuit.library import RZGate, RXGate, CXGate, HGate
from qiskit.qasm import pi

from qiskit.aqua import aqua_globals
from qiskit.aqua.components.initial_states import InitialState
from qiskit.aqua.operators import WeightedPauliOperator, Z2Symmetries
from qiskit.aqua.components.variational_forms import VariationalForm
from qiskit.chemistry.fermionic_operator import FermionicOperator

from g import GGate
from zx import ZXGate
from zy import ZYGate

class QOCA(VariationalForm):
    def __init__(self, num_qubits: Optional[int] = None, reps: int = 1, initial_state: Optional[InitialState] = None) -> None:
        super().__init__()

        self._num_qubits = num_qubits
        self._reps = reps
        self._initial_state = initial_state
        self._support_parameterized_circuit = True

    @property    
    def num_qubits(self) -> int:
        
        return self._num_qubits

    @num_qubits.setter
    def num_qubits(self, num_qubits: int) -> None:
        
        self._num_qubits = num_qubits

    def add_drive_layer(circuit: QuantumCircuit, layer_parameters: List[Parameter]):
        circuit.ry(layer_parameters[0],0)
        circuit.rx(layer_parameters[1],0)
        circuit.append(zy(layer_parameters[2]),0,1)
        circuit.append(zx(layer_parameters[3]),0,1)
        circuit.cx(0,1)
        circuit.append(zy(layer_parameters[4]),1,2)
        circuit.append(zx(layer_parameters[5]),1,2)
        circuit.cx(1,2)
        circuit.append(zy(layer_parameters[6]),2,3)
        circuit.append(zx(layer_parameters[7]),2,3)
        circuit.cx(2,3)
        circuit.cx(1,2)
        circuit.cx(0,1)
        return circuit

    def construct_circuit(self, parameters: List[Parameter], q: Optional[QuantumRegister] = None) -> QuantumCircuit:

        if q is None:
            q = QuantumRegister(self._num_qubits,name='q')
        
        circuit = QuantumCircuit(q)

        num_drive_params = 8

        for layer in range(self._reps):
            layer_params = parameters[layer*num_drive_params:(layer+1)*num_drive_params]
            self.add_drive_layer(circuit,layer_params)

        return circuit