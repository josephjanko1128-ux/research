function [j, g_t, g_T] =gmin2(params,Y,X,Z,W)

[T]=size(Y,1);

delta=abs(params(1));
theta = abs(params(2));
phi = abs(params(3));

mom = (delta^theta) * ((Y).^(-theta / phi)) .* (X.^(-1+theta)) .* X;

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

