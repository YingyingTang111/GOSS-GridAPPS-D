*Created by xinda ke in 7/20/2016
* this code is to extract data from gdx
*updated by xinda ke in 7/24/2016

*==== SECTION: Data (pre) declaration
$onUNDF
sets
* New sets
    conj /real,imag/
    costcoefset "Placeholder set for quadratic function coefficients (0,1,2)" /0*2/
    costptset "Placeholder set for pwl function pieces"  /1*40/

* Timeperiod
    t /%timeperiod%/,
* Dataset sets
    bus, gen, circuit, nongen, solarbus,
    interface, interfacemap (interface,bus,bus),
    demandbid, demandbidmap,
    fuel_t, fuel_s, prime_mover,
    bus_t, bus_s,
    gen_t, gen_s,
    branch_t, branch_s,

    interface_t,
    line(bus,bus,circuit),
    transformer(bus,bus,circuit),
    monitored_lines(bus,bus,circuit)
;
set demanStep  "demandresponse-steps"  /1 * 5/;
set demanRang  "demandresponse-steps"  /1 * 4/;
alias(bus,i,j);
alias(circuit,c);
alias(gen,gen1);
alias(bus_s,bus_s_0,bus_s_1,bus_s_2);
parameters
    version, baseMVA, total_cost,Nb,
* Domain info not stated because of how we iterate through data
     businfo(*,*,*),
     geninfo(*,*,*),
     fuelinfo(*,*),
     branchinfo(*,*,*,*,*),
     interfaceinfo(*,*,*)
;
*-- Specially handled data (option specific)
$onempty
sets
  demandbid_t(*) / /
  demandbid_s(*) / /
  demandbid(*) / /
  demandbidmap (*,*) / /
;

parameters
  demandbidinfo(*,*,*,*) / /
;
$offempty
*==== SECTION: Data read-in from input file
$GDXIN %case%
$LOAD version, baseMVA, total_cost
$LOAD bus,gen, circuit,bus_s, line,transformer
$LOAD bus_t, gen_t, branch_t, branch_s
*$LOAD fuel_t, fuel_s, prime_mover
$LOAD businfo, geninfo, branchinfo, fuelinfo
$LOAD interface, interfacemap, interfaceinfo
*$load bus_s, gen_s,
*susceptance of switched shunt
$GDXIN


set pq  "real and reactive"  /1 * 2/;
*$call 'GDXXRW input=solarbus.xlsx output=solarbus.gdx set=solarbus rng=Sheet1!A1:CX1 Cdim=1';


$GDXIN solarbus2.gdx
$LOAD solarbus
$GDXIN

* Option to use elastic demand bidding turned on
$if %demandbids% == 1 $LOADR demandbid_t, demandbid_s, demandbid, demandbidmap, demandbidinfo
$GDXIN
*==== SECTION: Validity of options
* linelimits, case insensitive




* allon, case insensitive
* this will allow u to turn on certain bus or circuit selectively
$iftheni %allon% == "gens"
$elseifi %allon% == "lines"
$elseifi %allon% == "both"
$elseif %allon% == 0
$else $if set allon $abort "Fix invalid option: --allon=%allon%"
$endif

