
* Set initial conditions
$batinclude 'ic_iv%sep%preset.gms'
$ifthen %ic% == 1 $batinclude 'ic_iv%sep%random_all.gms' condensed verbose
$elseif %ic% == 2 $batinclude 'ic_iv%sep%flat.gms' condensed verbose
$elseif %ic% == 3 $batinclude 'ic_iv%sep%random_v.gms' condensed verbose
*$elseif %ic% == 4 $batinclude 'ic_iv%sep%dcopf_pv.gms' limits condensed verbose allon obj Plim timeperiod
*$elseif %ic% == 5 $batinclude 'ic_iv%sep%dcopf_v.gms' limits condensed verbose allon obj Plim timeperiod
*$elseif %ic% == 6 $batinclude 'ic_iv%sep%decoupled.gms' condensed verbose
*$elseif %ic% == 7 $batinclude 'ic_iv%sep%dcopf_pv_loss ' condensed verbose
*$elseif %ic% == 8 $batinclude 'ic_iv%sep%matpower.gms' condensed verbose
$elseif %ic% == 9 $batinclude 'ic_iv%sep%given.gms' condensed verbose
$elseif $ic% == 10 $batinclude 'ic_iv%sep%previous.gms' condensed verbose
$else $batinclude 'ic_iv%sep%default.gms' condensed verbose
$endif

* set prior values of distance-penalized variables
* to their current levels.
V_P_prior(gen) = V_P.l(gen);
V_Q_prior(gen) = V_Q.l(gen);
P_S_prior(i) = P_S.l(i);
Q_S_prior(i) = Q_S.l(i);
V_real_prior(i) = V_real.l(i);
V_imag_prior(i) = V_imag.l(i);
Solar_p_curtail_prior(i) = Solar_p_curtail.l(i);
De_response_Inc_P_prior(i) = De_response_Inc_P.l(i);
De_response_Dec_P_prior(i) = De_response_Dec_P.l(i);

display V_real.l, V_imag.l, Vm;


