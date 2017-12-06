free variables
    V_P(gen)           "Real power generation of generator",
    V_Q(gen)           "Reactive power generation of generator",
    P_S(i)      "real power generation of solar bus"
    Q_S(i)      "reactive power generation of solar bus"
    V_real(i)          "Real part of bus voltage",
    V_imag(i)          "Imaginary part of bus voltage",

    V_LineIr(i,j,c)    "Real current flowing from bus i towards bus j on line c",
    V_LineIq(i,j,c)    "Reactive current flowing from bus i towards bus j on line c"

    V_Lossijc(i,j,c)      "Loss on line c connecting bus i and bus j"
    V_Lossi(i)         "Loss on lines connecting with bus i"
    V_switchedshuntB(i) "total susceptance from switched shunts connected to bus i"
;

integer variables
    V_shunt(bus,bus_s)    "number of shunt steps switched on"
;

negative variables
    De_response_Dec_P(bus)         "the decrease in demand response"
;

positive variables
    V_p_over(bus) "real power over"
    V_p_under(bus) "real power under"
    V_q_over(bus) "reactive power over"
    V_q_under(bus) "reactive power under"
    Solar_p_curtail(bus)    "the amount of real power cutailed from controllable solar bus"
    De_response_Inc_P(bus)         "the increment in demand response"
    controlLoad(bus)       "controllableload"
    V_load_bus_volt_pen "total penalty from load bus voltage deviation"
    V_load_bus_volt_pen_dev(i) "penalized load bus voltage deviation - i.e. deviation less dead band radius"
    V_shuntSwitching(i,bus_s) "number of steps switched"
    V_totalShuntSwitching "total number of steps switched"
    V_shuntSwitchingPenalty(i,bus_s) "defines local shunt switching"
    V_shuntTotalSwitchingPenalty "penalty incurred by total shunt switching"
    V_shuntSwitchingTotalPenalty "total penalty incurrent by shunt switching"
    V_devi(bus)          "absolute value of voltage deviation"
    V_pw_cost(gen)    "Generator piecewise cost"
    V_dem_Load(bus, demanStep)        "demand load level"
*    V_Pd_elastic(demandbid)     "Elastic incremental demand"
*    V_demandbid_rev(demandbid)  "Revenue from elastic incremental demand"
    V_artup(bus)       "artificial variablers"
    V_artlow(bus)       "artificial variablers"
    V_previous_solution_penalty "total penalty on deviation to previous solution"
;
* these are not necessary as the vars are defined as positive variables
*V_artup.l(bus)=0;
*V_artlow.l(bus)=0;

free variable
V_objcost  "Total cost of objective function"
V_objcosttest  "Total cost of objective function"
V_P_system_deviation "system total adjustment from real generation schedule"
;
