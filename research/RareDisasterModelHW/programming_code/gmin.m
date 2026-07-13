function [j, g_t, g_T] =gmin(params,Y,X,Z,W)
beta = .95;
[T]=size(Y,1);
gamma=params(1);
mom= beta*(Y.^(-gamma)).*X ;

if length(Z) > 0
for i=1:T
   g_t(i,:)=kron(mom(i,:),Z(i,:));
end

g_T=mean(g_t)';

j=g_T'*W*g_T; 
j = j*T;
else
for i=1:T
   g_t(i,:)=mom(i,:);
end

g_T=mean(g_t)';

j=g_T'*g_T; 
j = j*T;
end
end

