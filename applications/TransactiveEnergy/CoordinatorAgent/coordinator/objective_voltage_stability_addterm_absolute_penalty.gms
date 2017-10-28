$title Cost objective calculations for OPF models
*this file is modified by Xinda Ke from Wisconsin university IV_acopf.gms
*updated by Xinda ke in 7/26/2016

* Set costmodel variable
costmodel(gen)= 2;



*-- Convexity Check
* Not part of system of equations
* LP/QCP/NLP can't handle nonconvex piecewise linear cost functions
set thisgen(gen);

parameters cur_slope, next_slope;
loop(gen$(status(gen) and (costmodel(gen) eq 1) and (numcostpts(gen) > 2)),
    next_slope = (costpts_y(gen,'2') - costpts_y(gen,'1'))
                 / (costpts_x(gen,'2') - costpts_x(gen,'1'));
    loop(costptset$(ord(costptset) < numcostpts(gen) - 1),
        cur_slope = next_slope;
        if((ord(costptset) < numcostpts(gen) - 2) and (costpts_x(gen,costptset+2) eq costpts_x(gen,costptset+1)),
            abort "Zero-length piecewise segment detected";
        );
        next_slope = (costpts_y(gen,costptset+2) - costpts_y(gen,costptset+1))
                     / (costpts_x(gen,costptset+2) - costpts_x(gen,costptset+1))

        if(cur_slope - next_slope > 1e-8,
            thisgen(gen1)=no; thisgen(gen)=yes;
            display thisgen;
            abort "Nonconvex piecewise linear costs not supported";
        );
    );
);


*===== SECTION: EQUATIONS PART 2
* Defining piecewise linear generator cost curves
* P is in per-unit, costpts_x is in MW, and costpts_y is in $/hr


$ifthen.nobids %demandbids%==1
* Revenue from elastic demand are less than a concave function
c_demandbid_revenue(demandbid,demandbid_s)$((ord(demandbid_s) lt numdemandpts(demandbid)))..
V_demandbid_rev(demandbid) =l=
    ((demandpts_y(demandbid,demandbid_s+1) - demandpts_y(demandbid,demandbid_s))/
      (demandpts_x(demandbid,demandbid_s+1) - demandpts_x(demandbid,demandbid_s)))
       * (V_Pd_elastic(demandbid)*baseMVA - demandpts_x(demandbid,demandbid_s))
   + demandpts_y(demandbid,demandbid_s)
;
$endif.nobids

c_obj..
    V_objcost =e=
*0 objective function
         sum(bus$load(bus),  sqr(sqrt(sqr(V_real(bus)) + sqr(V_imag(bus)))-1))
+ 10* sum(i,V_devi(i))
*the term of line losses. tobe checked, tobe verified
 + sum(i,V_Lossi(i));

