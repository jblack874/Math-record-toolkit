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

int main(){FILE*f=fopen("q.txt","r");for(int i=0;i<256;i++)if(fscanf(f,"%lf",&q[i])!=1)return 1;fclose(f);
int I[16];int n=0;for(int z=0;z<256;z++) if(q[z]>0&&q[z]<1) I[n++]=z;
double h=1e-4;
for(int i=0;i<n;i++)for(int j=i;j<n;j++){double s1=q[I[i]],s2=q[I[j]];double v[4];int k=0;
for(int a=-1;a<=1;a+=2)for(int b=-1;b<=1;b+=2){q[I[i]]+=a*h;q[I[j]]+=b*h;v[k++]=D(q);q[I[i]]=s1;q[I[j]]=s2;}
printf("%d %d %.12g\n",i,j,(v[3]-v[1]-v[2]+v[0])/(4*h*h));}
}
