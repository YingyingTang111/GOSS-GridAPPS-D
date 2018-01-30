
* defines previous solution deviation penalty
c_previous_solution_penalty_def..
    V_previous_solution_penalty
      =g=
    previous_solution_penalty_2 * (
        sum(gen, sqr(V_P_prior(gen) - V_P(gen)))
      + sum(gen, sqr(V_Q_prior(gen) - V_Q(gen)))
      + sum(i, sqr(P_S_prior(i) - P_S(i)))
      + sum(i, sqr(Q_S_prior(i) - Q_S(i)))
      + sum(i, sqr(V_real_prior(i) - V_real(i)))
      + sum(i, sqr(V_imag_prior(i) - V_imag(i)))
      + sum(i, sqr(Solar_p_curtail_prior(i) - Solar_p_curtail(i)))
      + sum(i, sqr(De_response_Inc_P_prior(i) - De_response_Inc_P(i)))
      + sum(i, sqr(De_response_Dec_P_prior(i) - De_response_Dec_P(i))));

* defines total load bus voltage deviation penalty
c_load_bus_volt_pen_def..
    V_load_bus_volt_pen
      =g=
    sum(i$(bus_penalize_volt_mag_target(i) and type(i) eq 1),
          load_bus_volt_pen_coeff_1 * V_load_bus_volt_pen_dev(i)
        + load_bus_volt_pen_coeff_2 * sqr(V_load_bus_volt_pen_dev(i)))
;



* defines total susceptance from switched shunts connected to a bus
c_switchedshuntB_def(i)$sum(bus_s$numBswitched(i, bus_s), 1)..
    V_switchedshuntB(i)
      =e=
    sum(bus_s$numBswitched(i,bus_s), Bswitched(i,bus_s) * V_shunt(i,bus_s));

* defines number of steps switched - side 1
c_shuntSwitchingDef1(i,bus_s)$numBswitched(i,bus_s)..
    V_shuntSwitching(i,bus_s)
      =g=
    V_shunt(i,bus_s) - numShuntStepsOn_init(i,bus_s)
;

* defines number of steps switched - side 2
c_shuntSwitchingDef2(i,bus_s)$numBswitched(i,bus_s)..
    V_shuntSwitching(i,bus_s)
      =g=
    numShuntStepsOn_init(i,bus_s) - V_shunt(i,bus_s)
;

* defines total number of steps switched
c_totalShuntSwitchingDef..
    V_totalShuntSwitching
      =g=
    sum((i,bus_s)$numBswitched(i,bus_s),V_shuntSwitching(i,bus_s))
;

* defines local shunt switching penalty - segment 1
c_shuntSwitchingPenaltyDef1(i,bus_s)$numBswitched(i,bus_s)..
    V_shuntSwitchingPenalty(i,bus_s)
      =g=
    shuntSwitchingPenalty1 * V_shuntSwitching(i,bus_s)
;

* defines local shunt switching penalty - segment 2
c_shuntSwitchingPenaltyDef2(i,bus_s)$numBswitched(i,bus_s)..
    V_shuntSwitchingPenalty(i,bus_s)
      =g=
    shuntSwitchingPenalty2 * (V_shuntSwitching(i,bus_s) - shuntSwitchingTolerance)
;

* defines penalty incurred by total shunt switching
c_shuntTotalSwitchingPenalty..
    V_shuntTotalSwitchingPenalty
      =g=
    shuntSwitchingBudgetPenalty * (V_totalShuntSwitching - shuntSwitchingBudget)
;

* defines total penalty incurrent by shunt switching
c_shuntSwitchingTotalPenaltyDef..
    V_shuntSwitchingTotalPenalty
      =g=
    V_shuntTotalSwitchingPenalty +
    sum((i,bus_s)$numBswitched(i,bus_s),V_shuntSwitchingPenalty(i,bus_s))
;

* Limit apparent current on a line
c_I_limit(i,j,c)$(branchstatus(i,j,c) or branchstatus(j,i,c))..
    sqr(V_LineIr(i,j,c)) + sqr(V_LineIq(i,j,c))
      =l=
    sqr(currentrate(i,j,c))
