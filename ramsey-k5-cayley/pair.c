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
double base=D(q);time_t t0=time(0);double best=1;long n=0;int stop=0;
for(int a=0;a<256&&!stop;a++){ if(q[a]>0&&q[a]<1)continue;
 for(int b=a+1;b<256;b++){ if(q[b]>0&&q[b]<1)continue; if(time(0)-t0>200){printf("budget at a=%d\n",a);stop=1;break;}
  double sa=q[a],sb=q[b];q[a]=1-sa;q[b]=1-sb;double v=D(q);n++;if(v<best)best=v;
  if(v<base)printf("IMPROVE %d %d %.16g\n",a,b,v);q[a]=sa;q[b]=sb;}}
printf("pairs %ld base %.16g best-pair %.16g\n",n,base,best);}
