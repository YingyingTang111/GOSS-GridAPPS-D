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
$if not set load_bus_voltage_goal $set load_bus_voltage_goal 1.0

* disable solar ?
$if not set solar_off $set solar_off 0

$if not set solar_curtailment_off $set solar_curtailment_off 0

* disable demand response?
$if not set demand_response_off $set demand_response_off 0

* disable solar reactive power?
$if not set solar_q_off $set solar_q_off 0

* disable switched shunts?
$if not set shunt_switching_off $set shunt_switching_off 0

* start optimization algorithm at previous solution?
$if not set previous_solution_as_start_point $set previous_solution_as_start_point 1

* initial starting point
$if not set ic $set ic 0

* quadratic penalty on distance to previous solution
$if not set previous_solution_penalty_2 $set previous_solution_penalty_2 0

