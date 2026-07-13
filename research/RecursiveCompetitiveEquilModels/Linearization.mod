var k c R;
varexo taui tauc tauk g; 
parameters delta alpha gamma beta; 

delta=0.2;
alpha=0.33;
gamma=2;
beta=0.95;

model;
R=(1+tauc(-1))/(1+tauc)*((1-taui)/(1-taui(-1))*(1-delta)+(1-tauk)/(1-taui(-1))*alpha*k(-1)^(alpha-1));
c+g+k=k(-1)^alpha+(1-delta)*k(-1);
c^(-gamma)=beta*c(+1)^(-gamma)*R(+1);
end;

initval;
k=1.4;
c=0.5;
R=1;
taui=0;
tauc=0;
tauk=0;
g=0.2;
end;
steady;


endval;
k=1.4;
c=0.5;
R=1;
taui=0;
tauc=0;
tauk=0;
g=0.4;
end;
steady;

shocks;
var g;
periods 1:10;
values 0.4;
end;


simul(periods=60);

% to show variables
% oo_.exo_simul, oo_.endo_simul
% capital and consumption: 

figure(1); 
subplot(1,4,1);plot([1:62],oo_.exo_simul(:,1),'ro');title('tau_i'); 
subplot(1,4,2);plot([1:62],oo_.exo_simul(:,2),'o');title('tau_c');  
subplot(1,4,3);plot([1:62],oo_.exo_simul(:,3),'o');title('tau_k');
subplot(1,4,4);plot([1:62],oo_.exo_simul(:,4),'ro');title('g'); 

figure(2); 
subplot(1,3,1);plot([1:62],oo_.endo_simul(1,:),'ro');title('capitial'); 
subplot(1,3,2);plot([1:62],oo_.endo_simul(2,:),'o');title('consumption');  
subplot(1,3,3);plot([1:62],oo_.endo_simul(3,:),'o');title('R');


