% this program solves a growth model with policy function iteration
% This program uses a discretized state space
clear all; clc;
beta=0.9; delta=0.8;
W=linspace(0.0,5,501)';
v=zeros(size(W));
Tv=zeros(size(W));
Policy=zeros(size(W));
u=zeros(size(W));


for iters=1:20 % iteration loop
for i=1:length(W) % K(i) is today's state variable
    for j=1:length(W) % K(j) is tomorrow's state variable
        u2=W(i)-delta*W(j);
        if ((u2>=0)&&(u2<=1))
            c2=u2^2;
            temp(i,j)=(1-c2)^0.5;
        else
            temp(i,j)=-inf;
        end
    end % j loop
    [Tv(i),jstar]=max(temp(i,:)'+beta*v(:));
    Policy(i)=jstar;
    u(i)=(1-((W(i)-delta*W(jstar))^2))^0.5;
    
end % i loop
vec1=[[1:length(W)]';[1:length(W)]'];
vec2=[[1:length(W)]';Policy];
vec3=[ones(length(W),1);-beta*ones(length(W),1)];
N=sparse(vec1,vec2,vec3);
Tv=N\u;
disp([iters,max(abs(v-Tv))]);
plot(W,v);hold on;
v=Tv;
end


figure(1); hold on;
plot(W,Tv,'b');
xlabel('capital');
ylabel('value function');


figure(2); hold on;
plot(W,W(Policy),'b',W,W,'r');
xlabel('capital');
ylabel('policy function');