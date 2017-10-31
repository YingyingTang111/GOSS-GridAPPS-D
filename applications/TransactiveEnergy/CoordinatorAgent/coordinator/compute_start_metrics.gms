$title compute_start_metrics
$ontext
evaluate individual componenets of feasibility and optimality for the start point
$offtext

* set these from variable levels
    V_P_start(gen) = V_P.l(gen);
    V_Q_start(gen) = V_Q.l(gen);
    P_S_start(i) = P_S.l(i);
    Q_S_start(i) = Q_S.l(i);
    V_real_start(i) = V_real.l(i);
    V_imag_start(i) = V_imag.l(i);
    Solar_p_curtail_start(i) = solar_p_curtail.l(i);
    De_response_Dec_P_start(i) = de_response_dec_p.l(i);
    De_response_Inc_P_start(i) = de_response_inc_p.l(i);
    V_switchedshuntB_start(i)$sum(bus_s$numBswitched(i,bus_s), 1) = V_switchedshuntB.l(i);
    V_shunt_start(bus,bus_s) = v_shunt.l(bus,bus_s);
    V_P_system_deviation_start = v_p_system_deviation.l;
    V_LineIr_start(i,j,c)$(branchstatus(i,j,c)) = V_LineIr.l(i,j,c);
    V_LineIr_start(j,i,c)$(branchstatus(i,j,c)) = V_LineIr.l(j,i,c);
    V_LineIq_start(i,j,c)$(branchstatus(i,j,c)) = V_LineIq.l(i,j,c);
    V_LineIq_start(j,i,c)$(branchstatus(i,j,c)) = V_LineIq.l(j,i,c);

* compute losses
    V_Lossijc_start(i,j,c)$(branchstatus(i,j,c)) =
               g(i,j,c)/( sqr(b(i,j,c))+ sqr(g(i,j,c)) ) * (  sqr(V_LineIr_start(i,j,c))+ sqr(V_LineIq_start(i,j,c)) );
    V_Lossi_start(i) = sum((j,c)$(branchstatus(i,j,c)),V_Lossijc_start(i,j,c));

* compute penalties and objectives
    V_load_bus_volt_pen_dev_start(i)$bus_penalize_volt_mag_target(i) = abs(
          sqrt(sqr(V_real_start(i)) + sqr(V_imag_start(i)))
        - volt_mag_target(i)
        - load_bus_volt_dead_band);
    V_load_bus_volt_pen_start =
        sum(i$bus_penalize_volt_mag_target(i),
              load_bus_volt_pen_coeff_1 * V_load_bus_volt_pen_dev_start(i)
            + load_bus_volt_pen_coeff_2 * sqr(V_load_bus_volt_pen_dev_start(i)));
    V_shuntSwitching_start(i,bus_s)$numBswitched(i,bus_s) =
        abs(V_shunt_start(i,bus_s) - numShuntStepsOn_init(i,bus_s));
    V_totalShuntSwitching_start =
        sum((i,bus_s)$numBswitched(i,bus_s),V_shuntSwitching_start(i,bus_s));
    V_shuntSwitchingPenalty_start(i,bus_s)$numBswitched(i,bus_s) = max(0,
        shuntSwitchingPenalty1 * V_shuntSwitching_start(i,bus_s),
        shuntSwitchingPenalty2 * (V_shuntSwitching_start(i,bus_s) - shuntSwitchingTolerance));
    V_shuntTotalSwitchingPenalty_start =
        shuntSwitchingBudgetPenalty * max(0, V_totalShuntSwitching_start - shuntSwitchingBudget);
    V_shuntSwitchingTotalPenalty_start =
          V_shuntTotalSwitchingPenalty_start
        + sum((i,bus_s)$numBswitched(i,bus_s),V_shuntSwitchingPenalty_start(i,bus_s));
    V_previous_solution_penalty_start =
      previous_solution_penalty_2 * (
          sum(gen, sqr(V_P_prior(gen) - V_P_start(gen)))
        + sum(gen, sqr(V_Q_prior(gen) - V_Q_start(gen)))
        + sum(i, sqr(P_S_prior(i) - P_S_start(i)))
        + sum(i, sqr(Q_S_prior(i) - Q_S_start(i)))
        + sum(i, sqr(V_real_prior(i) - V_real_start(i)))
        + sum(i, sqr(V_imag_prior(i) - V_imag_start(i)))
        + sum(i, sqr(Solar_p_curtail_prior(i) - Solar_p_curtail_start(i)))
        + sum(i, sqr(De_response_Inc_P_prior(i) - De_response_Inc_P_start(i)))
        + sum(i, sqr(De_response_Dec_P_prior(i) - De_response_Dec_P_start(i))));
    V_objcost_start =
           V_shuntSwitchingTotalPenalty_start
         + V_load_bus_volt_pen_start
         + solar_curtail_penalty * sum(i,Solar_p_curtail_start(i))
         + demand_response_increase_penalty * sum(i,De_response_Inc_P_start(i))
         - demand_response_decrease_penalty * sum(i,De_response_Dec_P_start(i))
         + sum(i,V_Lossi_start(i))
         + V_previous_solution_penalty_start;

