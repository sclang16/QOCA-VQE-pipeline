from typing import Optional, List

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate, Parameter
from qiskit.qasm import pi

from qiskit.aqua import aqua_globals
from qiskit.aqua.components.initial_states import InitialState, Custom
from qiskit.aqua.components.variational_forms import VariationalForm
from qiskit.aqua.operators import PrimitiveOp, SummedOp, OperatorBase, ListOp

from qiskit.chemistry.drivers import PySCFDriver, UnitsType, Molecule
from qiskit.chemistry.transformations import FermionicTransformation, FermionicQubitMappingType

from g import GGate
from zx import ZXGate
from zy import ZYGate

import numpy as np

class QOCA(VariationalForm):
    def __init__(self,
        fermionic_op: FermionicTransformation = None,
        reps: int = 1,
        initial_state: Optional[InitialState] = None,
        qubit_mapping: str = 'jordan_wigner') -> None:
        
        super().__init__()

        if fermionic_op is not None:
            self._fermionic_op = fermionic_op
        else:
            return

        self._qubit_op = self._fermionic_op[0]
        self._num_qubits = self._qubit_op.num_qubits
        self._reps = reps

        if initial_state is None:
            self._initial_state = Custom(self._num_qubits, state='uniform')
        else:
            self._initial_state = initial_state
        self._support_parameterized_circuit = True

        self._num_parameters = ((2 * self._num_qubits) + len(self._qubit_op)) * self._reps
        self._parameters = [Parameter('theta_%s' % i) for i in range(self._num_parameters)]
        self._bounds = [(-np.pi, np.pi) for _ in range(self._num_parameters)]
    
    @property
    def num_qubits(self) -> int:
        """Number of qubits of the variational form.

        Returns:
           int:  An integer indicating the number of qubits.
        """
        return self._num_qubits

    @num_qubits.setter
    def num_qubits(self, num_qubits: int) -> None:
        """Set the number of qubits of the variational form.

        Args:
           num_qubits: An integer indicating the number of qubits.
        """
        self._num_qubits = num_qubits

    def add_hamiltonian_layer(self, circuit: QuantumCircuit, op: ListOp, layer_params: List[Parameter]):
        
        qarg_list = list(range(0, self._num_qubits))

        for i in range(len(op)):

            op_instruction = op.oplist[i].mul(layer_params[i]).exp_i().to_instruction()
            circuit.append(op_instruction,qarg_list,[])

        return circuit

    def add_drive_layer(self, circuit: QuantumCircuit, layer_params: List[Parameter]):
        split_qubit_index = int(self._num_qubits/2)

        circuit.ry(layer_params[0],0)
        circuit.rx(layer_params[1],0)
        circuit.ry(layer_params[(split_qubit_index*2)],split_qubit_index)
        circuit.rx(layer_params[(split_qubit_index * 2) + 1],split_qubit_index)

        for i in range(split_qubit_index-1):
            circuit.append(ZYGate(layer_params[(2*i)+2]),[i,i+1],[])
            circuit.append(ZXGate(layer_params[(2*i)+3]),[i,i+1],[])
            circuit.cx(i,i+1)
        
        for i in range(split_qubit_index-2, 0, -1):
            circuit.cx(i-1,i)

        for i in range(split_qubit_index, (split_qubit_index*2)-1):
            circuit.append(ZYGate(layer_params[(2*i)+2]),[i,i+1],[])
            circuit.append(ZXGate(layer_params[(2*i)+3]),[i,i+1],[])
            circuit.cx(i,i+1)

        for i in range((split_qubit_index*2)-2, split_qubit_index, -1):
            circuit.cx(i-1,i)

        return circuit

    def construct_circuit(self, parameters: List[Parameter], q: Optional[QuantumRegister] = None):

        if q is None:
            q = QuantumRegister(self._num_qubits,name='q')
        
        circuit = QuantumCircuit(q)

        if parameters is None:
            self._parameters = [Parameter('%s' % i) for i in range(self._num_parameters)]
        for layer in range(self._reps):
            layer_end_index = int(self._num_parameters/self._reps)

            ham_layer_params = self._parameters[(layer*layer_end_index):((layer*layer_end_index)+len(self._qubit_op))]
            drive_layer_params = self._parameters[((layer*layer_end_index)+len(self._qubit_op)):((layer+1)*layer_end_index)]
            self.add_hamiltonian_layer(circuit, self._qubit_op, ham_layer_params)
            self.add_drive_layer(circuit, drive_layer_params)

        return circuit