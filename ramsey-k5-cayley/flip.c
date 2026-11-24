#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static double q[256];
static double fact[5]={1,1,2,6,24};
double dens(const double *r){
  double tot=0;
  #pragma omp parallel for reduction(+:tot) schedule(dynamic)
  for(int b=0;b<256;b++){
    double rb=r[b];
    for(int c=b;c<256;c++){ double pc=rb*r[c]*r[b^c]; if(pc==0) continue;
      for(int d=c;d<256;d++){ double pd=pc*r[d]*r[b^d]*r[c^d]; if(pd==0) continue;
        for(int e=d;e<256;e++){ double pe=pd*r[e]*r[b^e]*r[c^e]*r[d^e]; if(pe==0) continue;
          /* multiplicity 4!/prod m! for weakly ordered b<=c<=d<=e */
          int m=1; double div=1; int v[4]={b,c,d,e};
          for(int i=1;i<4;i++){ if(v[i]==v[i-1]) m++; else {div*=fact[m]; m=1;} } div*=fact[m];
          tot+=pe*24.0/div; }}}}
  return tot/4294967296.0;
}
double D(const double *x){ double r[256],b[256]; for(int i=0;i<256;i++){r[i]=x[i];b[i]=1-x[i];} return dens(r)+dens(b);}

#include <time.h>
int main(){FILE*f=fopen("q.txt","r");for(int i=0;i<256;i++)if(fscanf(f,"%lf",&q[i])!=1)return 1;fclose(f);
double base=D(q);double p=2648.0/4041.0;time_t t0=time(0);double best=base;
for(int z=0;z<256;z++){ if(time(0)-t0>230){printf("budget at z=%d\n",z);break;}
 double s=q[z]; if(s>0&&s<1) continue;
 double opts[2]={1-s,p};
 for(int k=0;k<2;k++){q[z]=opts[k];double v=D(q);if(v<best){best=v;}
  if(v<base) printf("IMPROVE z=%d to %.6f D=%.16g\n",z,opts[k],v);}
 q[z]=s; fflush(stdout);}
printf("base %.16g best %.16g\n",base,best);}
