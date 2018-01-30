$title display_start
$ontext
Display variable values, constraint violations, bound violations, penalties, objectives, and summaries at the start point
$offtext

display
    "display start"
* data
    Pd
    Qd
* control variables
    V_P_start
    V_Q_start
    P_S_start
    Q_S_start
    V_real_start
    V_imag_start
    Solar_p_curtail_start
    De_response_Dec_P_start
    De_response_Inc_P_start
    V_switchedshuntB_start
    V_shunt_start
    V_P_system_deviation_start
* current
    V_LineIr_start
    V_LineIq_start
* losses
    V_Lossijc_start
    V_Lossi_start
* penalties and objectives
    V_load_bus_volt_pen_dev_start
    V_load_bus_volt_pen_start
    V_shuntSwitching_start
    V_totalShuntSwitching_start
    V_shuntSwitchingPenalty_start
    V_shuntTotalSwitchingPenalty_start
    V_shuntSwitchingTotalPenalty_start
    V_previous_solution_penalty_start
    V_objcost_start
* variable bound violations
    gen_p_lo_viol_start
    gen_p_up_viol_start
    gen_q_lo_viol_start
    gen_q_up_viol_start
    De_response_Inc_P_up_viol_start
    De_response_dec_P_lo_viol_start
    v_shunt_up_viol_start
* constraint violations
    balance_p_viol_start
    balance_q_viol_start
    p_generator_add_viol_start
    c_I_limit_viol_start
    c_V_limit_lo_viol_start
    c_V_limit_up_viol_start
    v_generator_hardupl_viol_start
    v_generator_harddownl_viol_start
    v_under_q_up_slack_viol_start
    v_over_q_lo_slack_viol_start
* summaries
    "display start summary"
    p_load_start
    p_gen_start
    p_shunt_start
    sum_loss_start
    v_load_bus_volt_pen_start
    v_totalshuntswitching_start
    v_shuntswitchingtotalpenalty_start
    v_previous_solution_penalty_start
    v_objcost_start
    max_gen_p_lo_viol_start
    max_gen_p_up_viol_start
    max_gen_q_lo_viol_start
    max_gen_q_up_viol_start
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

$ifthen %do_excel_reports%==1
execute_unload 'report_start.gdx',
* data
    Pd
    Qd
    solar_r
    atbus
    status
* control variables
    V_P_start
    V_Q_start
    P_S_start
    Q_S_start
    V_real_start
    V_imag_start
    Solar_p_curtail_start
    De_response_Dec_P_start
    De_response_Inc_P_start
    V_switchedshuntB_start
    V_shunt_start
    V_P_system_deviation_start
* current
    V_LineIr_start
    V_LineIq_start
* losses
    V_Lossijc_start
    V_Lossi_start
* penalties and objectives
    V_load_bus_volt_pen_dev_start
    V_load_bus_volt_pen_start
    V_shuntSwitching_start
    V_totalShuntSwitching_start
    V_shuntSwitchingPenalty_start
    V_shuntTotalSwitchingPenalty_start
    V_shuntSwitchingTotalPenalty_start
    V_previous_solution_penalty_start
    V_objcost_start
* variable bound violations
    gen_p_lo_viol_start
    gen_p_up_viol_start
    gen_q_lo_viol_start
    gen_q_up_viol_start
    solar_p_fx_viol_start
    solar_q_up_viol_start
    solar_q_lo_viol_start
    solar_p_curtail_up_viol_start
    De_response_Inc_P_up_viol_start
    De_response_dec_P_lo_viol_start
    v_shunt_up_viol_start
* constraint violations
    balance_p_viol_start
    balance_q_viol_start
    p_generator_add_viol_start
    c_I_limit_viol_start
    c_V_limit_lo_viol_start
    c_V_limit_up_viol_start
    v_generator_hardupl_viol_start
    v_generator_harddownl_viol_start
    v_under_q_up_slack_viol_start
    v_over_q_lo_slack_viol_start
* summaries
    p_load_start
    p_gen_start
    p_shunt_start
    sum_loss_start
    v_load_bus_volt_pen_start
    v_totalshuntswitching_start
    v_shuntswitchingtotalpenalty_start
    v_previous_solution_penalty_start
    v_objcost_start
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