;

*Limit voltage magnitude on a line
c_V_limit_lo(i)..
    sqr(V_real(i)) + sqr(V_imag(i)) =g= sqr(minVm(i))
;

*Limit voltage magnitude on a line
c_V_limit_up(i)..
    sqr(V_real(i)) + sqr(V_imag(i)) =l= sqr(maxVm(i))
;

*Real current flowing from bus i into bus j along line c
c_LineIrij(i,j,c)$(branchstatus(i,j,c))..
         V_LineIr(i,j,c) =e=
            1/sqr(ratio(i,j,c))
                * (g(i,j,c)*V_real(i) - (b(i,j,c) + bc(i,j,c)/2)*V_imag(i))
            - 1/ratio(i,j,c)
                * (  (g(i,j,c)*V_real(j) - b(i,j,c)*V_imag(j))*cos(angle(i,j,c))
                   - (g(i,j,c)*V_imag(j) + b(i,j,c)*V_real(j))*sin(angle(i,j,c))
                  )
;

*Real current flowing from bus j into bus i along line c
c_LineIrji(i,j,c)$(branchstatus(i,j,c))..
         V_LineIr(j,i,c) =e=
            (g(i,j,c)*V_real(j) - (b(i,j,c) + bc(i,j,c)/2)*V_imag(j))
            - 1/ratio(i,j,c)
                * (  (g(i,j,c)*V_real(i) - b(i,j,c)*V_imag(i))*cos(-angle(i,j,c))
                   - (g(i,j,c)*V_imag(i) + b(i,j,c)*V_real(i))*sin(-angle(i,j,c))
                  )
;

*Reactive current flowing from bus i into bus j along line c
c_LineIqij(i,j,c)$(branchstatus(i,j,c))..
         V_LineIq(i,j,c) =e=
            1/sqr(ratio(i,j,c))
                * (g(i,j,c)*V_imag(i) + (b(i,j,c) + bc(i,j,c)/2)*V_real(i))
            - 1/ratio(i,j,c)
                * (  (g(i,j,c)*V_imag(j) + b(i,j,c)*V_real(j))*cos(angle(i,j,c))
                   + (g(i,j,c)*V_real(j) - b(i,j,c)*V_imag(j))*sin(angle(i,j,c))
                  )
;

*Reactive current flowing from bus j into bus i along line c
c_LineIqji(i,j,c)$(branchstatus(i,j,c))..
         V_LineIq(j,i,c) =e=
            (g(i,j,c)*V_imag(j) + (b(i,j,c) + bc(i,j,c)/2)*V_real(j))
            - 1/ratio(i,j,c)
                * (  (g(i,j,c)*V_imag(i) + b(i,j,c)*V_real(i))*cos(-angle(i,j,c))
                   + (g(i,j,c)*V_real(i) - b(i,j,c)*V_imag(i))*sin(-angle(i,j,c))
                  )
;