* compute variable bound violations
    gen_p_lo_viol_start(gen)$status(gen) =
        max(0, pmin(gen) - v_p_start(gen));
    gen_p_up_viol_start(gen)$status(gen) =
        max(0, v_p_start(gen) - pmax(gen));
    gen_q_lo_viol_start(gen)$status(gen) =
        max(0, qmin(gen) - v_q_start(gen));
    gen_q_up_viol_start(gen)$status(gen) =
        max(0, v_q_start(gen) - qmax(gen));
    De_response_Inc_P_up_viol_start(bus)$(Pd_respon_location(bus)) =
        max(0, de_response_inc_p_start(bus) - Pd_respon_p_up(bus));
    De_response_dec_P_lo_viol_start(bus)$(Pd_respon_location(bus)) =
        max(0, Pd_respon_p_down(bus) - de_response_dec_p_start(bus));
    v_shunt_up_viol_start(bus,bus_s)$numbswitched(bus,bus_s) =
        max(0, v_shunt_start(bus,bus_s) - numbswitched(bus,bus_s));

* compute constraint violations
    balance_p_viol_start(i)$(type(i) ne 4) =
          sum(gen$(atBus(gen,i) and status(gen)), V_P_start(gen))
        - Pd(i)
        - De_response_Inc_P_start(i)$Pd_respon_location(i)
        - De_response_Dec_P_start(i)$Pd_respon_location(i)
        + P_S_start(i)$sum(solarbus,solarlocation(solarbus,i))
        - Solar_p_curtail_start(i)$contro_solar_location(i)
        - V_real_start(i) *
          (  sum((j,c)$(branchstatus(i,j,c)), V_LineIr_start(i,j,c))
           + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIr_start(i,j,c)) )
        - V_imag_start(i) *
          (  sum((j,c)$(branchstatus(i,j,c) ), V_LineIq_start(i,j,c))
           + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIq_start(i,j,c)))
        - Gs(i) * (sqr(V_real_start(i)) + sqr(V_imag_start(i)));
    balance_q_viol_start(i)$(type(i) ne 4) =
          sum(gen$(atBus(gen,i) and status(gen)), V_Q_start(gen))
        - Qd(i)
        - Pd_respon_q_up(i)*De_response_Inc_P_start(i)$Pd_respon_location(i)
        - Pd_respon_q_down(i)*De_response_Dec_P_start(i)$Pd_respon_location(i)
        + Q_S_start(i)$sum(solarbus,solarlocation(solarbus,i))
        + V_real_start(i) *
          (  sum((j,c)$(branchstatus(i,j,c) ), V_LineIq_start(i,j,c))
           + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIq_start(i,j,c)))
        - V_imag_start(i) *
          (  sum((j,c)$(branchstatus(i,j,c) ), V_LineIr_start(i,j,c))
           + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIr_start(i,j,c)))
        + (Bs(i) + V_switchedShuntB_start(i)$sum(bus_s$numBswitched(i,bus_s), 1)) * (sqr(V_real_start(i)) + sqr(V_imag_start(i)));
    p_generator_add_viol_start(gen)$(status(gen) eq 1) =
          V_P_start(gen)
        - PgSch(gen)
        - gen_participation_factor(gen) * V_P_system_deviation_start;
    c_I_limit_viol_start(i,j,c)$(branchstatus(i,j,c) or branchstatus(j,i,c)) =
