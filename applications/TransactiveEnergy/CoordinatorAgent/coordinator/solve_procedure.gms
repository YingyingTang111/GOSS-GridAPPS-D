
*nlpfile knitroset.opt
option  nlp = KNITRO;
option  rminlp = KNITRO;
option  minlp = knitro;
option SysOut = On;
*feastol =1e-7

$onecho>Knitro.opt
honorbnds = 1
*outlev = 6
*mip_heuristic 1
*mip_heuristic_maxit 1
*mip_method = 2
mip_rounding = 4
*infeastol=  1.0e-10
*ms_enable=1
*feastol=1.0e-7
presolve=1
*algorithm=3
*bar_penaltycons = 2
*bar_feasible = 1
*bar_relaxcons = 3
$offecho

$onecho>Knitro.op2
honorbnds = 1
*outlev = 6
*mip_heuristic 1
*mip_heuristic_maxit 1
*mip_method = 2
mip_rounding = 4
*infeastol=  1.0e-10
*ms_enable=1
opttol=5e-5
opttolabs=1e-2
algorithm=3
feastol=1.0e-5
feastolabs=1.0e-6
presolve=1
$offecho

acopf.optfile=1;
acopf.optca = 0;
*acopf.optcr = 1e-8;
acopf.reslim = 60;
acopf.holdfixed = 1;
acopf_check.optfile=1;
acopf_check.optca = 0;
*acopf_check.optcr = 1e-8;
acopf_check.reslim = 60;
acopf_check.holdfixed = 1;

$ontext
* TODO JH remove this solve
* initial solve with penalty model
* we seem to have significant difficulty solving a minlp problem,
* at some time steps, even if we provide a feasible solution.
* this is a problem with the knitro solver.
*display "foo", numShuntStepsOn_init;
V_shunt.l(bus,bus_s)$numBswitched(bus,bus_s) = numShuntStepsOn_init(bus,bus_s);
solve acopf_check min V_objcosttest using rminlp;
V_shunt.fx(bus,bus_s)$numBswitched(bus,bus_s) = round(V_shunt.l(bus,bus_s));
solve acopf_check min V_objcosttest using rminlp;
*solve acopf_check min V_objcosttest using minlp;
V_shunt.lo(bus,bus_s)$numBswitched(bus,bus_s) = 0;
V_shunt.up(bus,bus_s)$numBswitched(bus,bus_s) = numBswitched(bus,bus_s);
*solve acopf_check min V_objcosttest using minlp;
* PHASE 3:
* set voltage penalty parameters to 0
* fix voltage magnitude deviations to 0 for buses already achieving 0 deviation
* fix reactive power (to what value?) for buses with nonzero deviation
*   specifically,
*     if deviation > 0 fix q to qlo
*     if deviation < 0 fix q to qup
*   what if deviation is nonzero but q is not at a bound already?
*   this procedure risks infeasibility. Instead we could do:
*     if deviation <> fix q to q.l
*   or
*     if deviation > 0 require q <= q.l
*     if deviation < 0 require q >= q.l
parameter
    sstat "final solver status"
    mstat "final model status"
    infeas "Number of infeasibilities from model solve"
    sumInf "SUM OF infeasibility";
sstat=acopf_check.solvestat;
mstat=acopf_check.modelstat;
infeas = acopf_check.numInfes;
sumInf = acopf_check.sumInfes;
$offtext

* TODO JH - feasibility problems with these solves
* need to fix this
*$ontext

*==== SECTION: Solution Analysis
* See if model is solved
parameter
    sstat "final solver status"
    mstat "final model status"
    infeas "Number of infeasibilities from model solve"
    sumInf "SUM OF infeasibility";

* for test to evaluate quality of start point
* remove these lines for a real run
*option rminlp=examiner;
*solve acopf min V_objcost using rminlp;
*$exit

*** solve the model (phase 1)
solve acopf min V_objcost using rminlp;
**$exit
**OPTION NLP=GAMSCHK;
**solve acopf min V_objcost using rminlp;
*
*
*
infeas = acopf.numInfes;
sumInf = acopf.sumInfes;
sstat=acopf.solvestat;
mstat=acopf.modelstat;
*display infeas,sumInf;

if(infeas ne 0,
*        solve phase 2
*        what is the best shunt starting point?
*        does it matter?
         display  V_shunt.l;
         V_shunt.l(bus,bus_s)$numBswitched(bus,bus_s) = numShuntStepsOn_init(bus,bus_s);
         solve acopf_check min V_objcosttest using rminlp;
*         if(acopf_check.modelstat ne 2 or acopf_check.modelstat ne 7,
*            abort "failed to solve acopf_check with relaxed shunt settings";);
$ifthen %shunt_switching_off% == 0
                 Pd_respon_location(bus) = 0;
*                 acopf_check.optfile=2;
                 display  V_shunt.l;
                 V_shunt.fx(bus,bus_s)$numBswitched(bus,bus_s) = round(V_shunt.l(bus,bus_s));
*                acopf_check.holdfixed=1;

                 solve acopf_check min V_objcosttest using rminlp;
$endif
         display  V_shunt.l;
*         if(acopf_check.modelstat ne 2 or acopf_check.modelstat ne 7,
*            abort "failed to solve scopf_check after fixing shunts";);
         infeas = acopf_check.numInfes;
         sstat=acopf_check.solvestat;
         mstat=acopf_check.modelstat;
         saturaup(i)=V_artup.l(i);
         saturalow(i)=V_artlow.l(i);
*        solve phase 3
         V_Q.fx(gen)$((sum(bus$atBus(gen,bus),saturaup(bus)) ne 0) or (sum(bus$atBus(gen,bus),saturalow(bus)) ne 0)) =V_Q.l(gen);
*        V_Q.fx(gen)$(genQtemp(gen) ne 0 )=genQtemp(gen);
*         acopf.optfile=2;
         solve acopf min V_objcost using rminlp;
*         if(acopf.modelstat ne 2,
*            abort "failed to solve acopf after fixing V at saturated buses";);
         infeas = acopf.numInfes;
         sstat=acopf.solvestat;
         mstat=acopf.modelstat;
*        solve acopf_resolve min V_objcosttest using rminlp;
);

*$batinclude "%filepath%objective_voltage_stability_addterm.gms" obj demandbids

* TODO - need to fix above solves
*$offtext

*while((infeas ne 0),
*   voltageran_low=voltageran_low-step_leng;
*   voltageran_high=voltageran_high+step_leng;
*   display voltageran_low,voltageran_high;
*   solve acopf min V_objcost using minlp;
*);
