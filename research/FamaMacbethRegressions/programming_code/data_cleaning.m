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
 
 
 dict_data = containers.Map();
 
 %get an index of mutual funds for keys in the dictionary
 mut = [1:1:length(mfr(2,:))];
 %get the date column
 date = mfr(:,1);
 %get the actual mutual fund data outside of date
 data = mfr(:,2:length(mfr(2,:)));
 
 % get the ff5 and liquidty data on the same time frame
 covariates = [];
 for i = 1:length(date)
     date_match = date(i);
      
     for k = 1:length(ff5(:,1))
         if date_match == ff5(k,1)
             covariates = [covariates; [date_match ff5(k,2)/100.0 ff5(k,3)/100.0 ff5(k,4)/100.0 ff5(k,5)/100.0]];
         end
     end
 
 end
 
part1 = array2table(covariates);
part1.Properties.VariableNames  = {'date' ,'Mkt-RF','SMB','HML','RF'};
writetable(part1, fullfile(data_directory, 'cleaned_data_part2.csv'),'WriteRowNames',true);


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
 
 liq = fullfile(data_directory, 'liq_data.csv');
 liq = readmatrix(liq);
 
 dict_data = containers.Map();
 
 %get an index of mutual funds for keys in the dictionary
 mut = [1:1:length(mfr(2,:))];
 %get the date column
 date = mfr(:,1);
 %get the actual mutual fund data outside of date
 data = mfr(:,2:length(mfr(2,:)));
 
 % get the ff5 and liquidty data on the same time frame
 covariates = [];
 for i = 1:length(date)
     date_match = date(i);
      for k = 1:length(liq(:,1))
        if date_match == liq(k,1)
            liq_match = liq(k,4);
        end
      end
      
     for k = 1:length(ff5(:,1))
         if date_match == ff5(k,1)
             covariates = [covariates; [date_match liq_match ff5(k,2)/100.0 ff5(k,3)/100.0 ff5(k,4)/100.0 ff5(k,5)/100.0]];
         end
     end
 
 end
 
part1 = array2table(covariates);
part1.Properties.VariableNames  = {'date', 'liq' ,'Mkt-RF','SMB','HML','RF'};
writetable(part1, fullfile(data_directory, 'cleaned_data_part4.csv'),'WriteRowNames',true);


