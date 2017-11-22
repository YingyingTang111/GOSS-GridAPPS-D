$title switched_shunt_data_from_csv
$ontext
pulls in switched shunt data from a CSV file
$offtext

$if not set incsv $set incsv case_118_switched_shunt.csv
$if not set ingdx $set ingdx in.gdx
$if not set outgdx $set outgdx switched_shunt_data.gdx
$if not set currentgdx $set currentgdx switched_shunt_current.gdx
$if not set maxShuntSettings $set maxShuntSettings 100

$if not set initCurrentSettings $set initCurrentSettings 1
$if not set getCurrentSettings $set getCurrentSettings 0

*$if not set switchPenalty $set switchPenalty 1e3

sets
  switchedShuntIndex
  switchedShuntName
  switchedShuntID
  switchedShuntBusNo
  switchedShuntHeaderEntries;

alias(switchedShuntIndex,ssIn);
alias(switchedShuntName,ssNa);
alias(switchedShuntID,ssId);
alias(switchedShuntBusNo,ssBn);
alias(switchedShuntHeaderEntries,ssHe);

parameters
*  switchedShuntInfo(ssIn,ssNa,ssId,ssBn,ssHe);
  switchedShuntInfo(*,*,*,*,*);

$onecho > gdxxrwparam.txt
i='%incsv%'
o='%ingdx%'
dset=switchedShuntIndex rdim=1 cdim=0 rng=a2
dset=switchedShuntName rdim=1 cdim=0 rng=b2
dset=switchedShuntId rdim=1 cdim=0 rng=c2
dset=switchedShuntBusNo rdim=1 cdim=0 rng=d2
dset=switchedShuntHeaderEntries rdim=0 cdim=1 rng=e1
par=switchedShuntInfo rdim=4 cdim=1 rng=a1
$offecho
$call gdxxrw @gdxxrwparam.txt
$gdxin '%ingdx%'
$loaddc switchedShuntIndex
$loaddc switchedShuntName
$loaddc switchedShuntID
$loaddc switchedShuntBusNo
$loaddc switchedShuntHeaderEntries
$loaddc switchedShuntInfo
$gdxin

display
  switchedShuntIndex
  switchedShuntName
  switchedShuntID
  switchedShuntBusNo
  switchedShuntHeaderEntries
  switchedShuntInfo;

sets
  shuntSettings /s1*s%maxShuntSettings%/
  ssBn_ssIn_map(ssBn,ssIn)

alias(shuntSettings,s,s1);

sets
  sUsed(s)
  ssIn_s_Active(ssIn,s)
  ssIn_s_Current(ssIn,s);

parameters
  ssIn_Status(ssIn)
  ssIn_QC(ssIn)
  ssIn_QC_min(ssIn)
  ssIn_QC_max(ssIn)
  ssIn_NumSteps(ssIn)
  ssIn_EachStep(ssIn)
  ssIn_Conductance(ssIn)
  ssIn_s_Susceptance(ssIn,s);
*  shuntSwitchingPenalty;

ssIn_Status(ssIn) = sum((ssNa,ssId,ssBn),switchedShuntInfo(ssIn,ssNa,ssId,ssBn,'Status'));
ssIn_QC(ssIn) = sum((ssNa,ssId,ssBn),switchedShuntInfo(ssIn,ssNa,ssId,ssBn,'QC'));
ssIn_QC_min(ssIn) = sum((ssNa,ssId,ssBn),switchedShuntInfo(ssIn,ssNa,ssId,ssBn,'QC_min'));
ssIn_QC_max(ssIn) = sum((ssNa,ssId,ssBn),switchedShuntInfo(ssIn,ssNa,ssId,ssBn,'QC_max'));
ssIn_NumSteps(ssIn) = sum((ssNa,ssId,ssBn),switchedShuntInfo(ssIn,ssNa,ssId,ssBn,'# of steps'));
ssIn_EachStep(ssIn) = sum((ssNa,ssId,ssBn),switchedShuntInfo(ssIn,ssNa,ssId,ssBn,'each step'));

ssBn_ssIn_map(ssBn,ssIn) = sum((ssNa,ssId)$(switchedShuntInfo(ssIn,ssNa,ssId,ssBn,'Status') gt 0),1);
ssIn_s_Active(ssIn,s) = (ord(s) le ssIn_NumSteps(ssIn) + 1);
sUsed(s) = sum(ssIn$ssIn_s_Active(ssIn,s),1);
ssIn_Conductance(ssIn) = 0;
ssIn_s_Susceptance(ssIn,s)$(ssIn_s_Active(ssIn,s) and ssIn_EachStep(ssIn) gt 0) = ssIn_QC_min(ssIn) + (ord(s) - 1) * ssIn_EachStep(ssIn);
ssIn_s_Susceptance(ssIn,s)$(ssIn_s_Active(ssIn,s) and ssIn_EachStep(ssIn) lt 0) = ssIn_QC_max(ssIn) + (ord(s) - 1) * ssIn_EachStep(ssIn);
*shuntSwitchingPenalty = %switchPenalty%;

display
  ssBn_ssIn_map
  ssIn_s_Active;
*  shuntSwitchingPenalty;

execute_unload '%outgdx%',
  ssIn=switchedShunts
  sUsed=shuntSettings
  ssBn_ssIn_map=ihMap
  ssIn_s_Active=hsActive
  ssIn_Conductance=hConductance
  ssIn_s_Susceptance=hsSusceptance
*  shuntSwitchingPenalty;
;

$ifthen %initCurrentSettings%==1

* set initial current switch setting as the first setting
*ssIn_s_Current(ssIn,s)$ssIn_s_Active(ssIn,s) = (ord(s) = 1);

* set initial current switch setting as the last setting
*ssIn_s_Current(ssIn,s)$ssIn_s_Active(ssIn,s) = (ord(s) = ssIn_NumSteps(ssIn) + 1);

* set initial current switch setting as the middle setting
*ssIn_s_Current(ssIn,s)$ssIn_s_Active(ssIn,s) = (ord(s) = ceil(0.5*(ssIn_NumSteps(ssIn) + 1)));

* set initial current switch setting from ssIn_QC
*ssIn_s_Current(ssIn,s)$ssIn_s_Active(ssIn,s) = (
*  abs(ssIn_s_Susceptance(ssIn,s) - ssIn_QC(ssIn)) =
*  smin(s1$ssIn_s_active(ssIn,s1),abs(ssIn_s_Susceptance(ssIn,s1) - ssIn_QC(ssIn)))
*);
*ssIn_s_Current(ssIn,s)$ssIn_s_Current(ssIn,s-1) = no;

* set initial current switch setting to minimum susceptance
ssIn_s_Current(ssIn,s)$ssIn_s_Active(ssIn,s) = (
  ssIn_s_Susceptance(ssIn,s) =
  smin(s1$ssIn_s_active(ssIn,s1),ssIn_s_Susceptance(ssIn,s1))
);
ssIn_s_Current(ssIn,s)$ssIn_s_Current(ssIn,s-1) = no;

* set initial current switch setting to maximum susceptance
*ssIn_s_Current(ssIn,s)$ssIn_s_Active(ssIn,s) = (
*  ssIn_s_Susceptance(ssIn,s) =
*  smax(s1$ssIn_s_active(ssIn,s1),ssIn_s_Susceptance(ssIn,s1))
*);
*ssIn_s_Current(ssIn,s)$ssIn_s_Current(ssIn,s-1) = no;

display
  ssIn_s_Current;
execute_unload '%currentgdx%',
  ssIn_s_Current=hsCurrent;

$endif
