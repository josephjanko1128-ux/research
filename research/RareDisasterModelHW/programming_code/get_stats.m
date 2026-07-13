function output = get_stats(results_directory, consumption, mkt_ret, instruments)

%get the descriptive statistics
out = {'consumption','mkt-rf', 'lagged consumption', 'cay', 'log price to divided de-meaned'};
des_data = [consumption,mkt_ret, instruments];
numVars = length(out(1,:));
T = length(des_data);

mean_result = zeros(1,numVars);
median_result = zeros(1,numVars);
std_result = zeros(1,numVars);
corr_result = zeros(1,numVars);
autcorr_result = zeros(1,numVars);
min_result = zeros(1,numVars);
max_result = zeros(1,numVars);

for i = 1:numVars
    mean_result(1,i) =  round(mean(des_data(:,i)),4);
    median_result(1,i) = round(median(des_data(:,i)),4);
    std_result(1,i) = round(std(des_data(:,i)),4);
    corr_result(1,i) = round(corr(des_data(:,i), mkt_ret),2);
    %get the correlation at lag 1
    autcorr_result(1,i) = round(corr(des_data(2:T,i), des_data(1:T-1,i)),2);
    min_result(1,i) =  round(min(des_data(:,i)),4);
    max_result(1,i) = round(max(des_data(:,i)),4);
end

desc_out = [mean_result; median_result; std_result; corr_result; autcorr_result; min_result; max_result];
desc_out = array2table(desc_out);
desc_out.Properties.VariableNames = out;
desc_out.Properties.RowNames = {'mean', 'median', 'std', 'corr', 'autocorr(lag 1)', 'Min', 'Max'};
writetable(desc_out, fullfile(results_directory, 'descriptive_stats.csv'),'WriteRowNames',true);


output = 'Descriptive Statistics Done';
end