*==== SECTION: Data Declaration (extracted/manipulated from datafile)
*-- All OPF models
parameters
  type(bus)         "bus type (probably irrelevant, but gives reference bus[es])"
  pf(bus)           "bus demand power factor"
  Pd(bus)           "bus real power demand"
  Pd_respon_p_up(bus)   "the upper cap of real power of demand response"
  Pd_respon_p_down(bus)   "the downer cap of real power of demand response"
  Pd_respon_q_up(bus)   "the upper cap of reactive power of demand response"
  Pd_respon_q_down(bus)   "the downer cap of reactive power of demand response"
  Pd_respon_location(bus) "the location of demandresponse bus, equals 1 if that bus has this solar"
  gentype(gen)      "generator if equals 1 or slack bus equals 0"
  Pg(gen)           "gen real power output"
  PgSch(gen)        "gen scheduled power output"
  Pmax(gen)         "gen maximum real power output"
  Pmin(gen)         "gen minimum real power output"
  Va(bus)           "bus voltage angle"
  Vm(bus)           "bus voltage magnitude"
  MaxVm(bus)        "maximum bus voltage magnitude"
  MinVm(bus)        "minimum bus voltage magnitude"
  Gs(bus)           "bus shunt conductance"
  solar_r(bus)  "solar real power"
  dis_gen_par1(bus)      "distributed generator parameter 1"
  dis_gen_par2(bus)      "distributed generator parameter 1"
  dis_gen_par3(bus)      "distributed generator parameter 1"
  atBus(gen,bus)    "Location of generator"
  status(gen)       "generator status"
  status2(gen,bus)   "Online generator status marked for all bus"
  Vsch(bus)          "generator voltage schedule"
  r(i,j,c)          "line resistance"
  x(i,j,c)          "line reactance"
  B(i,j,c)          "line susceptance"
  ratio(i,j,c)      "transformer tap ratio",
  angle(i,j,c)      "transformer tap angle",
  rateA(i,j,c)      "line power limits (MW)",
  currentrate(i,j,c)  "line current limits",
  branchstatus(i,j,c) "line status",
  interfaceLimit(interface) "Limit on power across each interface"
  solarlocation(solarbus,bus)  "the location of solar bus"
  contro_solar_location(bus) "the location of controllable solar bus, equals 1 if that bus has this solar"
  csolar_Q_limit_up(bus) "the location of controllable solar bus, equals 1 if that bus has this solar"
  csolar_Q_limit_down(bus) "the location of controllable solar bus, equals 1 if that bus has this solar"
  contro_solar_pout(bus)   "the real power output of curtailable solar bus"
  Qd(bus)           "bus reactive power demand"
  Qg(gen)           "gen reactive power output"
  Qmax(gen)         "gen maximum reactive power output"
  Qmin(gen)         "gen minimum reactive power output"
  Bs(bus)           "bus shunt susceptance"
  yb(i,j,conj)      "Bus admittance matrix, Ybus"
  g(i,j,c)          "line conductance"
  bc(i,j,c)         "line charging susceptance"
  Bswitched(bus,bus_s)     "susceptance of switched shunts",
  numBswitched(bus,bus_s)  "number of each type of switched shunt elements at each bus"
*  switchedShuntB_init(bus,bus_s) "initial value of switched shunt susceptance"
  switchedShuntB_init(bus) "initial value of switched shunt susceptance"
  numShuntStepsOn_init(bus,bus_s) "initial number of switched shunt steps on"
  demLoad(demanStep) "demandresponse load"
  demPrice(demanStep) "demandresponse price"
  demSlope(demanStep) "slope"
  demLocation(bus)      "location of demand response"
;




*r(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'r','given');
*x(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'x','given');
*branchstatus(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'branchstatus','%timeperiod%');

$GDXIN geni_st.gdx
$LOAD status
$GDXIN

$GDXIN demand_response.gdx
$LOAD Pd_respon_location, Pd_respon_p_down, Pd_respon_q_down, Pd_respon_p_up, Pd_respon_q_up
$GDXIN

$GDXIN demandresponseload.gdx
$LOAD demLoad
$GDXIN
display demLoad;
$GDXIN demandresponseprice.gdx
$LOAD demPrice
$GDXIN
demLocation('18')=1;

demLoad(demanStep)=demLoad(demanStep)/baseMVA;
demSlope(demanStep)$(ord(demanStep) > 1 )=( (demPrice(demanStep)-demPrice(demanStep-1) ) /(demLoad(demanStep)-demLoad(demanStep-1)))$(demLoad(demanStep) ne demLoad(demanStep-1));

display demLoad,demPrice,demLocation,demSlope;
dis_gen_par1('13')=250*sqr(baseMVA);
dis_gen_par1('57')=310*sqr(baseMVA);
dis_gen_par2('13')=15.6*baseMVA;
dis_gen_par2('57')=29.7*baseMVA;
dis_gen_par3('13')=0.33;
dis_gen_par3('57')=0.3;

$ifthen %demand_response_off%==1
Pd_respon_p_down(bus)=0;
Pd_respon_q_down(bus)=0;
Pd_respon_p_up(bus)=0;
Pd_respon_q_up(bus)=0;
$else
Pd_respon_p_down(bus)= Pd_respon_p_down(bus)/baseMVA;
Pd_respon_q_down(bus)$Pd_respon_q_down(bus)= Pd_respon_q_down(bus)/Pd_respon_p_down(bus)/baseMVA;
*Pd_respon_q_down(bus)= Pd_respon_q_down(bus)/baseMVA;
Pd_respon_p_up(bus)= Pd_respon_p_up(bus)/baseMVA;
*Pd_respon_q_up(bus)=Pd_respon_q_up(bus)/baseMVA;
Pd_respon_q_up(bus)$Pd_respon_q_up(bus)= Pd_respon_q_up(bus)/Pd_respon_p_up(bus)/baseMVA;
$endif



