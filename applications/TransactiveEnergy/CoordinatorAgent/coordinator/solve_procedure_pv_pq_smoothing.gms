
option  nlp = KNITRO;
option  rminlp = knitro;
option  minlp = knitro;
option SysOut = On;

$onecho>Knitro.op3
* for barrier/cg - better for memory but not as robust?
*algorithm = 2
*honorbnds = 1
*outlev = 6
*mip_heuristic 1
*mip_heuristic_maxit 1
*mip_method = 2
mip_rounding = 4
*infeastol=  1.0e-10
*ms_enable=1
*feastol=1.0e-7
presolve=1
*bar_penaltycons = 2
*bar_feasible = 1
*bar_relaxcons = 3
$offecho

acopf_arctan.optfile=3;
acopf_arctan.reslim = 60;
*acopf_arctan.holdfixed = 1;

solve acopf_arctan min V_objcost using rminlp;
V_shunt.fx(bus,bus_s)$numBswitched(bus,bus_s) = round(V_shunt.l(bus,bus_s));
solve acopf_arctan min V_objcost using rminlp;
*solve acopf_arctan min V_objcost using minlp;
V_shunt.lo(bus,bus_s)$numBswitched(bus,bus_s) = 0;
V_shunt.up(bus,bus_s)$numBswitched(bus,bus_s) = numBswitched(bus,bus_s);
parameter
    sstat "final solver status"
    mstat "final model status"
    infeas "Number of infeasibilities from model solve"
    sumInf "SUM OF infeasibility";
sstat=acopf_arctan.solvestat;
mstat=acopf_arctan.modelstat;
infeas = acopf_arctan.numInfes;
sumInf = acopf_arctan.sumInfes;

*         if(acopf_check.modelstat ne 2 or acopf_check.modelstat ne 7,
*            abort "failed to solve acopf_check with relaxed shunt settings";);
*         if(acopf_check.modelstat ne 2 or acopf_check.modelstat ne 7,
*            abort "failed to solve scopf_check after fixing shunts";);
*         if(acopf.modelstat ne 2,
*            abort "failed to solve acopf after fixing V at saturated buses";);
