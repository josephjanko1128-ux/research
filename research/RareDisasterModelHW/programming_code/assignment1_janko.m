clear all; close all; clc;
%set this to the path of the data
data_directory = '/home/jjanko/Documents/MATLAB/hw1_janko/data';
%set this to the path of the results directory
results_directory = '/home/jjanko/Documents/MATLAB/hw1_janko/results';
%set this to the path of the writeup directory
writeup_directory = '/home/jjanko/Documents/MATLAB/hw1_janko/writeup';
%get the data for the project and name the variables

data_file = fullfile(data_directory, 'data_2.csv');
M = readmatrix(data_file);
consumption = M(:,2);
lagged_consumption = M(:,3);
mkt_ret = M(:,4);
ff = M(:,5:29);
cay = M(:,30);
pd = M(:, 31);
T = length(cay);
z = ones(T,1);

%define the instruments
instruments = [lagged_consumption, cay, pd];

output = get_stats(results_directory, consumption, mkt_ret, instruments);
disp(output);


%get the data
disp('Probelm 1.1')

inst = [];
mkt = mkt_ret;

[gamma_hat,t,se,j] = get_problem1(consumption, mkt, inst);
part_1_1 = [gamma_hat,t,se,j];


disp('Problem 1.2')
inst = [];
mkt = ff;
[gamma_hat,t,se,j] = get_problem1(consumption, mkt, inst);
part_1_2 = [gamma_hat,t,se,j];

disp('Problem 1.3')
inst = [z, lagged_consumption, cay];
mkt = ff;
[gamma_hat,t,se,j] = get_problem1(consumption, mkt, inst);
part_1_3 = [gamma_hat,t,se,j];

%write the results to results folder
part1 = [part_1_1; part_1_2; part_1_3];
part1 = array2table(part1);
part1.Properties.RowNames={'Part 1_1', 'Part 1_2', 'Part 1_3'};
part1.Properties.VariableNames  = {'gamma hat', 'tstat', 'se', 'jstat'};
writetable(part1, fullfile(results_directory, 'part_1.csv'),'WriteRowNames',true);

disp('Problem 2.1')
inst = [];
mkt = ff;
tcenter = 0;
[delta_hat, theta_hat, phi_hat,t,se,j] = get_problem2(consumption, mkt, inst, tcenter);

part_2_1 = [delta_hat, theta_hat, phi_hat,t,se,j];

disp('Problem 2.2')
inst = [];
mkt = ff;
tcenter = 1.0;
[delta_hat, theta_hat, phi_hat,t,se,j] = get_problem2(consumption, mkt, inst, tcenter);

part_2_2 = [delta_hat, theta_hat, phi_hat,t,se,j];

disp('Problem 2.3')
inst = [z, lagged_consumption, cay];
mkt = ff;
tcenter = 1.0;
[delta_hat, theta_hat, phi_hat,t,se,j] = get_problem2(consumption, mkt, inst, tcenter);

part_2_3 = [delta_hat, theta_hat, phi_hat,t,se,j];



%write the results to results folder
part2 = [part_2_1; part_2_2; part_2_3];
part2 = array2table(part2);
part2.Properties.RowNames={'Part 2_1', 'Part 2_2', 'Part 2_3'};
part2.Properties.VariableNames  = {'delta hat','theta hat', 'psi hat',  'tstat theta', 'se theta', 'jstat'};
writetable(part2, fullfile(results_directory, 'part_2.csv'),'WriteRowNames',true);


disp('Problem 3')
% The expected rate of returnon equity is in (9). 
% The expected rate of return on bills is in (12). 
% The equity premium is the difference betweenthese two rates. 
% The expected rate of return on equity conditioned on no disasters is in (10). 
% The face bill rateis in (11). 
% The equity premium conditioned on no disasters is the difference between these two rates. 
% Theprice-earnings ratio is in (17). 
% The expected growth rate is in (18), 
% and the expected growth rate conditionedon no disasters is in (19).

disp('Table V columns (1) and (2)')
%p probability of disaster
%b is the size of the contraction
%q theprobability of default (contingent on the occurrence of disaster)
%d the extent of default

disp('col 1')
p = 0.0;
b = .29;
q = 0.0;
one_minus_b = 0.625;

gamma = 0.025 ;
sigma = 0.02;
rho = .03;
theta = 4.;

