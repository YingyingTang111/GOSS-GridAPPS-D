$title switched_shunt_data_from_gdx

* gdx file containing switched shunt data that does not change
* from one time step to the next
$if not set ingdx $set ingdx switched_shunt_data.gdx

* gdx file containing switched shunt settings prior to the current optimization run
* i.e. from the previous time step or from initialization
$if not set currentgdx $set currentgdx switched_shunt_current.gdx

sets
  switchedShunts
  shuntSettings;
alias(switchedShunts,h,h0,h1,h2);
alias(shuntSettings,s,s0,s1,s2);
sets
  ihMap(i,h) switched shunt h is connected to bus i
  hsActive(h,s) switched shunt h uses shunt setting s - i.e. s is active for h
  hsCurrent(h,s) switched shunt h is set to setting s currently;
parameters
  hConductance(h) "(MW consumed by the shunt at v=1pu)"
  hsSusceptance(h,s) "(MVar consumed by the shunt at v=1pu)"
*  shuntSwitchingPenalty '(dol/MVar or 1/MVar)'
  hsPenalty(h,s) '(dimensions of the objective function - dol or dimensionless)';

$gdxin '%ingdx%'
$loaddc switchedShunts
$loaddc shuntSettings
$loaddc ihMap
$loaddc hsActive
$loaddc hConductance
$loaddc hsSusceptance
*$loaddc shuntSwitchingPenalty
$gdxin

display
  switchedShunts
  shuntSettings
  ihMap
  hsActive
  hConductance
  hsSusceptance;
*  shuntSwitchingPenalty;

$gdxin '%currentgdx%'
$loaddc hsCurrent
$gdxin

display
  hsCurrent;
