* prior variable values
* penalize the distance of the new solution to
* these prior variables in order to promote
* continuity
parameter
    V_P_prior(gen)           "Real power generation of generator",
    V_Q_prior(gen)           "Reactive power generation of generator",
    P_S_prior(i)      "real power generation of solar bus"
    Q_S_prior(i)      "reactive power generation of solar bus"
    V_real_prior(i)          "Real part of bus voltage",
    V_imag_prior(i)          "Imaginary part of bus voltage",
    Solar_p_curtail_prior(i)    "the amount of real power cutailed from controllable
    De_response_Dec_P_prior(i)         "the decrease in demand response"
    De_response_Inc_P_prior(i)         "the increment in demand response"
;

* set prior values of distance-penalized variables
* to their current levels.
V_P_prior(gen) = V_P.l(gen);
V_Q_prior(gen) = V_Q.l(gen);
P_S_prior(i) = P_S.l(i)
Q_S_prior(i) = Q_S.l(i)
V_real_prior(i) = V_real.l(i)
V_imag_prior(i) = V_imag.l(i)
Solar_p_curtail_prior(i) = Solar_p_curtail.l(i)
De_response_Inc_P_prior(i) = De_response_Inc_P.l(i)
De_response_Decc_P_prior(i) = De_response_Dec_P.l(i)
