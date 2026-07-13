function [delta_hat, theta_hat, phi_hat,t,se,j] = get_problem2(consumption, mkt, inst, tcenter)
T = length(consumption);
% delta, theta, psi
testparams = [.5,.5,.5];
nob_g_t=size(mkt,2);
W = eye(size(mkt,2)*size(inst,2));
GMM_2_1 = @(testparams) gmin2(testparams, consumption,mkt,inst, W);
[j, g_t, g_T]= GMM_2_1(testparams);

%DO THE TWO STEP GMM HANSEN SINGLETON 1982
bestgridJ = 1e10;
for griddelta = 0:1:10
    for gridtheta = 0:1:10
        for gridphi = 0:1:10
            gridtest = [griddelta, gridtheta, gridphi];
            [j, g_t, g_T] = GMM_2_1(gridtest);

            if j < bestgridJ

                bestgridJ = j;
                bestgridparams = gridtest;

        end
        end
    end
end
[j, g_t, g_T]= GMM_2_1(bestgridparams);
Acovg = g_t.'*g_t/T;
num_lags = 1;
for n = 1:num_lags
    NWweight = 1 - n/(num_lags+1);
    lag_cov = g_t(1+n:end,:).'*g_t(1:end-n,:)/T;
    Avcovg = Acovg + NWweight*(lag_cov+lag_cov');
end
W2 = pinv(Acovg);

GMM_2_1 = @(testparams) gmin2(testparams, consumption,mkt,inst, W2);

param_hat = janko_opt(GMM_2_1, bestgridparams);
GMM_2_1_f = @(testparams) gmin2_fmin(testparams, consumption,mkt,inst, W);
x = fmincon(GMM_2_1_f,[.5,.5,.5]);
param_hat = abs(x);

[j, g_t, g_T] =  GMM_2_1(param_hat);
disp(param_hat)
disp(j)

%get the standard error
delta_hat = param_hat(1);
theta_hat = param_hat(2);
phi_hat = param_hat(3);

stepsize = .01;
theta_fd = theta_hat + stepsize;
[ans, ans, g_T_fd] =  GMM_2_1([delta_hat, theta_fd, phi_hat]);
dgT = (g_T_fd - g_T)' / stepsize;

se = sqrt(pinv(dgT*W2*dgT')/T);
t = (theta_hat - tcenter)/ se;

end
