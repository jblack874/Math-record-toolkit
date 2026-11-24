import sys, itertools, numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog, minimize
from pts import P13, P14, REC
def hull(pts):
    pts=sorted(range(len(pts)),key=lambda i:(pts[i][0],pts[i][1]))
    def cr(o,a,b,Q): return (Q[a][0]-Q[o][0])*(Q[b][1]-Q[o][1])-(Q[a][1]-Q[o][1])*(Q[b][0]-Q[o][0])
    return pts
def hull_idx(Q):
    idx=sorted(range(len(Q)),key=lambda i:(Q[i][0],Q[i][1]))
    cr=lambda o,a,b:(Q[a][0]-Q[o][0])*(Q[b][1]-Q[o][1])-(Q[a][1]-Q[o][1])*(Q[b][0]-Q[o][0])
    lo=[];up=[]
    for i in idx:
        while len(lo)>=2 and cr(lo[-2],lo[-1],i)<=0: lo.pop()
        lo.append(i)
    for i in reversed(idx):
        while len(up)>=2 and cr(up[-2],up[-1],i)<=0: up.pop()
        up.append(i)
    return lo[:-1]+up[:-1]
def area2(Q,i,j,k): return (Q[j][0]-Q[i][0])*(Q[k][1]-Q[i][1])-(Q[j][1]-Q[i][1])*(Q[k][0]-Q[i][0])
def hull2(Q,H): return sum(Q[H[t]][0]*Q[H[(t+1)%len(H)]][1]-Q[H[(t+1)%len(H)]][0]*Q[H[t]][1] for t in range(len(H)))
def score(Q):
    H=hull_idx(Q); h=hull2(Q,H)
    return min(abs(area2(Q,*t)) for t in itertools.combinations(range(len(Q)),3))/h, H
for n,P in ((13,P13),(14,P14)):
    Q=[(F(x),F(y)) for x,y in P]
    v,H=score(Q); print(n,'exact matches registry:',v==F(REC[n]),'hull',len(H))
    Qf=np.array([[float(x),float(y)] for x,y in Q]); m=len(Q)
    T=list(itertools.combinations(range(m),3))
    def fs(z):
        Z=z.reshape(m,2); hh=abs(hull2(Z,H)); return np.array([abs(area2(Z,*t))/hh for t in T])
    s0=fs(Qf.ravel()); vmin=s0.min(); act=np.argsort(s0)[:40]
    gaps=(s0[act]-vmin)/vmin; print('  relative gaps of 25 smallest:', ' '.join('%.0e'%g for g in gaps[:25]))
    A=[i for i in act if (s0[i]-vmin)/vmin<1e-9]; print('  active (1e-9):',len(A),'| dof',2*m-6)
    # first-order LP: maximize s with grad_t . d >= s for active t, |d|<=1 (affine moves give s=0 at best)
    eps=1e-7; G=[]
    for i in A:
        g=np.zeros(2*m)
        for k in range(2*m):
            e=np.zeros(2*m); e[k]=eps; g[k]=(fs(Qf.ravel()+e)[i]-fs(Qf.ravel()-e)[i])/(2*eps)
        G.append(g)
    G=np.array(G); res=linprog(np.r_[np.zeros(2*m),-1],A_ub=np.hstack([-G,np.ones((len(A),1))]),b_ub=np.zeros(len(A)),bounds=[(-1,1)]*(2*m)+[(None,1)],method='highs')
    print('  first-order LP: best uniform rate s* = %.3e (0 = first-order stationary)'%(-res.fun))
