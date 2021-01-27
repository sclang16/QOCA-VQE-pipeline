from typing import Optional, Union, List, Tuple
import sys
import collections
import copy

import numpy as np
from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate
from qiskit.circuit.library import RZGate, RXGate, CXGate, HGate
from qiskit.qasm import pi

from qiskit.aqua import aqua_globals
from qiskit.aqua.components.initial_states import InitialState
from qiskit.aqua.operators import WeightedPauliOperator, Z2Symmetries
from qiskit.aqua.components.variational_forms import VariationalForm
from qiskit.chemistry.fermionic_operator import FermionicOperator

# Define gates not native to Qiskit (G, ZY, ZX) needed for drive Hamiltonian
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

# gate tests

qc = QuantumCircuit(1, name = 'G')
qc.rz(pi,0)
qc.rx(pi/2,0)
g_gate = qc.to_gate([],'G')

"""
    qc = QuantumCircuit(2, name = "ZY")
    qc.append(g_gate,[1])
    qc.cx(0,1)
    qc.rz(theta, 1)
    qc.cx(0,1)
    qc.append(g_gate,[1])
    zy_gate = qc.to_gate([theta],"ZY")

    qc = QuantumCircuit(2, name = "ZX")
    qc.h(1)
    qc.cx(0,1)
    qc.rz(theta, 1)
    qc.cx(0,1)
    qc.h(1)
    zx_gate = qc.to_gate([theta],"ZX")
"""
tc = QuantumCircuit(2)
tc.append(g_gate,[0])
tc.draw()