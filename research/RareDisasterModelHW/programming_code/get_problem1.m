function [gamma_hat,t,se,j] = get_problem1(consumption, mkt, inst)
T = length(consumption);

testparams = [20];
nob_g_t=size(mkt,2);
W = eye(size(mkt,2)*size(inst,2));
GMM_1_1 = @(testparams) gmin(testparams, consumption,mkt,inst, W);
[j, g_t, g_T]= GMM_1_1(testparams);

%DO THE TWO STEP GMM HANSEN SINGLETON 1982
bestgridJ = 1e10000;
for griddelta = 1:1:1000
    
    [j, g_t, g_T] = GMM_1_1([griddelta]);
    
    if j < bestgridJ
        
        bestgridJ = j;
        bestgridgamma = [griddelta];
        
    end
end
[j, g_t, g_T]= GMM_1_1(bestgridgamma);
Acovg = g_t.'*g_t/T;
num_lags = 1;
for n = 1:num_lags
    NWweight = 1 - n/(num_lags+1);
    lag_cov = g_t(1+n:end,:).'*g_t(1:end-n,:)/T;
    Avcovg = Acovg + NWweight*(lag_cov+lag_cov');
end
W2 = pinv(Acovg);


GMM_1_1 = @(testparams) gmin(testparams, consumption,mkt,inst, W2);

gamma_hat = janko_opt(GMM_1_1, bestgridgamma);
[j, g_t, g_T] =  GMM_1_1([gamma_hat]);
disp(gamma_hat)
disp(j)
%get the standard error

stepsize = .001;
gamma_hat2_fd = gamma_hat + stepsize;
[ans, ans, g_T_fd] =  GMM_1_1(gamma_hat2_fd);
dgT = (g_T_fd - g_T)' / stepsize;

se = sqrt(inv(dgT*W2*dgT')/T);
t = gamma_hat / se;

end