*        max(0,  sqrt(sqr(V_LineIr_start(i,j,c)) + sqr(V_LineIq_start(i,j,c)))
*              - currentrate(i,j,c));
0;
* NOTE: currentrate apparently is not defined and we are not enforcing this constraint
    c_V_limit_lo_viol_start(i) =
        max(0, minVm(i) - sqrt(sqr(V_real_start(i)) + sqr(V_imag_start(i))));
    c_V_limit_up_viol_start(i) =
        max(0, sqrt(sqr(V_real_start(i)) + sqr(V_imag_start(i))) - maxVm(i));
    v_generator_hardupl_viol_start(i) =
        max(0, sqrt(sqr(V_real_start(i)) + sqr(V_imag_start(i))) - 1.15);
    v_generator_harddownl_viol_start(i) =
        max(0, 0.88 - sqrt(sqr(V_real_start(i)) + sqr(V_imag_start(i))));
    v_under_q_up_slack_viol_start(gen)$status(gen) =
        sum(i$atbus(gen,i),
            min(max(0, vsch(i) - sqrt(sqr(v_real_start(i)) + sqr(v_imag_start(i)))),
                max(0, qmax(gen) - v_q_start(gen))));
    v_over_q_lo_slack_viol_start(gen)$status(gen) =
        sum(i$atbus(gen,i),
            min(max(0, sqrt(sqr(v_real_start(i)) + sqr(v_imag_start(i))) - vsch(i)),
                max(0, v_q_start(gen) - qmin(gen))));

* compute summaries
    p_load_start = sum(i, pd(i));
    p_gen_start = sum(gen$status(gen), V_P_start(gen));
    p_shunt_start = sum(i, Gs(i) * (sqr(V_real_start(i)) + sqr(V_imag_start(i))));
    p_solar_start
      = sum(i$sum(solarbus,solarlocation(solarbus,i)), P_S_start(i))
      - sum(i$contro_solar_location(i), Solar_p_curtail_start(i));
    p_dr_start
      = sum(i$Pd_respon_location(i), De_response_Inc_P_start(i))
      + sum(i$Pd_respon_location(i), De_response_Dec_P_start(i));
    p_imbalance_start
      = p_gen_start
      - p_load_start
      - p_shunt_start
      + p_solar_start
      - p_dr_start;
    sum_loss_start = sum(i,v_lossi_start(i));
*    v_load_bus_volt_pen_start
*    v_totalshuntswitching_start
*    v_shuntswitchingtotalpenalty_start
*    v_previous_solution_penalty_start
*    v_objcost_start
    max_gen_p_lo_viol_start = smax(gen$status(gen), gen_p_lo_viol_start(gen));
    max_gen_p_up_viol_start = smax(gen$status(gen), gen_p_up_viol_start(gen));
    max_gen_q_lo_viol_start = smax(gen$status(gen), gen_q_lo_viol_start(gen));
    max_gen_q_up_viol_start = smax(gen$status(gen), gen_q_up_viol_start(gen));
    max_De_response_Inc_P_up_viol_start = smax(bus$Pd_respon_location(bus), de_response_inc_p_up_viol_start(bus));
    max_De_response_dec_P_lo_viol_start = smax(bus$Pd_respon_location(bus), de_response_dec_p_lo_viol_start(bus));
    max_v_shunt_up_viol_start = smax((bus,bus_s)$numbswitched(bus,bus_s), v_shunt_up_viol_start(bus,bus_s));
    max_balance_p_viol_start = smax(i$(type(i) ne 4), abs(balance_p_viol_start(i)));
    max_balance_q_viol_start = smax(i$(type(i) ne 4), abs(balance_q_viol_start(i)));
    max_p_generator_add_viol_start = smax(gen$(status(gen) eq 1), abs(p_generator_add_viol_start(gen)));
    max_c_I_limit_viol_start = smax((i,j,c)$(branchstatus(i,j,c) or branchstatus(j,i,c)), c_i_limit_viol_start(i,j,c));
    max_c_V_limit_lo_viol_start = smax(i, c_v_limit_lo_viol_start(i));
    max_c_V_limit_up_viol_start = smax(i, c_v_limit_up_viol_start(i));
    max_v_generator_hardupl_viol_start = smax(i, v_generator_hardupl_viol_start(i));
    max_v_generator_harddownl_viol_start = smax(i, v_generator_harddownl_viol_start(i));
    max_v_under_q_up_slack_viol_start = smax(gen$status(gen), v_under_q_up_slack_viol_start(gen));
    max_v_over_q_lo_slack_viol_start = smax(gen$status(gen), v_over_q_lo_slack_viol_start(gen));