equity = rho + theta*gamma - .5 * theta^2 * sigma^2 + theta*sigma^2 -p * ((one_minus_b)^(1-theta) - 1 +b);
bills = rho + theta*gamma - .5 * theta^2 * sigma^2 - p *((1.0-q) * ((one_minus_b)^(-theta)) + q*((one_minus_b)^(1.0-theta)) + q*b - 1.0);
equit_prem = theta * sigma^2 + p*(1-q)*((one_minus_b)^-theta - (one_minus_b)^(1-theta) - b);
pe = 1.0 /(rho + (theta - 1)*gamma - .5*((theta - 1)^2)*(sigma^2)-p*((one_minus_b)^(1-theta)-1));
face_bill = rho + theta*gamma - .5 * theta^2 * sigma^2 - p *((1.0-q) * ((one_minus_b)^(-theta)) + q*((one_minus_b)^(1.0-theta)) - 1.0);
equit_prem_cond = theta * sigma^2 + p*(1-q)*((one_minus_b)^-theta - (one_minus_b)^(1-theta));
growth_rate= gamma + .5*sigma^2 - p*b;
growth_rate_conditional = gamma + .5*sigma^2;
equity_cond = rho + theta*gamma - .5 * theta^2 * sigma^2 + theta*sigma^2 -p * ((one_minus_b)^(1-theta) - 1 );

part_3_1 = [equity, bills, equit_prem, pe, face_bill, equit_prem_cond, growth_rate, growth_rate_conditional, equity_cond];

disp('col 2')
p = .017;
b = .29;
q = .4;
sigma = 0.02;

testparam = .625;
emin = @(testparam)prem_min(testparam, p,b,q,gamma,sigma,rho,theta);
one_minus_b = fmincon(emin,.625);

equity = rho + theta*gamma - .5 * theta^2 * sigma^2 + theta*sigma^2 -p * ((one_minus_b)^(1-theta) - 1 +b);
bills = rho + theta*gamma - .5 * theta^2 * sigma^2 - p *((1.0-q) * ((one_minus_b)^(-theta)) + q*((one_minus_b)^(1.0-theta)) + q*b - 1.0);
equit_prem = theta * sigma^2 + p*(1-q)*((one_minus_b)^-theta - (one_minus_b)^(1-theta) - b);
pe = 1.0 /(rho + (theta - 1)*gamma - .5*((theta - 1)^2)*(sigma^2)-p*((one_minus_b)^(1-theta)-1));
face_bill = rho + theta*gamma - .5 * theta^2 * sigma^2 - p *((1.0-q) * ((one_minus_b)^(-theta)) + q*((one_minus_b)^(1.0-theta)) - 1.0);
equit_prem_cond = theta * sigma^2 + p*(1-q)*((one_minus_b)^-theta - (one_minus_b)^(1-theta));
growth_rate= gamma + .5*sigma^2 - p*b;
growth_rate_conditional = gamma + .5*sigma^2;
equity_cond = rho + theta*gamma - .5 * theta^2 * sigma^2 + theta*sigma^2 -p * ((one_minus_b)^(1-theta) - 1 );

part_3_2 = [equity, bills, equit_prem, pe, face_bill, equit_prem_cond, growth_rate, growth_rate_conditional, equity_cond];
disp('col 2 with savov')
%the garbage growth for savov is .0288
p = .017;
b = .29;
q = .4;
sigma = 0.0288;



equity = rho + theta*gamma - .5 * theta^2 * sigma^2 + theta*sigma^2 -p * ((one_minus_b)^(1-theta) - 1 +b);
bills = rho + theta*gamma - .5 * theta^2 * sigma^2 - p *((1.0-q) * ((one_minus_b)^(-theta)) + q*((one_minus_b)^(1.0-theta)) + q*b - 1.0);
equit_prem = theta * sigma^2 + p*(1-q)*(((one_minus_b)^-theta) - ((one_minus_b)^(1-theta)) - b);
pe = 1.0 /(rho + (theta - 1)*gamma - .5*((theta - 1)^2)*(sigma^2)-p*((one_minus_b)^(1-theta)-1));
face_bill = rho + theta*gamma - .5 * theta^2 * sigma^2 - p *((1.0-q) * ((one_minus_b)^(-theta)) + q*((one_minus_b)^(1.0-theta)) - 1.0);
equit_prem_cond = theta * sigma^2 + p*(1-q)*((one_minus_b)^-theta - (one_minus_b)^(1-theta));
growth_rate= gamma + .5*sigma^2 - p*b;
growth_rate_conditional = gamma + .5*sigma^2;
equity_cond = rho + theta*gamma - .5 * theta^2 * sigma^2 + theta*sigma^2 -p * ((one_minus_b)^(1-theta) - 1 );

part_3_3 = [equity, bills, equit_prem, pe, face_bill, equit_prem_cond, growth_rate, growth_rate_conditional, equity_cond];

part3 = [part_3_1; part_3_2; part_3_3];
part3 = array2table(part3);
part3.Properties.RowNames={'Part 3_1', 'Part 3_2', 'Part 3_3'};
part3.Properties.VariableNames  = {'Expected equity rate','Expected bill rate','Equity premium','PE', 'Face Bill Rate', 'Equity premium conditional', 'growth rate', 'growth rate conditional', 'equity rate conditional'};
writetable(part3, fullfile(results_directory, 'part_3.csv'),'WriteRowNames',true);
disp(part3)
