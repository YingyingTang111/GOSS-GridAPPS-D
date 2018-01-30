$ontext
Randomized initial conditions for rectangular ACOPF
$offtext

$if not set filepath $setnames "%gams.i%" filepath filename fileextension

V_P.l(gen)$status(gen) = uniform(Pmin(gen),Pmax(gen));
V_Q.l(gen)$status(gen) = uniform(Qmin(gen),Qmax(gen));

* There should be a better way of choosing bounds for these
Vm(bus) = uniform(minVm(bus),maxVm(bus));
Va(bus) = uniform(-pi,pi);
V_real.l(bus) = Vm(bus)*cos(Va(bus));
V_imag.l(bus) = Vm(bus)*sin(Va(bus));

$if %condensed% == 'no' $include '%filepath%ic_iv%sep%calc_derived_vars.gms'
