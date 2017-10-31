
gen_participation_factor(gen)
  = 1$(sum(bus$(atBus(gen,bus) and businfo(bus,'type','given') eq 3),1) > 0);

* set shunt penalties to 0
* if this is the first time step
$ifthen not exist 'switched_shunt_current.gdx'
shuntSwitchingPenalty1 = 0;
shuntSwitchingPenalty2 = 0;
shuntSwitchingTolerance = 0;
shuntSwitchingBudgetPenalty = 0;
shuntSwitchingBudget = 0;
$endif

display Bswitched;

*--- Define load, gen buses and active lines
file fx;
put fx;

load(bus)$(type(bus) eq 1)  = 1;
isSolar(bus)$(sum(solarbus, solarlocation(solarbus,bus)) eq 1) = 1;
isGen(bus)$(not(load(bus))) = 1;
activeGen(bus)$(isGen(bus) and (sum(gen$atBus(gen,bus), status(gen))>0) ) = 1;
option isLine < branchstatus;

* disable solar
$ifthen %solar_off%==1
isSolar(bus) = 0;
solarlocation(solarbus,bus) = 0;
contro_solar_location(bus) = 0;
$endif

saturaup(bus)=0;
 saturalow(bus)=0;
genQtemp(gen)=0;
*voltageran_low=0.999;
*voltageran_high=1.001;
voltageran_low=1;
voltageran_high=1;
step_leng=0.1;

* voltage magnitude target will be loaded from a file
* for now set it as the scalar voltage goal

* load from a gdx file if desired
* this gdx file can be written in the Python simulation code
* after reading from csv
* or else we can read from csv and construct a gdx file in the Gams code
* for now we assume the gdx file is constructed externally to the Gams code
volt_mag_target(bus) = load_bus_voltage_goal;

* which buses should be subject to a voltage magnitude target deviation penalty?
* for any given bus, if the real power load has a nonzero value,
* then we should penalize the deviation from the voltage magnitude target
bus_penalize_volt_mag_target(bus) = yes$(abs(pd(bus)) > 0 and abs(volt_mag_target(bus)) > 0);
