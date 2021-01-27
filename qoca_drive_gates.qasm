OPENQASM 2.0;
include "qelib1.inc";
gate g q0 {
  rz(pi) q0;
  rx(pi/2) q0;
}

gate zy(param) q0, q1 {
  g q1;
  cx q0, q1;
  rz(param) q1;
  cx q0, q1;
  g q1;
}

gate zx(param) q0, q1 {
  h q1;
  cx q0, q1;
  rz(param) q1;
  cx q0, q1;
  h q1;
}

gate d4(p1, p2, p3, p4, p5, p6, p7, p8) q0, q1, q2, q3 {
  ry(p1) q0;
  rx(p2) q0;
  zy(p3) q0, q1;
  zx(p4) q0, q1;
  cx q0, q1;
  zy(p5) q1, q2;
  zx(p6) q1, q2;
  cx q1, q2;
  zy(p7) q2, q3;
  zx(p8) q2, q3;
  cx q2, q3;
  cx q1, q2;
  cx q0, q1;
}

