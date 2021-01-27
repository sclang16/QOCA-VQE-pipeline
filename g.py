"""G gate."""

import numpy as np
from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate
from qiskit.circuit.library import RZGate, RXGate
from qiskit.qasm import pi

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