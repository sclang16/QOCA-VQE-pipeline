from typing import Optional, Union, List, Tuple

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate
from qiskit.circuit.library import RZGate, RXGate, CXGate, HGate
from qiskit.qasm import pi

from qiskit.aqua import aqua_globals
from qiskit.aqua.components.initial_states import InitialState
from qiskit.aqua.operators import WeightedPauliOperator, Z2Symmetries
from qiskit.aqua.components.variational_forms import VariationalForm
from qiskit.chemistry.fermionic_operator import FermionicOperator

# Define gates not native to Qiskit (G, ZY, ZX) needed for drive hamiltonian
class GGate(Gate):
    def __init__(self, label = None):
        super().__init__('g',1,[],label=label)

    def _define(self):
        q = QuantumRegister(1,'q')
        qc = QuantumCircuit(q,name=self.name)

        rules = [
            (RZGate(pi),[q[0]],[]),
            (RXGate(pi/2),[q[0]],[])
        ]
        for instr, qargs, cargs in rules:
            qc._append(instr, qargs, cargs)

        self.definition = qc
    
class ZYGate(Gate):
    def __init__(self, theta, label = None):
        super().__init__('zy',2,[theta],label=label)

    def _define(self):
        q = QuantumRegister(2,'q')
        theta = self.params[0]
        qc = QuantumCircuit(q,name=self.name)

        rules = [
            (GGate(),[q[1]],[]),
            (CXGate(),[q[0],q[1]],[]),
            (RZGate(theta),[q[1]],[]),
            (CXGate(),[q[0],q[1]],[]),
            (GGate(),[q[1]],[])
        ]
        for instr, qargs, cargs in rules:
            qc._append(instr, qargs, cargs)

        self.definition = qc

class ZXGate(Gate):
    def __init__(self, theta, label = None):
        super().__init__('zx',2,[theta],label=label)

    def _define(self):
        q = QuantumRegister(2,'q')
        theta = self.params[0]
        qc = QuantumCircuit(q,name=self.name)

        rules = [
            (HGate(),[q[1]],[]),
            (CXGate(),[q[0],q[1]],[]),
            (RZGate(theta),[q[1]],[]),
            (CXGate(),[q[0],q[1]],[]),
            (HGate(),[q[1]],[])
        ]
        for instr, qargs, cargs in rules:
            qc._append(instr, qargs, cargs)

        self.definition = qc

class QOCA(VariationalForm):
    def __init__(self, num_qubits: Optional[int] = None, reps: int = 1; initial_state: Optional[InitialState] = None) -> None:
        super().__init__()

        self._num_qubits = num_qubits
        self._reps = reps
        self._initial_state = initial_state

    @property    
    def num_qubits(self) -> int:
        
        return self._num_qubits

    @num_qubits.settter
    def num_qubits(self, num_qubits: int) -> None:
        
        self._num_qubits = num_qubits

    def construct_circuit(self, parameters: List[Parameter], q: Optional[QuantumRegister] = None) -> QuantumCircuit:

        if q is None:
            q = QuantumRegister(self._num_qubits,name='q')
        
        circuit = QuantumCircuit(q)

        circuit.ry(,0)
        circuit.rx(,0)

        for nq in self._num_qubits:
            

        return circuit