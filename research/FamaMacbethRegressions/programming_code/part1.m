clear all; close all; clc;
%set this to the path of the data
data_directory = '/home/jjanko/Documents/MATLAB/hw2_janko/data';
%set this to the path of the results directory
results_directory = '/home/jjanko/Documents/MATLAB/hw2_janko/results';
%set this to the path of the writeup directory
writeup_directory = '/home/jjanko/Documents/MATLAB/hw2_janko/writeup';
%get the data for the project and name the variables

 mfr = readmatrix(fullfile(data_directory, 'mfr.dat'));
 
 disp('Problem 1')
 disp("The number of funds in mfr.dat")
 disp("There should be 3,716")
 disp(length(mfr(1,2:length(mfr(1,:)))))
 
 ff5 = fullfile(data_directory, 'F-F_Research_Data_Factors_cleaned.txt');
 ff5 = readmatrix(ff5);

 count = 0;
 mean_ret = [];
 std_ret = [];
 rho1 = [];

 dict_data = containers.Map();
 for i = 2:length(mfr(1,2:length(mfr(1,:))))
     mut = mfr(:,i);
     date = mfr(:,1);
     cleaned_mut = [];
     for j = 1:length(mut)
         if mut(j) ~= -99.
             date_match = date(j);
             for k = 1:length(ff5(:,1))
                 if date_match == ff5(k,1)
                     mut_risk = mut(j) - ff5(k,5)/100.0;
                     cleaned_mut = [cleaned_mut; [date(j) mut_risk ff5(k,2)/100.0 ff5(k,3)/100.0 ff5(k,4)/100.0]];
                 end
             end
         end
     end
     if isempty(cleaned_mut) == 0
         if length(cleaned_mut(:,1)) >= 8

            test = cleaned_mut;
            y = test(:,2);
            mean_ret = [mean_ret; mean(y)];
            std_ret = [std_ret; std(y)];
            rho1 = [rho1; corr(y(2:length(y)),y(1:length(y)-1))];
            count = count + 1;
         end
     end
 end
 
 pcrtile_check = [1 5 10 25 50 75 90 95 99];
 p_check = prctile(mean_ret,pcrtile_check,'all');
 output = [];
 
 for p=1:length(p_check)
     
     pct_array = [];
     std_array = [];
     rho_array = [];
     for i = 1:length(mean_ret)
         if p == 1
             if  mean_ret(i) <= p_check(p)  
                 pct_array = [pct_array; mean_ret(i)*100.0];
                 std_array = [std_array; std_ret(i)*100.0];
                 rho_array = [rho_array; rho1(i)];
                 
             end
         end
         if p~=1 && p ~= length(p_check)
             if  mean_ret(i) > p_check(p-1) && mean_ret(i) <= p_check(p)
                 pct_array = [pct_array; mean_ret(i)*100.0];
                 std_array = [std_array; std_ret(i)*100.0];
                 rho_array = [rho_array; rho1(i)];

             end
         end
         
         if p == length(p_check)
             if  mean_ret(i) > p_check(p)  
                 pct_array = [pct_array; mean_ret(i)*100.0];
                 std_array = [std_array; std_ret(i) *100.0];
                 rho_array = [rho_array; rho1(i)];
                 
             end
         end
     end
     output = [output; [pcrtile_check(p) length(pct_array) round(mean(pct_array),2) round(mean(std_array),2) round(mean(rho_array),2)]];
     
 end

part1_out = array2table(output);
part1_out.Properties.VariableNames  = {'Percentile' 'Nobs' 'Mean' 'Std', 'Rho1'};
writetable(part1_out, fullfile(results_directory, 'part_1.csv'),'WriteRowNames',true);



