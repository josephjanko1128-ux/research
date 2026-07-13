function best_param = janko_opt(func, start_point)

small_peturb  = 1e-10;
med_peturb = 1e-5;
big_peturb = 1e-2;

n_params = size(start_point, 1);
best_param = start_point;
best_val = func(start_point);
not_done = 1;
while not_done == 1
    not_done = 0;
    for i = 1:n_params
        step_up = best_param;
        step_up(i) = step_up(i) + big_peturb;
        if func(step_up) < best_val
            best_param = step_up;
            best_val = func(step_up);
            not_done = 1;
        end
        step_down = best_param;
        step_down(i) = step_down(i) - big_peturb;
        if func(step_down) < best_val
            best_param = step_down;
            best_val = func(step_down);
            not_done = 1;
        end
        
        step_up = best_param;
        step_up(i) = step_up(i) + med_peturb;
        if func(step_up) < best_val
            best_param = step_up;
            best_val = func(step_up);
            not_done = 1;
        end
        step_down = best_param;
        step_down(i) = step_down(i) - med_peturb;
        if func(step_down) < best_val
            best_param = step_down;
            best_val = func(step_down);
            not_done = 1;
        end
        
        
        step_up = best_param;
        step_up(i) = step_up(i) + small_peturb;
        if func(step_up) < best_val
            best_param = step_up;
            best_val = func(step_up);
            not_done = 1;
        end
        step_down = best_param;
        step_down(i) = step_down(i) - small_peturb;
        if func(step_down) < best_val
            best_param = step_down;
            best_val = func(step_down);
            not_done = 1;
        end  
        
    end
end
