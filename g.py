"""G gate."""

import numpy as np
from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate
from qiskit.circuit.library import U2Gate
from qiskit.qasm import pi

class GGate(Gate):
    def __init__(self, label = None):
        super().__init__('g',1,[],label=label)

    def _define(self):
        q = QuantumRegister(1,'q')
        qc = QuantumCircuit(q,name=self.name)

        rules = [
            (U2Gate(pi/2,pi/2),[q[0]],[])
        ]
        for instr, qargs, cargs in rules:
            qc._append(instr, qargs, cargs)

        self.definition = qc