$onecho > gdxxrwcmd_start.txt
i=report_start.gdx
o=report_start.xlsx
par=    Pd rng=Pd! cdim=0
par=    Qd rng=Qd! cdim=0
par=    solar_r rng=solar_r! cdim=0
par=    atbus rng=atBus! cdim=0
par=    status rng=status! cdim=0
par=V_P_start rng=V_P_start! cdim=0
par=V_Q_start rng=V_Q_start! cdim=0
par=P_S_start rng=P_S_start! cdim=0
par=Q_S_start rng=Q_S_start! cdim=0
par=V_real_start rng=V_real_start! cdim=0
par=V_imag_start rng=V_imag_start! cdim=0
par=Solar_p_curtail_start rng=Solar_p_curtail_start! cdim=0
par=De_response_Dec_P_start rng=De_response_Dec_P_start! cdim=0
par=De_response_Inc_P_start rng=De_response_Inc_P_start! cdim=0
par=V_switchedshuntB_start rng=V_switchedshuntB_start! cdim=0
par=V_shunt_start rng=V_shunt_start! cdim=0
par=V_P_system_deviation_start rng=V_P_system_dev! cdim=0
par=V_LineIr_start rng=V_LineIr_start! cdim=0
par=V_LineIq_start rng=V_LineIq_start! cdim=0
par=V_Lossijc_start rng=V_Lossijc_start! cdim=0
par=V_Lossi_start rng=V_Lossi_start! cdim=0
par=V_load_bus_volt_pen_dev_start rng=V_load_bus_volt_pen_dev_start! cdim=0
par=V_load_bus_volt_pen_start rng=V_load_bus_volt_pen_start! cdim=0
par=V_shuntSwitching_start rng=V_shuntSwitching_start! cdim=0
par=V_totalShuntSwitching_start rng=V_totalShuntSwitching_start! cdim=0
par=V_shuntSwitchingPenalty_start rng=V_shuntSwitchingPenalty_start! cdim=0
par=V_shuntTotalSwitchingPenalty_start rng=V_shuntTotalSwitchingPen! cdim=0
par=V_shuntSwitchingTotalPenalty_start rng=V_shuntSwitchingTotalPen! cdim=0
par=V_previous_solution_penalty_start rng=V_previous_solution_pen! cdim=0
par=V_objcost_start rng=V_objcost_start! cdim=0
par=gen_p_lo_viol_start rng=gen_p_lo_viol_start! cdim=0
par=gen_p_up_viol_start rng=gen_p_up_viol_start! cdim=0
par=gen_q_lo_viol_start rng=gen_q_lo_viol_start! cdim=0
par=gen_q_up_viol_start rng=gen_q_up_viol_start! cdim=0
par=solar_p_fx_viol_start rng=solar_p_fx_viol_start! cdim=0
par=solar_q_up_viol_start rng=solar_q_up_viol_start! cdim=0
par=solar_q_lo_viol_start rng=solar_q_lo_viol_start! cdim=0
par=solar_p_curtail_up_viol_start rng=solar_p_curtail_up_viol_start! cdim=0
par=De_response_Inc_P_up_viol_start rng=De_response_Inc_P_up_viol_start! cdim=0
par=De_response_dec_P_lo_viol_start rng=De_response_dec_P_lo_viol_start! cdim=0
par=v_shunt_up_viol_start rng=v_shunt_up_viol_start! cdim=0
par=balance_p_viol_start rng=balance_p_viol_start! cdim=0
par=balance_q_viol_start rng=balance_q_viol_start! cdim=0
par=p_generator_add_viol_start rng=p_generator_add_viol_start! cdim=0
par=c_I_limit_viol_start rng=c_I_limit_viol_start! cdim=0
par=c_V_limit_lo_viol_start rng=c_V_limit_lo_viol_start! cdim=0
par=c_V_limit_up_viol_start rng=c_V_limit_up_viol_start! cdim=0
par=v_generator_hardupl_viol_start rng=v_generator_hardupl_viol! cdim=0
par=v_generator_harddownl_viol_start rng=v_generator_harddownl_viol! cdim=0
par=v_under_q_up_slack_viol_start rng=v_under_q_up_slack_viol_start! cdim=0
par=v_over_q_lo_slack_viol_start rng=v_over_q_lo_slack_viol_start! cdim=0
par=p_load_start rng=p_load_start! cdim=0
par=p_gen_start rng=p_gen_start! cdim=0
par=p_shunt_start rng=p_shunt_start! cdim=0
par=sum_loss_start rng=sum_loss_start! cdim=0
par=v_load_bus_volt_pen_start rng=v_load_bus_volt_pen_start! cdim=0
par=v_totalshuntswitching_start rng=v_totalshuntswitching_start! cdim=0
par=v_objcost_start rng=v_objcost_start! cdim=0
par=max_gen_p_lo_viol_start rng=max_gen_p_lo_viol_start! cdim=0
par=max_gen_p_up_viol_start rng=max_gen_p_up_viol_start! cdim=0
par=max_gen_q_lo_viol_start rng=max_gen_q_lo_viol_start! cdim=0
par=max_gen_q_up_viol_start rng=max_gen_q_up_viol_start! cdim=0
par=max_solar_p_fx_viol_start rng=max_solar_p_fx_viol_start! cdim=0
par=max_solar_q_up_viol_start rng=max_solar_q_up_viol_start! cdim=0
par=max_solar_q_lo_viol_start rng=max_solar_q_lo_viol_start! cdim=0
par=max_solar_p_curtail_up_viol_start rng=max_solar_p_curtail_up_vi! cdim=0
par=max_De_response_Inc_P_up_viol_start rng=max_De_response_Inc_P_up_vi! cdim=0
par=max_De_response_dec_P_lo_viol_start rng=max_De_response_dec_P_lo_vi! cdim=0
par=max_v_shunt_up_viol_start rng=max_v_shunt_up_viol_start! cdim=0
par=max_balance_p_viol_start rng=max_balance_p_viol_start! cdim=0
par=max_balance_q_viol_start rng=max_balance_q_viol_start! cdim=0
par=max_p_generator_add_viol_start rng=max_p_generator_add_vi! cdim=0
par=max_c_I_limit_viol_start rng=max_c_I_limit_viol_start! cdim=0
par=max_c_V_limit_lo_viol_start rng=max_c_V_limit_lo_viol_start! cdim=0
par=max_c_V_limit_up_viol_start rng=max_c_V_limit_up_viol_start! cdim=0
par=max_v_generator_hardupl_viol_start rng=max_v_generator_hardupl_vi! cdim=0
par=max_v_generator_harddownl_viol_start rng=max_v_generator_harddownl_vi! cdim=0
par=max_v_under_q_up_slack_viol_start rng=max_v_under_q_up_slack_vi! cdim=0
par=max_v_over_q_lo_slack_viol_start rng=max_v_over_q_lo_slack_vi! cdim=0
$offecho

