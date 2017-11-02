$title "AC optimal power flow model, rectangular current-voltage formulation"
*this file is modified by Xinda Ke from Wisconsin university IV_acopf.gms
*updated by xinda ke in 8/1/2016
*_______________________________________________________________________________
* Filename: iv_acopf.gms
* Description: AC optimal power flow model, rectangular current-voltage formulation
*
* Usage: gams iv_acopf.gms --case=/path/case.gdx
*
* Options:
* --timeperiod: Select time period to solve. Default=1
* --obj: Objective function, piecewise linear or quadratic. Default="quad"
* --obj: Objective function, the default is to minimize for voltage deviation Default="v_dev"
* --linelimits: Type of line limit data to use. Default="given"
* --genPmin: Data for Generator lower limit. Default="given"
* --allon: Option to turn on all gens or lines during solve. Default=none
* --savesol: Turn on save solution option(1). Default=0
* --verbose: Supresses printout(0). Default=1
*_______________________________________________________________________________







*===== SECTION: USER PARAMETERS
*$include user_params.gms

* switched shunt user parameters
* later these will be passed in from Python
$if not set shuntSwitchingPenalty1 $set shuntSwitchingPenalty1 1e-3
$if not set shuntSwitchingPenalty2 $set shuntSwitchingPenalty2 1e6
$if not set shuntSwitchingTolerance $set shuntSwitchingTolerance 1e0
$if not set shuntSwitchingBudgetPenalty $set shuntSwitchingBudgetPenalty 1e6
$if not set shuntSwitchingBudget $set shuntSwitchingBudget 5e0

* other penalty parameters
$if not set demand_response_decrease_penalty $set demand_response_decrease_penalty 10
$if not set demand_response_increase_penalty $set demand_response_increase_penalty 10
$if not set solar_curtail_penalty $set solar_curtail_penalty 50
$if not set generator_voltage_deviation_penalty $set generator_voltage_deviation_penalty 1e5
$if not set load_bus_volt_pen_coeff_1 $set load_bus_volt_pen_coeff_1 1
$if not set load_bus_volt_pen_coeff_2 $set load_bus_volt_pen_coeff_2 0
$if not set load_bus_volt_dead_band $set load_bus_volt_dead_band 1e-2

* load bus voltage goal point
* TODO: replace this with a gdx file containing individual goal
* values for the buses
$if not set load_bus_voltage_goal $set load_bus_voltage_goal 1.0

$if not set load_bus_voltage_goal_from_file $set load_bus_voltage_goal_from_file 0

$if not set load_bus_voltage_goal_file $set load_bus_voltage_goal_file load_bus_voltage_goal.gdx

* disable solar ?
$if not set solar_off $set solar_off 0

$if not set solar_curtailment_off $set solar_curtailment_off 1

* disable demand response?
$if not set demand_response_off $set demand_response_off 1
* disable controllable solar q limit
$if not set solar_q_boun_adjust_off $set solar_q_boun_adjust_off 1
* disable solar reactive power?
$if not set solar_q_off $set solar_q_off 0

* disable switched shunts?
$if not set shunt_switching_off $set shunt_switching_off 1

* start optimization algorithm at previous solution?
$if not set previous_solution_as_start_point $set previous_solution_as_start_point 0

* initial starting point
$if not set ic $set ic 9

* quadratic penalty on distance to previous solution
$if not set previous_solution_penalty_2 $set previous_solution_penalty_2 0

* use constraints in addition to variable bounds
$if not set use_constrs $set use_constrs 0

* append to report file
$if not set append_report $set append_report 0

* use pv/pq smoothing approach
$if not set use_pv_pq_smoothing $set use_pv_pq_smoothing 0

* pv/pq smoothing parameter
$if not set pv_pq_smoothing_param $set pv_pq_smoothing_param 0.001

* report file
$if not set reporttxt $set reporttxt report.txt

* write excel reports
$if not set do_excel_reports $set do_excel_reports 0

