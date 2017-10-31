$title switched shunt declarations

* switched shunt data
*set isubset(i);
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
  hConductance(h) '(MW consumed by the shunt at v=1pu)'
  hsSusceptance(h,s) '(MVar consumed by the shunt at v=1pu)'
  shuntSwitchingPenalty '(dol/MVar or 1/MVar)'
  hsPenalty(h,s) '(dimensions of the objective function - dol or dimensionless)';

* switched shunt variables
binary variables
  V_hsSelect(h,s) '= 1 if setting s is selected for shunt h';
free variables
  V_obj_shunt_switching objective for shunt switching problem
  V_shunt_switching_penalty total shunt switching penalty
  V_hSusceptance(h) shunt susceptance resulting from the selected setting;

* switched shunt equations
equations
  c_hSelect(h) requires exactly 1 setting to be selected
  c_hSusceptance(h) defines selected shunt susceptance
  c_BalanceP(bus) real power balance - including treatment of solar and switched shunts
  c_BalanceQ(bus) reactive power balance - including treatment of solar and switched shunts
  c_shunt_switching_penalty_def defines total shunt switching penalty
  c_obj_shunt_switching_def defines objective for shunt switching problem

* switched shunt models
models
  feas_switched_shunt /
         c_hSelect, c_hSusceptance, c_BalanceP, c_BalanceQ,
         c_LineIrij, c_LineIrji, c_LineIqij, c_LineIqji,
         c_Lossijc,c_Lossi,v_generator_devi1, v_generator_devi2,
         v_generator_hardupl, v_generator_harddownl
         p_generator_addup, p_generator_addlow, solarp_real_addup,
         solarp_real_addlow,solarp_reactive_addup,solarp_reactive_addlow,
         c_shunt_switching_penalty_def /
  acopf_switched_shunt /
         feas_switched_shunt, c_obj, c_obj_shunt_switching_def /;

* switched shunt equation definitions
c_obj_shunt_switching_def..
      V_obj_shunt_switching
  =e= V_objcost
   +  V_shunt_switching_penalty;
c_shunt_switching_penalty_def..
      V_shunt_switching_penalty
  =e= sum((h,s)$hsActive(h,s),hsPenalty(h,s)*V_hsSelect(h,s));
c_hSelect(h)..
      sum(s$hsActive(h,s),V_hsSelect(h,s))
  =e= 1;
c_hSusceptance(h)..
      V_hSusceptance(h)
  =e= sum(s$hsActive(h,s),hsSusceptance(h,s)*V_hsSelect(h,s));
c_BalanceP(i)$(type(i) ne 4)..
        sum(gen$(atBus(gen,i) and status(gen)), V_P(gen))
        - Pd(i)
        + P_S(i)$(sum(solarbus,solarlocation(solarbus,i)) ne 0)
        - sum(h$ihMap(i,h),hConductance(h))*(sqr(V_real(i)) + sqr(V_imag(i)))
            =e=
          V_real(i) *
        ( sum((j,c)$(branchstatus(i,j,c) ), V_LineIr(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIr(i,j,c)) )
        + V_imag(i) *
         (sum((j,c)$(branchstatus(i,j,c) ), V_LineIq(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIq(i,j,c)))
        + Gs(i) * (sqr(V_real(i)) + sqr(V_imag(i)))
;
c_BalanceQ(i)$(type(i) ne 4)..
        sum(gen$(atBus(gen,i) and status(gen)), V_Q(gen))
        - Qd(i)
        + Q_S(i)$(sum(solarbus,solarlocation(solarbus,i)) ne 0)
        + sum(h$ihMap(i,h),V_hSusceptance(h))*(sqr(V_real(i)) + sqr(V_imag(i)))
            =e=
        - V_real(i) *
        ( sum((j,c)$(branchstatus(i,j,c) ), V_LineIq(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIq(i,j,c)))
        + V_imag(i) *
        ( sum((j,c)$(branchstatus(i,j,c) ), V_LineIr(i,j,c))
          + sum((j,c)$(branchstatus(j,i,c) and not(branchstatus(i,j,c))  ), V_LineIr(i,j,c)))
        - Bs(i) * (sqr(V_real(i)) + sqr(V_imag(i)))
        - (sqr(V_real(i)) + sqr(V_imag(i))) * sum(bus_s$(not sameas(bus_s,'given')), Bswitched(i,bus_s) * V_shunt(i,bus_s))
;