execute 'gdxxrw @gdxxrwcmd_start.txt';
$endif

put report_file;
report_file.ap = 1;
put
    'start point summary' /
    'p_load'
    p_load_start /
    'p_gen'
    p_gen_start /
    'p_shunt'
    p_shunt_start /
    'p_solar'
    p_solar_start /
    'p_dr'
    p_dr_start /
    'p_imbalance'
    p_imbalance_start /
    'sum_loss'
    sum_loss_start /
    'v_load_bus_volt_pen'
    v_load_bus_volt_pen_start /
    'v_totalshuntswitching'
    v_totalshuntswitching_start /
    'v_shuntswitchingtotalpenalty'
    v_shuntswitchingtotalpenalty_start /
    'v_previous_solution_penalty'
    v_previous_solution_penalty_start /
    'v_objcost'
    v_objcost_start /
    'max_gen_p_lo_viol'
    max_gen_p_lo_viol_start /
    'max_gen_p_up_viol'
    max_gen_p_up_viol_start /
    'max_gen_q_lo_viol'
    max_gen_q_lo_viol_start /
    'max_gen_q_up_viol'
    max_gen_q_up_viol_start /
    'max_De_response_Inc_P_up_viol'
    max_De_response_Inc_P_up_viol_start /
    'max_De_response_dec_P_lo_viol'
    max_De_response_dec_P_lo_viol_start /
    'max_v_shunt_up_viol'
    max_v_shunt_up_viol_start /
    'max_balance_p_viol'
    max_balance_p_viol_start /
    'max_balance_q_viol'
    max_balance_q_viol_start /
    'max_p_generator_add_viol'
    max_p_generator_add_viol_start /
    'max_c_I_limit_viol'
    max_c_I_limit_viol_start /
    'max_c_V_limit_lo_viol'
    max_c_V_limit_lo_viol_start /
    'max_c_V_limit_up_viol'
    max_c_V_limit_up_viol_start /
    'max_v_generator_hardupl_viol'
    max_v_generator_hardupl_viol_start /
    'max_v_generator_harddownl_viol'
    max_v_generator_harddownl_viol_start /
    'max_v_under_q_up_slack_viol'
    max_v_under_q_up_slack_viol_start /
    'max_v_over_q_lo_slack_viol'
    max_v_over_q_lo_slack_viol_start /;
putclose;