* use soft constraints for power balance
$if not set use_soft_balance_constrs $set use_soft_balance_constrs 0

* penalty parameter for soft power balance constraints
$if not set balance_constr_penalty $set balance_constr_penalty 1e3

*===== SECTION: DEVELOPER PARAMETERS
*$include developer_params.gms

* System dependence
$if %system.filesys% == UNIX $set sep '/'
$if not %system.filesys% == UNIX $set sep '\'

*define the path and name of case to be used
$if not set case $set  case "7bus.gdx"
*$if not set case $set  case "Dukeare342.gdx"

* Printout options
$ifthen %verbose% == 0
* Turn off print options
$offlisting
option limrow=0, limcol=0
$endif
* Define filepath, name and extension.
$setnames "%gams.i%" filepath filename fileextension
* Define input case

$if not set case $abort "Model aborted. Please provide input case"
$setnames "%case%" casepath casename caseextension

*$set obj "pwl"

* Default: timeperiod = 1
$if not set timeperiod $set timeperiod "1"
* Default: allon=0
$if not set allon $set allon 0
* Default: Quadratic objective function
$if not set obj $set obj "v_dev"
* Default: Ignore D-curve constraints
*$if not set qlim $set qlim 0
* Default: elastic demand bidding does not apply here
$set demandbids 0
* Default: Use provided line limits (as opposed to uwcalc)
$if not set linelimits $set linelimits "given"
* Default: Use provided generator lower limit
$if not set genPmin $set genPmin "0"
* Default: Save solution option turned off
$if not set savesol $set savesol 0

$set condensed 'no'

*===== SECTION: EXTRACT DATA
*$batinclude "%filepath%excel2gdx4ACOPF.gms"  excelpath solar_rp demand_P demand_Q gen_status geni_psch
$batinclude "%filepath%extract_data_SunLamp_newformulation_cle.gms" excelpath timeperiod demandbids linelimits genPmin allon demand_response_off solar_curtailment_off solar_q_boun_adjust_off
* load prior sol switched shunt settings if this is not the first time step
$ifthen exist 'switched_shunt_current.gdx'
execute_load 'switched_shunt_current.gdx', numShuntStepsOn_init=numShuntStepsOn;
$endif

*===== SECTION: PARAMETERS FROM USER
$include params_from_user.gms

*===== SECTION: MODEL PARAMETERS
$include model_params.gms

*===== SECTION: DATA MANIPULATION
$include data_manipulation.gms

*===== SECTION: VARIABLE DEFINITION
$include var_declaration.gms
*display  V_real.l;
*===== SECTION: EQUATION DECLARATION
$include eqn_declaration.gms
*display V_P.l,V_P.up, V_P.lo;
*===== SECTION: EQUATION DEFINITION
$include eqn_definition.gms
*display Pmax, Pmin, V_P.l;
*===== SECTION: MODEL DEFINITION
$include mod_definition.gms
display Pmax, Pmin, Pd, Va, Vm, Qg, Gs, b, bc;
*===== SECTION: VARIABLE BOUNDS
$include var_bounds.gms

*===== SECTION: VARIABLE START VALUES
$include start_point.gms
*===== SECTION: COMPUTE START METRICS
$include compute_start_metrics.gms

*===== SECTION: DISPLAY START METRICS
$include display_start.gms

*===== SECTION: MODEL OPTIONS AND SOLVE
$ifthen %use_pv_pq_smoothing%==1
$include solve_procedure_pv_pq_smoothing.gms
$else
$include solve_procedure.gms
$endif



*===== SECTION: SOLUTION ANALYSIS
$include solution_analysis.gms

*==== SECTION: SOLUTION SAVE
$include solution_save.gms
display Pmax, Pmin,ratio,switchedShuntB_init, V_dem_Load.l, V_switchedshuntB.l,V_P.l,V_P.up, V_P.lo, V_Q.l, V_Q.up, V_Q.lo, Qmax, Qmin;
