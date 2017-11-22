

* generator participation in system adjustment from real generation schedule
parameter
  gen_participation_factor(gen);

sets
    load(bus) "Load buses"
    isGen(bus) "Generator buses"
    activeGen(bus) "Active generator buses"
    isLine(i,j) "Active (i,j) line"
    isSolar(bus) "solar bus";

* prior variable values
* penalize the distance of the new solution to
* these prior variables in order to promote
* continuity
parameter
    V_P_prior(gen)           "Real power generation of generator",
    V_Q_prior(gen)           "Reactive power generation of generator",
    P_S_prior(i)      "real power generation of solar bus"
    Q_S_prior(i)      "reactive power generation of solar bus"
    V_real_prior(i)          "Real part of bus voltage",
    V_imag_prior(i)          "Imaginary part of bus voltage",
    Solar_p_curtail_prior(i)    "the amount of real power cutailed from controllable",
    De_response_Dec_P_prior(i)         "the decrease in demand response",
    De_response_Inc_P_prior(i)         "the increment in demand response"
    balance_real_bound
    balance_react_bound
;

parameters
  saturaup(bus) "the saturation status of generator bus"
  saturalow(bus) "the saturation status of generator bus"
  genQtemp(gen)      "the reactive of generator ";

scalar voltageran_low,voltageran_high,step_leng;

* bus voltage target info
set
    bus_penalize_volt_mag_target(bus) "yes if the voltage magnitude target penalty should be assessed for this bus"
parameter
    volt_mag_target(bus) ideal voltage magnitude for each bus;

* variable values, constraint violation, and objective. at start point
parameter
* control variables
    V_P_start(gen)
    V_Q_start(gen)
    P_S_start(i)
    Q_S_start(i)
    V_real_start(i)
    V_imag_start(i)
    Solar_p_curtail_start(i)
    De_response_Dec_P_start(i)
    De_response_Inc_P_start(i)
    V_shunt_start(bus,bus_s)
    V_P_system_deviation_start
    V_switchedshuntB_start(i)
* current
    V_LineIr_start(i,j,c)
    V_LineIr_start(j,i,c)
    V_LineIq_start(i,j,c)
    V_LineIq_start(j,i,c)
* losses
    V_Lossijc_start(i,j,c)
    V_Lossi_start(i)
* penalties and objectives
    V_load_bus_volt_pen_dev_start
    V_load_bus_volt_pen_start
    V_shuntSwitching_start(i,bus_s)
    V_totalShuntSwitching_start
    V_shuntSwitchingPenalty_start(i,bus_s)
    V_shuntTotalSwitchingPenalty_start
    V_shuntSwitchingTotalPenalty_start
    V_previous_solution_penalty_start
    V_objcost_start
* variable bound violations
    gen_p_lo_viol_start(gen)
    gen_p_up_viol_start(gen)
    gen_q_lo_viol_start(gen)
    gen_q_up_viol_start(gen)
    solar_p_fx_viol_start(i)
    solar_q_up_viol_start(i)
    solar_q_lo_viol_start(i)
    solar_p_curtail_up_viol_start(bus)
    De_response_Inc_P_up_viol_start(bus)
    De_response_dec_P_lo_viol_start(bus)
    v_shunt_up_viol_start(bus,bus_s)
* constraint violations
    balance_p_viol_start(i)
    balance_q_viol_start(i)
    p_generator_add_viol_start(gen)
    c_I_limit_viol_start(i,j,c)
    c_V_limit_lo_viol_start(i)
    c_V_limit_up_viol_start(i)
    v_generator_hardupl_viol_start(i)
    v_generator_harddownl_viol_start(i)
    v_under_q_up_slack_viol_start(gen)
    v_over_q_lo_slack_viol_start(gen)
* summaries
    p_load_start
    p_gen_start
    p_shunt_start
    p_solar_start
    p_dr_start
    p_imbalance_start
    min_p_shortfall
    sum_loss_start
