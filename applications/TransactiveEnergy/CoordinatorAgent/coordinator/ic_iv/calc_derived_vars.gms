$ontext
independent variables V_real and V_imag are set prior to this code
other independent variables are set here
then dependent variables are computed here - including objective
finally we could check constraint violations - e.g. balance constraints
$offtext

*--------------------
* derived variables -
*--------------------

         V_LineIr.l(i,j,c)$(branchstatus(i,j,c)) =
            1/sqr(ratio(i,j,c))
                * (g(i,j,c)*V_real.l(i) - (b(i,j,c) + bc(i,j,c)/2)*V_imag.l(i))
            - 1/ratio(i,j,c)
                * (  (g(i,j,c)*V_real.l(j) - b(i,j,c)*V_imag.l(j))*cos(angle(i,j,c))
                   - (g(i,j,c)*V_imag.l(j) + b(i,j,c)*V_real.l(j))*sin(angle(i,j,c)));

         V_LineIr.l(j,i,c)$(branchstatus(i,j,c)) =
            (g(i,j,c)*V_real.l(j) - (b(i,j,c) + bc(i,j,c)/2)*V_imag.l(j))
            - 1/ratio(i,j,c)
                * (  (g(i,j,c)*V_real.l(i) - b(i,j,c)*V_imag.l(i))*cos(-angle(i,j,c))
                   - (g(i,j,c)*V_imag.l(i) + b(i,j,c)*V_real.l(i))*sin(-angle(i,j,c)));

         V_LineIq.l(i,j,c)$(branchstatus(i,j,c)) =
            1/sqr(ratio(i,j,c))
                * (g(i,j,c)*V_imag.l(i) + (b(i,j,c) + bc(i,j,c)/2)*V_real.l(i))
            - 1/ratio(i,j,c)
                * (  (g(i,j,c)*V_imag.l(j) + b(i,j,c)*V_real.l(j))*cos(angle(i,j,c))
                   + (g(i,j,c)*V_real.l(j) - b(i,j,c)*V_imag.l(j))*sin(angle(i,j,c)));

         V_LineIq.l(j,i,c)$(branchstatus(i,j,c)) =
            (g(i,j,c)*V_imag.l(j) + (b(i,j,c) + bc(i,j,c)/2)*V_real.l(j))
            - 1/ratio(i,j,c)
                * (  (g(i,j,c)*V_imag.l(i) + b(i,j,c)*V_real.l(i))*cos(-angle(i,j,c))
                   + (g(i,j,c)*V_real.l(i) - b(i,j,c)*V_imag.l(i))*sin(-angle(i,j,c)));

    V_devi.l(i)$(sum(gen,status2(gen,i)) eq 1 ) =
    abs(sqrt(sqr(V_real.l(i)) + sqr(V_imag.l(i))) - Vsch(i));

    V_artup.l(i)$(sum(gen,status2(gen,i)) eq 1 ) =
    max(0,
    sqrt(sqr(V_real.l(i)) + sqr(V_imag.l(i))) - voltageran_high*Vsch(i));

    V_artlow.l(i)$(sum(gen,status2(gen,i)) eq 1 ) =
    max(0,
    voltageran_low*Vsch(i) - sqrt(sqr(V_real.l(i)) + sqr(V_imag.l(i))));

    V_Lossijc.l(i,j,c)$(branchstatus(i,j,c)) =
    g(i,j,c) / (sqr(b(i,j,c)) + sqr(g(i,j,c))) *
    (sqr(V_LineIr.l(i,j,c)) + sqr(V_LineIq.l(i,j,c)));

    V_Lossi.l(i) =
    sum((j,c)$(branchstatus(i,j,c)),V_Lossijc.l(i,j,c));

    V_load_bus_volt_pen_dev.l(i)$bus_penalize_volt_mag_target(i) =
    max(
      sqrt(sqr(V_real.l(i)) + sqr(V_imag.l(i)))
    - load_bus_voltage_goal
    - load_bus_volt_dead_band,
      load_bus_voltage_goal
    - sqrt(sqr(V_real.l(i)) + sqr(V_imag.l(i)))
    - load_bus_volt_dead_band);

    V_load_bus_volt_pen.l =
    max(0,
    sum(i$bus_penalize_volt_mag_target(i),
          load_bus_volt_pen_coeff_1 * V_load_bus_volt_pen_dev.l(i)
        + load_bus_volt_pen_coeff_2 * sqr(V_load_bus_volt_pen_dev.l(i))));

    V_shuntSwitching.l(i,bus_s)$numBswitched(i,bus_s) =
    abs(V_shunt.l(i,bus_s) - numShuntStepsOn_init(i,bus_s));

    V_shuntSwitchingPenalty.l(i,bus_s)$numBswitched(i,bus_s) =
    max(0,
    shuntSwitchingPenalty1 * V_shuntSwitching.l(i,bus_s),
    shuntSwitchingPenalty2 * (V_shuntSwitching.l(i,bus_s) - shuntSwitchingTolerance));

    V_totalShuntSwitching.l =
    max(0,
    sum((i,bus_s)$numBswitched(i,bus_s),V_shuntSwitching.l(i,bus_s)));

    V_shuntTotalSwitchingPenalty.l =
    max(0,
    shuntSwitchingBudgetPenalty * (V_totalShuntSwitching.l - shuntSwitchingBudget));

    V_shuntSwitchingTotalPenalty.l =
    max(0,
    V_shuntTotalSwitchingPenalty.l +
    sum((i,bus_s)$numBswitched(i,bus_s),V_shuntSwitchingPenalty.l(i,bus_s)));

    V_previous_solution_penalty.l = 0;

    V_objcost.l =
           V_shuntSwitchingTotalPenalty.l
         + V_load_bus_volt_pen.l
         + solar_curtail_penalty * sum(i,Solar_p_curtail.l(i))
         + demand_response_increase_penalty * sum(i,De_response_Inc_P.l(i))
         - demand_response_decrease_penalty * sum(i,De_response_Dec_P.l(i))
         + sum(i,V_Lossi.l(i))
	 + V_previous_solution_penalty.l;

    V_objcosttest.l =
           V_objcost.l
	 + generator_voltage_deviation_penalty
             * sum(bus$(sum(gen,status2(gen,bus)) eq 1),  V_artup.l(bus))
         + generator_voltage_deviation_penalty
             * sum(bus$(sum(gen,status2(gen,bus)) eq 1),  V_artlow.l(bus));
