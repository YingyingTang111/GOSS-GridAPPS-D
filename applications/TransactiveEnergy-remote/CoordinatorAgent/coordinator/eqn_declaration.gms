equations
    c_load_bus_volt_pen_def "defines total load bus voltage deviation penalty"
    c_load_bus_volt_pen_dev_def1(i) "first constraint defining penalized load bus voltage deviation"
    c_load_bus_volt_pen_dev_def2(i) "second constraint defining penalized load bus voltage deviation"

    c_switchedshuntB_Def(i) "defines total susceptance from switched shunts at bus i"
    c_shuntSwitchingDef1(i,bus_s) "defines number of steps switched - side 1"
    c_shuntSwitchingDef2(i,bus_s) "defines number of steps switched - side 2"
    c_totalShuntSwitchingDef "defines total number of steps switched"
    c_shuntSwitchingPenaltyDef1(i,bus_s) "defines local shunt switching penalty - segment 1"
    c_shuntSwitchingPenaltyDef2(i,bus_s) "defines local shunt switching penalty - segment 2"
    c_shuntTotalSwitchingPenalty "defines penalty incurred by total shunt switching"
    c_shuntSwitchingTotalPenaltyDef " defines total penalty incurrent by shunt switching"

    c_I_limit(i,j,c)     "Limit apparent current on a line"
    c_V_limit_lo(i)      "Limit voltage magnitude on a line"
    c_V_limit_up(i)      "Limit voltage magnitude on a line"
    c_LineIrij(i,j,c)    "Real current flowing from bus i into bus j along line c"
    c_LineIrji(i,j,c)    "Real  current flowing from bus j into bus i along line c"
    c_LineIqij(i,j,c)    "Reactive current  flowing from bus i into bus j along line c"
    c_LineIqji(i,j,c)    "Reactive current flowing from bus j into bus i along line c"

    c_Lossijc(i,j,c)     "Loss on line c connecting bus i and bus j"
    c_Lossi(i)           "Loss on lines connected with bus i"

    c_BalanceP_nosolar(bus)      "Balance of real power for bus without solar"
    c_BalanceP_solar(bus)      "Balance of real power for bus with solar"
    c_BalanceP_control_solar(bus)        "balance of real power for controllable solar"
    c_BalanceQ_nosolar(bus)      "Balance of reactive power for bus without solar"
    c_BalanceQ_solar(bus)      "Balance of reactive power for bus with solar"
    v_generator_addup(bus) "generator voltage constraints added selectively"
    v_generator_addlow(bus) "generator voltage constraints added"
    v_generator_addup_arti(bus)  "generator voltage up constraints added with artificial variables"
    v_generator_addlow_arti(bus)  "generator voltage low constraints added with artificial variables"
    v_generator_hardupl(bus) "bus voltage constraints upper bound"
    v_generator_harddownl(bus) "bus voltage constraints lower bound"
    p_generator_add(gen) "enforces generator participation factor in adjustment from schedule"
    p_generator_addup(gen) "generator real power constraints added"
    p_generator_addlow(gen) "generator real power constraints added"
    c_obj  "Objective function"
    c_objtest  "Objective function"
    c_previous_solution_penalty_def "defines previous solution deviation penalty"
    c_gen_q_arctan_v(gen) "smooth arctan formulation of pv/pq complementarity constraint"
;
