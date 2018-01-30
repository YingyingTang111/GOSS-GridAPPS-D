$if not set filepath $setnames "%gams.i%" filepath filename fileextension

* set start point from a previous solution if one exists. error otherwise
* execute_load seems to overwrite the bounds
* while execute_loadpoint with no arguments beyond the file gives some infeasibility
* execute_loadpoint with all variables and level suffix specified seems to work.
*execute_load 'one_step_solution.gdx',
execute_loadpoint 'one_step_solution.gdx',
*execute_loadpoint 'one_step_solution.gdx';
    V_P.l
    V_Q.l
    P_S.l
    Q_S.l
    V_real.l
    V_imag.l
    V_LineIr.l
    V_LineIq.l
    V_Lossijc.l
    V_Lossi.l
    Solar_p_curtail.l
    De_response_Inc_P.l
    De_response_Dec_P.l
    V_switchedshuntB.l
    V_shunt.l
    V_load_bus_volt_pen.l
    V_load_bus_volt_pen_dev.l
    V_shuntSwitching.l
    V_totalShuntSwitching.l
    V_shuntSwitchingPenalty.l
    V_shuntTotalSwitchingPenalty.l
    V_shuntSwitchingTotalPenalty.l
    V_devi.l
    V_pw_cost.l
*    V_Pd_elastic.l
*    V_demandbid_rev.l
    V_artup.l
    V_artlow.l
    V_objcost.l
    V_objcosttest.l
    V_P_system_deviation.l;

$if %condensed% == 'no' $include '%filepath%ic_iv%sep%calc_derived_vars.gms'
