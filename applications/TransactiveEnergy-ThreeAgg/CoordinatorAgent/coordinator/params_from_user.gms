
* switched shunt penalty parameters
parameter
  shuntSwitchingPenalty1 /%shuntSwitchingPenalty1%/
  shuntSwitchingPenalty2 /%shuntSwitchingPenalty2%/
  shuntSwitchingTolerance /%shuntSwitchingTolerance%/
  shuntSwitchingBudgetPenalty /%shuntSwitchingBudgetPenalty%/
  shuntSwitchingBudget /%shuntSwitchingBudget%/;

* other penalty parameters
parameter
  load_bus_volt_pen_coeff_1 /%load_bus_volt_pen_coeff_1%/
  load_bus_volt_pen_coeff_2 /%load_bus_volt_pen_coeff_2%/
  demand_response_decrease_penalty /%demand_response_decrease_penalty%/
  demand_response_increase_penalty /%demand_response_increase_penalty%/
  solar_curtail_penalty /%solar_curtail_penalty%/
  generator_voltage_deviation_penalty /%generator_voltage_deviation_penalty%/
  previous_solution_penalty_2 /%previous_solution_penalty_2%/;

* other parameters
parameter
  previous_solution_as_start_point /%previous_solution_as_start_point%/
  load_bus_volt_dead_band /%load_bus_volt_dead_band%/
  load_bus_voltage_goal /%load_bus_voltage_goal%/
  use_constrs /%use_constrs%/
  use_pv_pq_smoothing /%use_pv_pq_smoothing%/
  pv_pq_smoothing_param /%pv_pq_smoothing_param%/;

