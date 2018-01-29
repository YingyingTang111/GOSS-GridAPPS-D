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
           V_shuntSwitchingTotalPenalty
         + V_load_bus_volt_pen
*penalty for contro_solar_pout
         + solar_curtail_penalty * sum(i,Solar_p_curtail(i))
         + demand_response_increase_penalty * sum(i,De_response_Inc_P(i))
         - demand_response_decrease_penalty * sum(i,De_response_Dec_P(i))
*the demand response q is comment out because it change with respose to p
*+5*sum(i,De_response_Inc_Q(i))-5*sum(i,De_response_Dec_Q(i))
*the term of line losses. tobe checked, tobe verified
         + sum(i,V_Lossi(i))
	 + V_previous_solution_penalty
;

c_objtest..
    V_objcosttest =e=
           V_shuntSwitchingTotalPenalty
         + V_load_bus_volt_pen
*penalty for contro_solar_pout
         + solar_curtail_penalty * sum(i,Solar_p_curtail(i))
         + demand_response_increase_penalty * sum(i,De_response_Inc_P(i))
         - demand_response_decrease_penalty * sum(i,De_response_Dec_P(i))
*the demand response q is comment out because it change with respose to p
*+5*sum(i,De_response_Inc_Q(i))-5*sum(i,De_response_Dec_Q(i))
*the term of line losses. tobe checked, tobe verified
         + sum(i,V_Lossi(i))
* artificial variables is included in objective function with high penalty cost
         + generator_voltage_deviation_penalty
             * sum(bus$(sum(gen,status2(gen,bus)) eq 1),  V_artup(bus))
         + generator_voltage_deviation_penalty
             * sum(bus$(sum(gen,status2(gen,bus)) eq 1),  V_artlow(bus))
	 + V_previous_solution_penalty
;
