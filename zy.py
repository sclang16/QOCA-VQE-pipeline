"""ZY gate."""

import numpy as np
from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate
from qiskit.circuit.library import RZGate, CXGate
from qiskit.qasm import pi

# import GGate

class ZYGate(Gate):
    def __init__(self, theta, label = None):
        super().__init__('zy',2,[theta],label=label)

    def _define(self):
        q = QuantumRegister(2,'q')
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