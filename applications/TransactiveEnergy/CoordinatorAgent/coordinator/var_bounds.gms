
* shunt switching
V_shunt.lo(bus,bus_s)$numBswitched(bus,bus_s) = 0;
V_shunt.up(bus,bus_s)$numBswitched(bus,bus_s) = numBswitched(bus,bus_s);
$ifthen %shunt_switching_off% == 1
V_shunt.fx(bus,bus_s)$numBswitched(bus,bus_s) = numShuntStepsOn_init(bus,bus_s);
$endif

* Generator active power generation limits
V_P.lo(gen)$(status(gen) and abs(gen_participation_factor(gen))) = Pmin(gen);
V_P.up(gen)$(status(gen) and abs(gen_participation_factor(gen))) = Pmax(gen);
V_P.fx(gen)$(status(gen) and not abs(gen_participation_factor(gen))) = PgSch(gen);
V_P.fx(gen)$(not status(gen)) = 0;


$ifthen %solar_curtailment_off%==1
Solar_p_curtail.fx(bus)=0;
contro_solar_location(bus) = 0;
$else
Solar_p_curtail.up(bus)$contro_solar_location(bus)=contro_solar_pout(bus);
Solar_p_curtail.lo(bus)$contro_solar_location(bus)=0;
Solar_p_curtail.fx(bus)$(not contro_solar_location(bus))=0;
$endif



V_dem_Load.up(demanStep)$(ord(demanStep) > 1)=  demLoad(demanStep)-demLoad(demanStep-1);
V_dem_Load.fx('1')=0;
Q_s.lo('13')=-300;
Q_s.lo('57')=-300;
Q_s.up('13')=300;
Q_s.up('57')=300;


P_S.lo('13')=0.03;
P_S.lo('57')=0.02;
P_S.up('13')=0.3;
P_S.up('57')=0.25;




De_response_Inc_P.up(bus)$(Pd_respon_location(bus))=Pd_respon_p_up(bus);
De_response_Inc_P.lo(bus)$(Pd_respon_location(bus))=0;
De_response_Inc_P.fx(bus)$(not Pd_respon_location(bus))=0;

De_response_Dec_P.lo(bus)$(Pd_respon_location(bus))=Pd_respon_p_down(bus);
De_response_Dec_P.up(bus)$(Pd_respon_location(bus))=0;
De_response_Dec_P.fx(bus)$(not Pd_respon_location(bus))=0;



* disable demand response
$ifthen %demand_response_off%==1
Pd_respon_location(bus) = 0;
De_response_Dec_P.fx(bus) = 0;
De_response_Inc_P.fx(bus) = 0;
$endif

* Generator reactive power generation limits
* Does not impose Qmax, Qmin limits when the D-curve contraint is applied
*$ifthen %qlim% == 0
V_Q.lo(gen)$status(gen) = Qmin(gen);
V_Q.up(gen)$status(gen) = Qmax(gen);
*$endif
V_Q.fx(gen)$(not status(gen)) = 0;
*display V_Q.l, V_Q.up, V_Q.lo;
* Bus voltage magnitude limits
* Note these bounds are numerically helpful
* even if they are not necessary for the correctness
* of the formulation
V_real.lo(bus) = -MaxVm(bus); V_real.up(bus) = MaxVm(bus);
V_imag.lo(bus) = -MaxVm(bus); V_imag.up(bus) = MaxVm(bus);
V_imag.fx(bus)$(type(bus) eq 3) = 0;

* disable solar q
$ifthen %solar_q_off%==1
Q_S.fx(i) = 0;
$endif


* soft power balance constraints
balance_real_bound=0.01;
balance_react_bound=0.01;
$ifthen %use_soft_balance_constrs% == 0
V_p_over.fx(i) = 0;
V_p_under.fx(i) = 0;
V_q_over.fx(i) = 0;
V_q_under.fx(i) = 0;
$else
V_p_over.up(i) = balance_real_bound;
V_p_under.up(i) = balance_real_bound;
V_q_over.up(i) = balance_react_bound;
V_q_under.up(i) = balance_react_bound;

$endif
