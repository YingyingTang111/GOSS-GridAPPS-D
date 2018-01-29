
* Declaration needs to be made outside loop
set
    lines_at_limit(i,j,c) "lines at their bound"
;
parameters
    total_cost "Cost of objective function"
    LMP(bus) "Locational marginal price"
    LineSP(i,j,c) "Marginal price of active power on line (i,j,c)"
    shuntB(i)
    TotalLoss         " Total Loss of all the lines"
    TotalSwitches "number of shunt switches used"
    RMSVoltageDeviation "root mean square of load bus voltage deviations"
    AverageLoadBusVoltageDeviation "average of load bus voltage deviations"
    VoltageDevNongen(bus) "voltage deviation in percentage"
    vmgen(gen) "generator voltage magnitude"
    vmgenBus(bus) "generator voltage magnitude at bus, consider multiple gen at same bus"
    vmnongen(bus) "nongenerator voltage magnitude"
    Totalvgendev "total gen voltage deviation from schedule"
    Totalvnongendev "total nongen voltage deviation from schedule"
    genbusid(gen)
    solarQupperlimit(bus)
    solarQlowerlimit(bus)
;

    TotalLoss=sum(i,V_Lossi.l(i));
*     TotalLoss=0;
    TotalSwitches = sum((i,bus_s)$numBswitched(i,bus_s),abs(V_shunt.l(i,bus_s) - numShuntStepsOn_init(i,bus_s)));
*    RMSVoltageDeviation=sqrt(sum(bus$load(bus), sqr(load_bus_voltage_goal - sqrt(sqr(V_real.l(bus)) + sqr(V_imag.l(bus))))) / max(sum(bus$load(bus),1),1));
    AverageLoadBusVoltageDeviation = sum(bus$load(bus), abs(load_bus_voltage_goal - sqrt(sqr(V_real.l(bus)) + sqr(V_imag.l(bus))))) / max(sum(bus$load(bus),1),1);
    VoltageDevNongen(bus)$(bus_penalize_volt_mag_target(bus) and type(bus) eq 1)=  load_bus_voltage_goal - sqrt(sqr(V_real.l(bus)) + sqr(V_imag.l(bus)));
*calculate the total voltage deviation of generator bus and nongenerator bus
    Totalvnongendev= sum(bus$load(bus), abs(load_bus_voltage_goal - sqrt(sqr(V_real.l(bus)) + sqr(V_imag.l(bus)))));
    Totalvgendev= sum(bus$isGen(bus), abs(Vsch(bus) - sqrt(sqr(V_real.l(bus)) + sqr(V_imag.l(bus)))));




*    Totalvgendev


display  TotalLoss, infeas;

** switched shunt solution values
parameter
  numShuntStepsOn_final(bus,bus_s)
  switched_shunt_susceptance_final(bus,bus_s);
set
  switched_shunt_susceptance_keys(bus,bus_s);
switched_shunt_susceptance_keys(bus,bus_s) = yes$numBswitched(bus,bus_s);
numShuntStepsOn_final(i,bus_s)$numBswitched(i,bus_s) = V_shunt.l(i,bus_s);
switched_shunt_susceptance_final(bus,bus_s)$numBswitched(bus,bus_s) = V_shunt.l(bus,bus_s) * Bswitched(bus,bus_s);
execute_unload 'switched_shunt_current.gdx', numShuntStepsOn_final=numShuntStepsOn;
*display switched_shunt_susceptance_keys;
if(infeas eq 0,
* Final Objective function value
    total_cost = V_objcost.l;
* Generator real power solution
    Pg(gen) = V_P.l(gen);
* Generator reactive power solution
    Qg(gen) = V_Q.l(gen);
* Voltage magnitude solution
    Vm(bus) = sqrt(sqr(V_real.l(bus)) + sqr(V_imag.l(bus)));
    vmgen(gen) =sum(bus$(atBus(gen,bus)), Vm(bus));
    vmgenBus(bus)$(sum(gen,atBus(gen,bus)) > 0)= Vm(bus);
    vmnongen(bus)=Vm(bus)$(load(bus))
    display Vm;
* Voltage angle solution
*    Va(bus) = arctan2(V_imag.l(bus),V_real.l(bus)) * 180 / pi;
    loop(bus,
    if(V_real.l(bus) > 0,
        Va(bus) = arctan(V_imag.l(bus)/V_real.l(bus)) * 180/pi;
    else
        Va(bus) = arctan(V_imag.l(bus)/V_real.l(bus)) * 180/pi + 180;
    );
    );
* Bus shunt solution
    shuntB(i) = sum(bus_s$numBswitched(i,bus_s), V_shunt.l(i,bus_s)*Bswitched(i,bus_s));
* Locational marginal price of bus at time t
*    LMP(bus) = c_BalanceP_nosolar.m(bus);

* Marginal for active power on a line
*    LineSP(i,j,c)$branchstatus(i,j,c) = c_I_Limit.m(i,j,c);
*    LineSP(j,i,c)$branchstatus(i,j,c) = c_I_Limit.m(j,i,c);

* Find which lines are at their limits
*lines_at_limit(i,j,c)$(branchstatus(i,j,c) or branchstatus(j,i,c)) = yes$
*     (sqr(currentrate(i,j,c)) - sqr(V_LineIr.L(i,j,c)) - sqr(V_LineIq.L(i,j,c)) le 1e-4);
*display lines_at_limit;
