"""Write q.txt (256 red probabilities) for Pinho's round-4 binary Cayley step graphon (masks from his PROOF.md, bit z = (mask >> z) & 1)."""
H=int("173e5ee876e8e880167c7ae06ec8a801173e5ee876e8e880e88181178117177e",16)
F=int("0040200008000001010204081020408000402000080000010000000000000000",16)
q=[1.0 if (H>>z)&1 else (2648/4041 if (F>>z)&1 else 0.0) for z in range(256)]
open("q.txt","w").write("\n".join(repr(x) for x in q))
