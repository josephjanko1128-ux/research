
function [beta,epsilon,SE,tstat,r2]=janko_ols(y,x)

beta = inv(x'*x)*(x'*y);
yhat = x*beta;
epsilon = y-yhat;

var_epsilon = epsilon.^2;
SE=sqrt(diag(inv(x'*x)*x'*diag(var_epsilon)*x*inv(x'*x)));

tstat = beta./SE;

r2 = 1.0 - sum((y-epsilon).^2) / sum((y-mean(y)).^2);