$ifthen %solar_curtailment_off%==1
contro_solar_pout(bus)=0;
contro_solar_location(bus)=0;
$else
$GDXIN solar_control.gdx
$LOAD contro_solar_pout, contro_solar_location
$GDXIN
* to per unit
contro_solar_pout(bus)=contro_solar_pout(bus)/baseMVA;

$endif

$ifthen %solar_q_boun_adjust_off%==1
csolar_Q_limit_up(bus)=0;
csolar_Q_limit_down(bus)=0;
contro_solar_location(bus)=0;
$elseif %solar_curtailment_off%==1  and  %solar_q_boun_adjust_off%==0
$GDXIN solar_controlQlimit.gdx
$LOAD csolar_Q_limit_up, csolar_Q_limit_down, contro_solar_location
$GDXIN
$else

$GDXIN solar_controlQlimit.gdx
$LOAD csolar_Q_limit_up, csolar_Q_limit_down
$GDXIN
$endif
*to per unit
csolar_Q_limit_up(bus) =csolar_Q_limit_up(bus)/baseMVA;
csolar_Q_limit_down(bus) =csolar_Q_limit_down(bus)/baseMVA;

* trying to replace the input file in the gdx above using wisconsin gdx
*solar section
*$call 'GDXXRW input=solar_s.xlsx output=solar_s.gdx par=solar_s rng=Sheet1!B1:CX2 Cdim=1';
*$call 'GDXXRW input=solarindex.xlsx output=solarlocation.gdx par=solarlocation rng=Sheet1!B1:CX3 Cdim=2 ';
$GDXIN solarlocation.gdx
$LOAD solarlocation
$GDXIN
* Bus type
type(bus) = businfo(bus,'type','given');
atBus(gen,bus)$geninfo(gen,'atBus',bus) = 1;
Pmax(gen) = geninfo(gen,'Pmax','given')/baseMVA;
Pmin(gen) = geninfo(gen,'Pmin','given')/baseMVA;
Qmax(gen) = geninfo(gen,'Qmax','given')/baseMVA;
Qmin(gen) = geninfo(gen,'Qmin','given')/baseMVA;


*gentype  generator if equals 1 or slack bus equals 0
gentype(gen)=1$(sum(bus$(atBus(gen,bus)), type(bus) eq 2));
Vsch(bus)$(sum(gen,atBus(gen,bus)) > 0)=sum(gen$(atBus(gen,bus)), geninfo(gen,'Vg','given'))/ sum(gen, atBus(gen,bus));
* Line resistance (r) and reactance (x)
r(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'r','given');
x(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'x','given');
r(j,i,c)$r(i,j,c) = r(i,j,c);
x(j,i,c)$x(i,j,c) = x(i,j,c);
* line charging conductance
bc(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'bc','given');
bc(j,i,c)$(bc(i,j,c)) = bc(i,j,c);
* transformer tap ratios and angles
ratio(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'ratio','given');
ratio(j,i,c)$(ratio(i,j,c)) =  1/ratio(i,j,c);
* TODO is this right?
* should we have 1/ratio and -angle? or
* ratio and angle?
* original was ratio and -angle, which makes no sense
*CHECK the angle is all zero in 118 system, should be checked in other system
angle(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'angle','given') * pi/180;
* TODO is this right?
angle(j,i,c)$(angle(i,j,c)) = -angle(i,j,c);
*TODO the time step for branchstatus
*time step has checked with Sidhart
branchstatus(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'branchstatus','1');
* Bus shunt conductance and susceptance
* in the 118 system fixed shunt elements all got replaced by switched shunt elements
Gs(bus) = businfo(bus,'Gs','given')/baseMVA;
Bs(bus) = businfo(bus,'Bs','given')/baseMVA;

* add the input replacement above

status2(gen,bus) = 1$(atBus(gen,bus) and status(gen) eq 1 );
$GDXIN UC_OPF_load_elwi_BV.gdx
$LOAD Pd
$GDXIN

Pd(bus) =Pd(bus)/baseMVA;


* Voltage angle
Va(bus) = businfo(bus,'Va','1')*pi/180;
*Va(bus) = 0;
*Voltage magnitude information
Vm(bus) = businfo(bus,'Vm','1');
*Vm(bus) = 1;
maxVm(bus) = businfo(bus,'maxVm','given');
minVm(bus) = businfo(bus,'minVm','given');

* Initial branch status (active/not connected)

* Define original cost model in dataset
* If linelimits=inf, no monitored lines
$if %linelimits% == 'inf' monitored_lines(i,j,c) = no;