*Balance of real power for bus without solar
c_BalanceP_nosolar(i)$(type(i) ne 4 and (sum(solarbus,solarlocation(solarbus,i)) eq 0))..
        sum(gen$(atBus(gen,i) and status(gen)), V_P(gen))
        - (Pd(i)+sum(demanStep ,V_dem_Load(i, demanStep))$(demLocation(i) eq 1)+ De_response_Inc_P(i)$(Pd_respon_location(i)) + De_response_Dec_P(i)$(Pd_respon_location(i))   )
        + V_p_over(i)
        - V_p_under(i)
            =e=
          V_real(i) *
        ( sum((j,c)$(branchstatus(i,j,c) ), V_LineIr(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIr(i,j,c)) )
        + V_imag(i) *
         (sum((j,c)$(branchstatus(i,j,c) ), V_LineIq(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIq(i,j,c)))
        + Gs(i) * (sqr(V_real(i)) + sqr(V_imag(i)))
;
*Balance of real power for bus with uncontrollable solar installed
c_BalanceP_solar(i)$(type(i) ne 4 and (sum(solarbus,solarlocation(solarbus,i)) ne 0) and contro_solar_location(i) eq 0)..
        sum(gen$(atBus(gen,i) and status(gen)), V_P(gen))
         - (Pd(i)+ sum(demanStep ,V_dem_Load(i,demanStep))$(demLocation(i) eq 1)- P_S(i)+De_response_Inc_P(i)$(Pd_respon_location(i)) + De_response_Dec_P(i)$(Pd_respon_location(i)))
        + V_p_over(i)
        - V_p_under(i)
            =e=
          V_real(i) *
        ( sum((j,c)$(branchstatus(i,j,c) ), V_LineIr(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIr(i,j,c)) )
        + V_imag(i) *
         (sum((j,c)$(branchstatus(i,j,c) ), V_LineIq(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIq(i,j,c)))
        + Gs(i) * (sqr(V_real(i)) + sqr(V_imag(i)))
;

c_BalanceP_control_solar(i)$(type(i) ne 4 and  contro_solar_location(i) ne 0)..
        sum(gen$(atBus(gen,i) and status(gen)), V_P(gen))
         - (Pd(i)+ sum(demanStep ,V_dem_Load(i,demanStep))$(demLocation(i) eq 1)+ De_response_Inc_P(i)$(Pd_respon_location(i))+ De_response_Dec_P(i)$(Pd_respon_location(i)) - (P_S(i)-Solar_p_curtail(i) ))
        + V_p_over(i)
        - V_p_under(i)
            =e=
          V_real(i) *
        ( sum((j,c)$(branchstatus(i,j,c) ), V_LineIr(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIr(i,j,c)) )
        + V_imag(i) *
         (sum((j,c)$(branchstatus(i,j,c) ), V_LineIq(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIq(i,j,c)))
        + Gs(i) * (sqr(V_real(i)) + sqr(V_imag(i)))
;
* Balance of reactive power for bus without solar
c_BalanceQ_nosolar(i)$(type(i) ne 4 and (sum(solarbus,solarlocation(solarbus,i)) eq 0))..
        sum(gen$(atBus(gen,i) and status(gen)), V_Q(gen))
        - (Qd(i)+Pd_respon_q_up(i)*De_response_Inc_P(i)$(Pd_respon_location(i)) + Pd_respon_q_down(i)*De_response_Dec_P(i)$(Pd_respon_location(i))  )
        + V_q_over(i)
        - V_q_under(i)
            =e=
        - V_real(i) *
        ( sum((j,c)$(branchstatus(i,j,c) ), V_LineIq(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIq(i,j,c)))
        + V_imag(i) *
        ( sum((j,c)$(branchstatus(i,j,c) ), V_LineIr(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIr(i,j,c)))
        - (Bs(i) + V_switchedshuntB(i)$sum(bus_s$numbswitched(i, bus_s), 1)) * (sqr(V_real(i)) + sqr(V_imag(i)));
;
* Balance of reactive power for bus with solar
c_BalanceQ_solar(i)$(type(i) ne 4 and (sum(solarbus,solarlocation(solarbus,i)) ne 0))..
        sum(gen$(atBus(gen,i) and status(gen)), V_Q(gen))
        - ( Qd(i)+ Pd_respon_q_up(i)*De_response_Inc_P(i)$(Pd_respon_location(i)) + Pd_respon_q_down(i)*De_response_Dec_P(i)$(Pd_respon_location(i)) - Q_S(i) )
        + V_q_over(i)
        - V_q_under(i)
            =e=
        - V_real(i) *
        ( sum((j,c)$(branchstatus(i,j,c) ), V_LineIq(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIq(i,j,c)))
        + V_imag(i) *
        ( sum((j,c)$(branchstatus(i,j,c) ), V_LineIr(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIr(i,j,c)))
        - (Bs(i) + V_switchedshuntB(i)$sum(bus_s$numbswitched(i, bus_s), 1)) * (sqr(V_real(i)) + sqr(V_imag(i)));
;

* Loss on line c connecting bus i and bus j
c_Lossijc(i,j,c)$(branchstatus(i,j,c))..
          V_Lossijc(i,j,c) =e=
               g(i,j,c)/( sqr(b(i,j,c))+ sqr(g(i,j,c)) ) * (  sqr(V_LineIr(i,j,c))+ sqr(V_LineIq(i,j,c)) )
;

*Loss on lines connected with bus i
c_Lossi(i)..
       V_Lossi(i) =e=
              sum((j,c)$(branchstatus(i,j,c)),V_Lossijc(i,j,c))
;

* generator bus voltage set points enforced with violation variables
v_generator_addup(i)$(sum(gen,status2(gen,i)) eq 1 and saturaup(i) eq 0)..
         sqrt(sqr(V_real(i)) + sqr(V_imag(i))) =l= voltageran_high*Vsch(i)
;
v_generator_addlow(i)$(sum(gen,status2(gen,i)) eq 1 and saturalow(i) eq 0)..
         sqrt(sqr(V_real(i)) + sqr(V_imag(i))) =g= voltageran_low*Vsch(i)
;


v_generator_addup_arti(i)$(sum(gen,status2(gen,i)) eq 1 )..
         sqrt(sqr(V_real(i)) + sqr(V_imag(i))) =l= voltageran_high*Vsch(i) + V_artup(i)
;
v_generator_addlow_arti(i)$(sum(gen,status2(gen,i)) eq 1 )..
         sqrt(sqr(V_real(i)) + sqr(V_imag(i))) =g= voltageran_low*Vsch(i) - V_artlow(i)
;

v_generator_hardupl(i)..
         sqrt(sqr(V_real(i)) + sqr(V_imag(i))) =l= 1.15
;

v_generator_harddownl(i)..
         sqrt(sqr(V_real(i)) + sqr(V_imag(i))) =g= 0.88
;

* enforces generator participation factor in adjustment from schedule
p_generator_add(gen)$(status(gen) eq 1 and abs(gen_participation_factor(gen)))..
         V_P(gen) =e= PgSch(gen) + gen_participation_factor(gen) * V_P_system_deviation
;

p_generator_addup(gen)$(status(gen) eq 1 and gentype(gen) eq 1)..
         V_P(gen) =l= 1.001*PgSch(gen)
;
p_generator_addlow(gen)$(status(gen) eq 1 and gentype(gen) eq 1 and PgSch(gen) > 0 )..
         V_P(gen) =g= 0.999*PgSch(gen)

;
*solar bus active power constraints uppr bound
;
* WARNING TODO JH this equation has an error
* causes infeasibility
* e.g. 0 =g= 1e-6
*
* fixed it
* Xinda can you check that this is correct?
* am I understanding the data and model correctly?
*solar bus  power constraints lower bound
;


* Objective functions and pwl costs are listed in a separate file
*$batinclude "%filepath%objective_voltage_stability_addterm.gms" obj demandbids
$title Cost objective calculations for OPF models
*this file is modified by Xinda Ke from Wisconsin university IV_acopf.gms
*updated by Xinda ke in 7/26/2016

$ontext
* Set costmodel variable
costmodel(gen)= 2;

*-- Convexity Check
* Not part of system of equations
* LP/QCP/NLP can't handle nonconvex piecewise linear cost functions
set thisgen(gen);

parameters cur_slope, next_slope;
loop(gen$(status(gen) and (costmodel(gen) eq 1) and (numcostpts(gen) > 2)),
    next_slope = (costpts_y(gen,'2') - costpts_y(gen,'1'))
                 / (costpts_x(gen,'2') - costpts_x(gen,'1'));
    loop(costptset$(ord(costptset) < numcostpts(gen) - 1),
        cur_slope = next_slope;
        if((ord(costptset) < numcostpts(gen) - 2) and (costpts_x(gen,costptset+2) eq costpts_x(gen,costptset+1)),
            abort "Zero-length piecewise segment detected";
        );
        next_slope = (costpts_y(gen,costptset+2) - costpts_y(gen,costptset+1))
                     / (costpts_x(gen,costptset+2) - costpts_x(gen,costptset+1))

        if(cur_slope - next_slope > 1e-8,
            thisgen(gen1)=no; thisgen(gen)=yes;
            display thisgen;
            abort "Nonconvex piecewise linear costs not supported";
        );
    );
);
$offtext

*===== SECTION: EQUATIONS PART 2
* Defining piecewise linear generator cost curves
* P is in per-unit, costpts_x is in MW, and costpts_y is in $/hr


$ifthen.nobids %demandbids%==1
* Revenue from elastic demand are less than a concave function
c_demandbid_revenue(demandbid,demandbid_s)$((ord(demandbid_s) lt numdemandpts(demandbid)))..
V_demandbid_rev(demandbid) =l=
    ((demandpts_y(demandbid,demandbid_s+1) - demandpts_y(demandbid,demandbid_s))/
      (demandpts_x(demandbid,demandbid_s+1) - demandpts_x(demandbid,demandbid_s)))
       * (V_Pd_elastic(demandbid)*baseMVA - demandpts_x(demandbid,demandbid_s))
   + demandpts_y(demandbid,demandbid_s)
;
$endif.nobids




c_obj..
    V_objcost =e=
           V_shuntSwitchingTotalPenalty  +
5000000*sum(gen, V_P(gen)-Pg(gen))
*penalty for contro_solar_pout
         -sum(i,sum(demanStep ,demSlope(i,demanStep)*V_dem_Load(i,demanStep))  )
         + sum(i,sqr(P_S(i))*dis_gen_par1(i)+P_S(i)*dis_gen_par2(i)+dis_gen_par3(i))
         + solar_curtail_penalty * sum(i,Solar_p_curtail(i))
*         + demand_response_increase_penalty * sum(i,De_response_Inc_P(i))
*         - demand_response_decrease_penalty * sum(i,De_response_Dec_P(i))
*the demand response q is comment out because it change with respose to p
*+5*sum(i,De_response_Inc_Q(i))-5*sum(i,De_response_Dec_Q(i))
*the term of line losses. tobe checked, tobe verified
*         + sum(i,V_Lossi(i))
*         + V_previous_solution_penalty
*the penalty for power balancing relaxation
*         + %balance_constr_penalty% * (
*               sum(i,V_p_over(i))
*             + sum(i,V_p_under(i))
*             + sum(i,V_q_over(i))
*             + sum(i,V_q_under(i)))
;

c_objtest..
    V_objcosttest =e=
           V_shuntSwitchingTotalPenalty +
 5000000*sum(gen, V_P(gen)-Pg(gen))
         -sum(i,sum(demanStep ,demSlope(i,demanStep)*V_dem_Load(i,demanStep)) )
         + sum(i,sqr(P_S(i))*dis_gen_par1(i)+P_S(i)*dis_gen_par2(i)+dis_gen_par3(i))
*penalty for contro_solar_pout
         + solar_curtail_penalty * sum(i,Solar_p_curtail(i))
*         + demand_response_increase_penalty * sum(i,De_response_Inc_P(i))
*         - demand_response_decrease_penalty * sum(i,De_response_Dec_P(i))
*the demand response q is comment out because it change with respose to p
*+5*sum(i,De_response_Inc_Q(i))-5*sum(i,De_response_Dec_Q(i))
*the term of line losses. tobe checked, tobe verified
*         + sum(i,V_Lossi(i))
* artificial variables is included in objective function with high penalty cost
*         + generator_voltage_deviation_penalty
*             * sum(bus$(sum(gen,status2(gen,bus)) eq 1),  V_artup(bus))
*         + generator_voltage_deviation_penalty
*             * sum(bus$(sum(gen,status2(gen,bus)) eq 1),  V_artlow(bus))
*         + V_previous_solution_penalty
*the penalty for power balancing relaxation
*         + %balance_constr_penalty% * (
*               sum(i,V_p_over(i))
*             + sum(i,V_p_under(i))
*             + sum(i,V_q_over(i))
*             + sum(i,V_q_under(i)))
;

c_gen_q_arctan_v(gen)$status(gen)..
    v_q(gen) =e=
    qmin(gen) +
    (qmax(gen) - qmin(gen))
    * (0.5 -
       (1 / pi) *
       arctan(
           sum(bus$atbus(gen,bus),
               sqrt(sqr(v_real(bus)) + sqr(v_imag(bus))) - vsch(bus)) /
           pv_pq_smoothing_param));
