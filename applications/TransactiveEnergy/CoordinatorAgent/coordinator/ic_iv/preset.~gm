$ontext
sets values for some variables that might not otherwise be set
$offtext

V_P.l(gen) = 0;
V_Q.l(gen) = 0;
V_LineIr.l(i,j,c) = 0;
V_LineIq.l(i,j,c) = 0;
V_P_system_deviation.l = 0;
V_switchedshuntB.l(i)$sum(bus_s$numBswitched(i,bus_s), 1) = 0;
V_shunt.l(bus,bus_s)$numBswitched(bus,bus_s) = 0;
*P_S.l(i)$(isSolar(i) and contro_solar_location(i) ne 1) = solar_r(i);
*P_S.l(i)$(isSolar(i) and contro_solar_location(i) eq 1) = contro_solar_pout(i);
Q_S.l(i)$isSolar(i) = 0;
solar_p_curtail.l(bus)$contro_solar_location(bus) = 0;
de_response_dec_p.l(bus)$pd_respon_location(bus) = 0;
de_response_inc_p.l(bus)$pd_respon_location(bus) = 0;

