$ontext
Use given initial conditions for Polar ACOPF.
$offtext

$if not set filepath $setnames "%gams.i%" filepath filename fileextension

V_P.l(gen) = Pg(gen)$status(gen);
V_Q.l(gen) = Qg(gen)$status(gen);
V_real.l(bus) = Vm(bus)*cos(Va(bus));
V_imag.l(bus) = Vm(bus)*sin(Va(bus));
V_switchedshuntB.l(i)$sum(bus_s$numBswitched(i,bus_s), 1) = switchedshuntB_init(i);
V_shunt.l(bus,bus_s)$numBswitched(bus,bus_s)
  = switchedshuntB_init(bus) * numBswitched(bus,bus_s)
  / sum(bus_s_1, numBswitched(bus,bus_s_1) * Bswitched(bus,bus_s_1));

*Parameter Bs_solved(bus);
*Bs_solved(bus) = businfo(bus,'switchedBsSolved','%timeperiod%')/baseMVA;
*loop((bus,bus_s)$((not sameas(bus_s,'given') and (Bswitched(bus,bus_s) ne 0)) and (abs(Bs_solved(bus)) > 1e-6)),
*    V_shunt.l(bus,bus_s) = min(Bs_solved(bus)/Bswitched(bus,bus_s), V_shunt.up(bus,bus_s));
*    Bs_solved(bus) = Bs_solved(bus) - V_shunt.l(bus,bus_s)*Bswitched(bus,bus_s);
*);

$if %condensed% == 'no' $include '%filepath%ic_iv%sep%calc_derived_vars.gms'

