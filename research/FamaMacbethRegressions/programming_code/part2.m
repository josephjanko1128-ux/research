clear;
clc;
%set this to the path of the data
data_directory = '/home/jjanko/Documents/MATLAB/hw2_janko/data';
%set this to the path of the results directory
results_directory = '/home/jjanko/Documents/MATLAB/hw2_janko/results';
%set this to the path of the writeup directory
writeup_directory = '/home/jjanko/Documents/MATLAB/hw2_janko/writeup';
%get the data for the project and name the variables

mfr = readmatrix(fullfile(data_directory, 'mfr.dat'));

disp('Problem 2')
disp("The number of funds in mfr.dat")
disp("There should be 3,716")
disp(length(mfr(1,2:length(mfr(1,:)))))
mfr = mfr(:,2:length(mfr(1,:)));

[T,N] = size(mfr);
mfr(mfr == -99.) = NaN;

ff5 = fullfile(data_directory, 'cleaned_data_part2.csv');
factors = readmatrix(ff5);
rf = factors(:,length(factors(1,:)));
factors = factors(:, 2:length(factors(1,:)) -1);

[Tfactors, K] = size(factors);

MKT_dict = containers.Map();
HML_dict = containers.Map();
SMB_dict = containers.Map();
int_dict = containers.Map();
saved_residuals_dict = containers.Map();
savedCoef_dict = containers.Map();
alpha = containers.Map();
tstat = containers.Map();
alpha_simulation = containers.Map();
tstat_simulation = containers.Map();

for i = 1:N
    idx = find(isnan(mfr(:,i)) == 0);
    fund_i = mfr(idx,i);
    length_i = length(fund_i);
    if length_i > 8
        Mkt_RF = factors(idx,1);
        SMB = factors(idx,2);
        HML = factors(idx,3);
        RF = rf(idx,:);
        intercept = ones(length_i,1);
        excessR = fund_i - RF;
        MKT_dict(string(i)) = Mkt_RF;
        SMB_dict(string(i))= SMB;
        HML_dict(string(i))= HML;
        int_dict(string(i))= intercept;
        x = [Mkt_RF, SMB, HML, intercept];
        [params,Resid,se_ols,tstat_ols]=janko_ols(excessR,x);
        alpha(string(i)) = params(4);
        saved_residuals_dict(string(i)) = Resid;
        tstat(string(i)) = tstat_ols(4);
        savedCoef_dict(string(i)) = params;
        alpha_simulation(string(i)) = [];
        tstat_simulation(string(i)) = [];
    end
end
    
%%Kosowski method
k = keys(saved_residuals_dict) ;
for sim = 1:1000
    for i = 1:length(saved_residuals_dict)
        res_i = saved_residuals_dict(k{i});
        lenr = length(res_i);
        T_b = randi([1,lenr],lenr,1);
        intercept_b = ones(lenr,1);
        res_b = res_i(T_b);
        c = savedCoef_dict(k{i});
        pseudoR = c(1) * MKT_dict(k{i}) + c(2) * SMB_dict(k{i}) + c(3) * HML_dict(k{i})+c(4) + res_b;
        x =   [MKT_dict(k{i}), SMB_dict(k{i}), HML_dict(k{i}), intercept_b];
        %estimate alpha from bootstrapped return
        [params,Resid,se_ols,tstat_ols]=janko_ols(pseudoR,x);
        a = params(4);
        t = tstat_ols(4);
        alpha_simulation(k{i}) = [alpha_simulation(k{i}); a];
        tstat_simulation(k{i}) = [tstat_simulation(k{i}); t];
    end
    
end

k = keys(alpha);
alpha_values = [];
for i = 1:length(k)
    alpha_values = [alpha_values; alpha(k{i})];
end
pcrtile_check = [1 5 10 25 50 75 90 95 99];
p_check = prctile(alpha_values,pcrtile_check,'all');
output = [];
 
for p=1:length(p_check)

 alpha_array = [];
 tstat_array = [];
 sim_alpha_array = [];
 pct_array = [];
 
 for i = 1:length(alpha_values)
     if p == 1
         if  alpha_values(i) <= p_check(p)  
             alpha_array = [alpha_array; alpha(k{i})];
             tstat_array = [tstat_array; tstat(k{i})];
             sim_alpha_array = [sim_alpha_array; mean(alpha_simulation(k{i}))];
             pct_array = [pct_array; length(find(tstat_simulation(k{i}) > 1.96)) / length(tstat_simulation(k{i}))];
             
         end
     end
     if p~=1 && p ~= length(p_check)
         if  alpha_values(i) > p_check(p-1) && alpha_values(i) <= p_check(p)
             alpha_array = [alpha_array; alpha(k{i})];
             tstat_array = [tstat_array; tstat(k{i})];
             sim_alpha_array = [sim_alpha_array; mean(alpha_simulation(k{i}))];
             pct_array = [pct_array; length(find(tstat_simulation(k{i}) > 1.96)) / length(tstat_simulation(k{i}))];
         end
     end

     if p == length(p_check)
         if  alpha_values(i) > p_check(p)  
             alpha_array = [alpha_array; alpha(k{i})];
             tstat_array = [tstat_array; tstat(k{i})];
             sim_alpha_array = [sim_alpha_array; mean(alpha_simulation(k{i}))];
             pct_array = [pct_array; length(find(tstat_simulation(k{i}) > 1.96)) / length(tstat_simulation(k{i}))];
         end
     end
 end
 output = [output; [pcrtile_check(p) length(alpha_array) mean(alpha_array) mean(tstat_array) mean(sim_alpha_array) mean(pct_array)]];

end

part2_out = array2table(output);
part2_out.Properties.VariableNames  = {'Percentile' 'Nobs' 'Alpha' 't-stat', 'Sim-Alpha', '% > 1.96'};
writetable(part2_out, fullfile(results_directory, 'part_2.csv'),'WriteRowNames',true);

