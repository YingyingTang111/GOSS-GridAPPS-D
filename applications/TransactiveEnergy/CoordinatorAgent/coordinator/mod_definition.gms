
model base_model /
$ifthen %use_constrs%==1
    bounds_model
$endif
**    c_I_limit
**    c_V_limit_lo
**    c_V_limit_up
    c_LineIrij
    c_LineIrji
    c_LineIqij
    c_LineIqji
    c_BalanceP_nosolar
    c_BalanceP_solar
    c_BalanceQ_nosolar
    c_BalanceQ_solar
    c_Lossijc
    c_Lossi
    v_generator_hardupl
    v_generator_harddownl
    p_generator_add
    c_BalanceP_control_solar
    c_switchedshuntB_def
    c_shuntSwitchingDef1
    c_shuntSwitchingDef2
    c_totalShuntSwitchingDef
    c_shuntSwitchingPenaltyDef1
    c_shuntSwitchingPenaltyDef2
    c_shuntTotalSwitchingPenalty
    c_shuntSwitchingTotalPenaltyDef
    c_previous_solution_penalty_def
    /;
model feas /
    base_model
    v_generator_addup
    v_generator_addlow
    /;
model test /
    base_model
    v_generator_addup_arti
    v_generator_addlow_arti
    /;
model acopf /
    feas
    c_obj
    /;
model acopf_check /
    test
    c_objtest
    /;
model acopf_arctan /
    base_model
    c_gen_q_arctan_v
    c_obj /;