*    v_load_bus_volt_pen_start
*    v_total_shunt_switching_start
*    v_shunt_switching_total_penalty_start
*    v_previous_solution_penalty_start
*    v_objcost_start
    max_gen_p_lo_viol_start
    max_gen_p_up_viol_start
    max_gen_q_lo_viol_start
    max_gen_q_up_viol_start
    max_solar_p_fx_viol_start
    max_solar_q_up_viol_start
    max_solar_q_lo_viol_start
    max_solar_p_curtail_up_viol_start
    max_De_response_Inc_P_up_viol_start
    max_De_response_dec_P_lo_viol_start
    max_v_shunt_up_viol_start
    max_balance_p_viol_start
    max_balance_q_viol_start
    max_p_generator_add_viol_start
    max_c_I_limit_viol_start
    max_c_V_limit_lo_viol_start
    max_c_V_limit_up_viol_start
    max_v_generator_hardupl_viol_start
    max_v_generator_harddownl_viol_start
    max_v_under_q_up_slack_viol_start
    max_v_over_q_lo_slack_viol_start;

* variable values, constraint violation, and objective. at solution point
parameter
* control variables
    V_P_sol(gen)
    V_Q_sol(gen)
    P_S_sol(i)
    Q_S_sol(i)
    V_real_sol(i)
    V_imag_sol(i)
    Solar_p_curtail_sol(i)
    De_response_Dec_P_sol(i)
    De_response_Inc_P_sol(i)
    V_shunt_sol(bus,bus_s)
    V_P_system_deviation_sol
    V_switchedshuntB_sol(i)
* current
    V_LineIr_sol(i,j,c)
    V_LineIr_sol(j,i,c)
    V_LineIq_sol(i,j,c)
    V_LineIq_sol(j,i,c)
* losses
    V_Lossijc_sol(i,j,c)
    V_Lossi_sol(i)
* penalties and objectives
    V_shuntSwitching_sol(i,bus_s)
    V_totalShuntSwitching_sol
    V_shuntSwitchingPenalty_sol(i,bus_s)
    V_shuntTotalSwitchingPenalty_sol
    V_shuntSwitchingTotalPenalty_sol
    V_previous_solution_penalty_sol
    V_objcost_sol
* variable bound violations
    gen_p_lo_viol_sol(gen)
    gen_p_up_viol_sol(gen)
    gen_q_lo_viol_sol(gen)
    gen_q_up_viol_sol(gen)
    solar_p_fx_viol_sol(i)
    solar_q_up_viol_sol(i)
    solar_q_lo_viol_sol(i)
    solar_p_curtail_up_viol_sol(bus)
    De_response_Inc_P_up_viol_sol(bus)
    De_response_dec_P_lo_viol_sol(bus)
    v_shunt_up_viol_sol(bus,bus_s)
* constraint violations
    balance_p_viol_sol(i)
    balance_q_viol_sol(i)
    p_generator_add_viol_sol(gen)
    c_I_limit_viol_sol(i,j,c)
    c_V_limit_lo_viol_sol(i)
    c_V_limit_up_viol_sol(i)
    v_generator_hardupl_viol_sol(i)
    v_generator_harddownl_viol_sol(i)
    v_under_q_up_slack_viol_sol(gen)
    v_over_q_lo_slack_viol_sol(gen)
* summaries
    sum_loss_sol
*    v_load_bus_volt_pen_sol
*    v_total_shunt_switching_sol
*    v_shunt_switching_total_penalty_sol
*    v_previous_solution_penalty_sol
*    v_objcost_sol
    max_gen_p_lo_viol_sol
    max_gen_p_up_viol_sol
    max_gen_q_lo_viol_sol
    max_gen_q_up_viol_sol
    max_solar_p_fx_viol_sol
    max_solar_q_up_viol_sol
    max_solar_q_lo_viol_sol
    max_solar_p_curtail_up_viol_sol
    max_De_response_Inc_P_up_viol_sol
    max_De_response_dec_P_lo_viol_sol
    max_v_shunt_up_viol_sol
    max_balance_p_viol_sol
    max_balance_q_viol_sol
    max_p_generator_add_viol_sol
    max_c_I_limit_viol_sol
    max_c_V_limit_lo_viol_sol
    max_c_V_limit_up_viol_sol
    max_v_generator_hardupl_viol_sol
    max_v_generator_harddownl_viol_sol
    max_v_under_q_up_slack_viol_sol
    max_v_over_q_lo_slack_viol_sol;

* files for output
file report_file /'%reporttxt%'/;
report_file.nr = 2;
report_file.nd = 6;
report_file.pc = 5;
$ifthen %append_report%==1
report_file.ap = 1;
$endif
put report_file;
put 'sunlamp crest-vct prototype acopf model' /;
put 'start run' /;
putclose;