* Limit on power across each interface
*interfaceLimit(interface) = interfaceinfo(interface,'%timeperiod%','rateA')/baseMVA;

* Line current
*currentrate(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'currentrateA','%linelimits%');
*currentrate(j,i,c)$(line(i,j,c)) = branchinfo(i,j,c,'currentrateA','%linelimits%');

* Take down all lines to buses marked as "isolated"
branchstatus(i,j,c)$(type(i) eq 4 or type(j) eq 4) = 0;

* Line susceptance
B(i,j,c)$line(i,j,c) = -x(i,j,c)/(sqr(r(i,j,c))+sqr(x(i,j,c)));
B(j,i,c)$(b(i,j,c)) = b(i,j,c);



$GDXIN geni_p.gdx
$LOAD PgSch
$GDXIN
PgSch(gen) =PgSch(gen)/baseMVA;
*starting searching point of generator real power output, might need obtained from input data
Pg(gen)=PgSch(gen);
*generator scheduled volage output


* Line limit (active power)
*line limit is disabled to match Matpower
*rateA(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'rateA','%linelimits%')/baseMVA;
*rateA(j,i,c)$(line(i,j,c)) = branchinfo(i,j,c,'rateA','%linelimits%')/baseMVA;



$GDXIN UC_OPF_load_elwi_Q.gdx
$LOAD Qd
$GDXIN
Qd(bus) =Qd(bus)/baseMVA;




*$GDXIN geni_q.gdx
*$LOAD Qg
*$GDXIN
*Qg(gen) =Qg(gen)/baseMVA;
*Qg is zero from gdx.
Qg(gen)=geninfo(gen,'Qg','1')/baseMVA;

* Bus shunt conductance and susceptance


* line conductance
g(i,j,c)$line(i,j,c) =  r(i,j,c)/(sqr(r(i,j,c))+sqr(x(i,j,c)));
g(j,i,c)$(g(i,j,c)) = g(i,j,c);




* line charging conductance
*bc(i,j,c)$line(i,j,c) = branchinfo(i,j,c,'bc','given');


* number and susceptance of switched shunt element data
* number of steps in each switched shunt
numBswitched(bus,bus_s) =
  businfo(bus,'switchedelements',bus_s)
*  $(
*    businfo(bus,'SwSh_Stat','given') = 1 and
*    businfo(bus,'MODSW','given') = 1 and
*    businfo(bus,'SwSh_RMPCT','given') = 100)
    ;
* step size in each switched shunt
Bswitched(bus,bus_s)$numBswitched(bus,bus_s) =
  businfo(bus,'switchedBs',bus_s)/baseMVA;
* switched shunt susceptance in a prior solution
switchedShuntB_init(bus)$(sum(bus_s,numBswitched(bus,bus_s))) =
  businfo(bus,'SwSh_Stat','given')* businfo(bus,'BINIT','given')/baseMVA;
*switchedShuntB_init('307723')=0;
* not sure if there is any better way to set this
* but we only need it for the first time step
numShuntStepsOn_init(bus,bus_s)$numBswitched(bus,bus_s)
  = switchedshuntB_init(bus) * numBswitched(bus,bus_s)
  / sum(bus_s_1, numBswitched(bus,bus_s_1) * Bswitched(bus,bus_s_1));

* ==== SECTION: Additional Model Options
*-- Elastic demand bidding turned on/off
$ifthen %demandbids% ==1
parameters
  demandpts_x       "price responsive demand cost breakpoints (piecewise linear)"
  demandpts_y       "price responsive demand cost breakpoints (piecewise linear)"
  numdemandpts      "number of price responsive demand points"
;

  numdemandpts(demandbid) = demandbidinfo(demandbid,'%timeperiod%','numbids','given');
  demandpts_x(demandbid,demandbid_s) = demandbidinfo(demandbid,'%timeperiod%','Quantity',demandbid_s);
  demandpts_y(demandbid,demandbid_s) = demandbidinfo(demandbid,'%timeperiod%','Price',demandbid_s);
$endif

*-- %allon% options
$ifthen %allon% == "gens"
  status(gen) = 1;
$elseif %allon% == "lines"
  branchstatus(i,j,c)$line(i,j,c) = 1;
$elseif %allon% == "both"
  status(gen) = 1;
  branchstatus(i,j,c)$line(i,j,c) = 1;
$endif
*branchstatus(j,i,c)$(branchstatus(i,j,c)) =  branchstatus(i,j,c);
* filepath is not coming in from batinclude from iv_acopf correctly
* use setnames to get it
* temp_solution.gdx not found. is that OK?
$setnames "%gams.i%" filepath
