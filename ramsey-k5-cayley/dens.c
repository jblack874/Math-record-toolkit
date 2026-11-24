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
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"r"); for(int i=0;i<256;i++) fscanf(f,"%lf",&q[i]); fclose(f);
  printf("D=%.16g\n",D(q)); fflush(stdout);
  if(argc>2){ double h=1e-6; for(int z=0;z<256;z++){ double s=q[z]; q[z]=s+h; double a=D(q); q[z]=s-h; double b2=D(q); q[z]=s; printf("%d %.6g %.10g\n",z,s,(a-b2)/(2*h)); fflush(stdout);} }
}
