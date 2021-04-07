from typing import Optional, List

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate, Parameter
from qiskit.qasm import pi

from qiskit.aqua import aqua_globals
from qiskit.aqua.components.initial_states import InitialState, Custom
from qiskit.aqua.components.variational_forms import VariationalForm

from qiskit.chemistry.drivers import PySCFDriver, UnitsType, Molecule
from qiskit.chemistry.transformations import FermionicTransformation, FermionicQubitMappingType

from g import GGate
from zx import ZXGate
from zy import ZYGate

import numpy as np

class QOCA(VariationalForm):
    def __init__(self,
        molecule: Molecule = None,
        driver: PySCFDriver = None,
        reps: int = 1,
        initial_state: Optional[InitialState] = None,
        qubit_mapping: str = 'jordan_wigner') -> None:
        
        super().__init__()

        if molecule is not None:
            self._molecule = molecule
        else:
            self._molecule = Molecule(geometry=[['Li', [0., 0., 0.]], ['H', [0., 0., 1.6]]], charge=0, multiplicity=1)

        if driver is not None:
            self._driver = driver
        else:
            self._driver = PySCFDriver(molecule = molecule, unit=UnitsType.ANGSTROM, basis='sto3g')

        self._fermionic_op = FermionicTransformation(qubit_mapping = FermionicQubitMappingType.JORDAN_WIGNER, freeze_core = True).transform(self._driver)

        self._qubit_op = self._fermionic_op[0]
        self._num_qubits = self._qubit_op.num_qubits
        self._reps = reps

        if initial_state is None:
            self._initial_state = Custom(self._num_qubits, state='uniform')
        else:
            self._initial_state = initial_state
        self._support_parameterized_circuit = True

        self._num_parameters = (2 * self._num_qubits) * self._reps
        self.parameters = []
        [self.parameters.append(0) for i in range(self._num_parameters)]
        parameters = self.parameters
        self._bounds = [(-np.pi, np.pi) for _ in range(self._num_parameters)]

    def add_hamiltonian_layer(self, circuit: QuantumCircuit, layer_params: List[Parameter]):
        
        ham_gate = self._qubit_op.exp_i().to_instruction()
        qarg_list = list(range(0, self._num_qubits))
        circuit.append(ham_gate,qarg_list,[])

        return circuit
    
# TODO: Update indices for general multilayer case
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
            self.add_hamiltonian_layer(circuit, layer_params)
            self.add_drive_layer(circuit, layer_params)

        return circuit