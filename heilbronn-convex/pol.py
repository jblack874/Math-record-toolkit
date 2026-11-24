import itertools, numpy as np
from fractions import Fraction as F
from scipy.optimize import minimize
from h import hull_idx, area2, hull2, score
from pts import P13, P14, REC
for n,P in ((13,P13),(14,P14)):
    Q=[(F(x),F(y)) for x,y in P]; v0,H=score(Q); m=n; T=list(itertools.combinations(range(m),3))
    z0=np.array([[float(x),float(y)] for x,y in Q]).ravel()
    sgn=np.array([np.sign(area2(z0.reshape(m,2),*t)) for t in T]); hs=np.sign(hull2(z0.reshape(m,2),H))
    def tri(z):
        Z=z[:-1].reshape(m,2); hh=hs*hull2(Z,H); return np.array([sgn[k]*area2(Z,*t)/hh for k,t in enumerate(T)])-z[-1]
    best=float(v0)
    for trial in range(6):
        rng=np.random.default_rng(trial); z=z0+(rng.normal(0,1e-6,z0.shape) if trial else 0)
        x0=np.r_[z,min(tri(np.r_[z,0]))]
        r=minimize(lambda x:-x[-1],x0,jac=lambda x:np.r_[np.zeros(2*m),-1],constraints=[{'type':'ineq','fun':tri}],method='SLSQP',options={'maxiter':500,'ftol':1e-16})
        Z=r.x[:-1].reshape(m,2); Qn=[(F(a),F(b)) for a,b in Z]
        if hull_idx(Qn)!=H and sorted(hull_idx(Qn))!=sorted(H): pass
        v,_=score(Qn); best=max(best,float(v))
        print(n,'trial',trial,'exact value after polish %.18f  vs record %.18f  diff %.2e'%(float(v),float(v0),float(v-v0)))
