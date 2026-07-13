function e = prem_min(one_minus_b,p,b,q,gamma,sigma,rho,theta)

equity = rho + theta*gamma - .5 * theta^2 * sigma^2 + theta*sigma^2 -p * ((one_minus_b)^(1-theta) - 1 +b);
bills = rho + theta*gamma - .5 * theta^2 * sigma^2 - p *((1.0-q) * ((one_minus_b)^(-theta)) + q*((one_minus_b)^(1.0-theta)) + q*b - 1.0);
equity_prem = theta * sigma^2 + p*(1-q)*((one_minus_b)^-theta - (one_minus_b)^(1-theta) - b);

e_equity = (equity-.071)^2;
e_bill = (bills-.035)^2;
e_prem = (equity_prem-.036)^2;
e = e_equity + e_bill + 2*e_prem;
end