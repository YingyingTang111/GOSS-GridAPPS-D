$ontext
Default initial conditions for polar ACOPF:
Just pick midpoint of variable ranges.
$offtext

$if not set filepath $setnames "%gams.i%" filepath filename fileextension

V_P.l(gen)$status(gen) = (Pmin(gen)+Pmax(gen))/2;
V_Q.l(gen)$status(gen) = (Qmin(gen)+Qmax(gen))/2;
V_real.l(bus)  = (minVm(bus)+maxVm(bus))/2;
* V_imag can stay 0, since angles are allowed to range in (-pi, pi)
V_imag.l(bus) = 0;

$if %condensed% == 'no' $include '%filepath%ic_iv%sep%calc_derived_vars.gms'
