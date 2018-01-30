$title switched shunt data

sets
  switchedShunts
/
    h1
/
  shuntSettings
/
    s1
    s2
    s3
/
;
alias(switchedShunts,h,h0,h1,h2);
alias(shuntSettings,s,s0,s1,s2);
sets
  ihMap(i,h) switched shunt h is connected to bus i
/
    1.h1
/
  hsActive(h,s) switched shunt h uses shunt setting s - i.e. s is active for h
/
    h1.s1
    h1.s2
    h1.s3
/
  hsCurrent(h,s) switched shunt h uses shunt setting s currently - i.e. prior to solve
/
    h1.s2
/
;
parameters
  shuntSwitchingPenalty "objective penalty per switch"
/
  1e-3
/
  hConductance(h) "(MW consumed by the shunt at v=1pu)"
/
    h1 0
/
  hsSusceptance(h,s) "(MVar consumed by the shunt at v=1pu)"
/
    h1.s1 -1
    h1.s2 0
    h1.s3 1
/
  hsPenalty(h,s) "objective penalty on using setting s for switched shunt h"
/
    h1.s1 10
    h1.s2 0
    h1.s3 10
/
;
