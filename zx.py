"""ZX gate."""

import numpy as np
from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate
from qiskit.circuit.library import RZGate, CXGate, HGate
from qiskit.qasm import pi

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