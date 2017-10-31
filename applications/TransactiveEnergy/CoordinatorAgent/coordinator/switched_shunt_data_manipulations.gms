$title switched shunt data manipulations

* Might want larger penalties on larger devices
* as these are more expensive and wear and tear on them
* thus costs more.
* Easier to understand in terms of penalizing just the
* number of switches rather than the size.
$if not set useDeviceSize $set useDeviceSize 0

* exponent to be used on the shunt switching penalty
* quadratic gives more gradual shunt switching behavior
* but linear is easier to understand in terms of cost of
* wear and tear on device
* best results might come from linear penalty with
* hard bounds on number of switches allowed per device
$if not set shuntSwitchingPenaltyPower $set shuntSwitchingPenaltyPower 2

* if using UW data where switched shunts were replaced by fixed shunts
* and data on fixed shunts is provided separately,
* then clear the fixed shunt data
$if not set clearFixedShuntAdmittance $set clearFixedShuntAdmittance 1

* deactivate all switched shunts
$if not set clearSwitchedShuntAdmittance $set clearSwitchedShuntAdmittance 0

* shunt switching penalty
* per number of switches
$if not set shuntSwitchingPenalty $set shuntSwitchingPenalty 1e3

* rather than a hard limit on number of switches per device
* try a very high penalty on >= 2 switches per device.
* adds a large constant
$if not set shuntSwitchingPenaltyAtLeast2 $set shuntSwitchingPenaltyAtLeast2 0

* switched shunt data checks
loop(h,
  if(sum(s$hsActive(h,s),1) < 2,
    abort 'Switched shunts must have at least 2 active settings. Just 1 active setting should be modeled as a fixed shunt. 0 active settings does not make sense.';
  );
);

* compute penalty for each setting
hsPenalty(h,s)$hsActive(h,s) = sum(s1$hsCurrent(h,s1), %shuntSwitchingPenalty% * (abs(

$ifthen %useDeviceSize% == 1
hsSusceptance(h,s) - hsSusceptance(h,s1)
$endif

$ifthen %useDeviceSize% == 0
ord(s) - ord(s1)
$endif

) ** %shuntSwitchingPenaltyPower% ));

* apply penalty factor for at least two switches per device
hsPenalty(h,s)$(
    hsActive(h,s) and
    sum(s1$(hsCurrent(h,s1) and abs(ord(s) - ord(s1)) gt 1.5),1) gt 0) =  
  %shuntSwitchingPenaltyAtLeast2% +
  hsPenalty(h,s);

* convert switched shunt data to per unit
hConductance(h) = hConductance(h) / baseMVA;
hsSusceptance(h,s)$hsActive(h,s) = hsSusceptance(h,s) / baseMVA;

$ifthen %clearFixedShuntAdmittance% == 1
Gs(bus) = 0;
Bs(bus) = 0;
$endif

$ifthen %clearSwitchedShuntAdmittance% == 1
hConductance(h) = 0;
hsSusceptance(h,s)$hsActive(h,s) = 0;
$endif