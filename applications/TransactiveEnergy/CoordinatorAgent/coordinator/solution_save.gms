*file filename;
*put_utility filename 'Exec' / 'results_' i.tl:0 '.gdx';






*put_utilities  'gdxout' / 'out' Nb:0:0;

$ifthen %savesol% == 1
display "save solution";
execute_unload '%filepath%temp_solution.gdx',TotalLoss, total_cost, V_Q, shuntB,Qd,line, Vm, Pmax, Pmin, Qmax, Qmin, r, x, bc, atBus, V_P, P_S, Q_S;
execute 'gams %filepath%save_solution.gms gdxcompress=1 --ac=1 --case=%case% --solution=%filepath%temp_solution.gdx --timeperiod=%timeperiod% --out=%filepath%%casename%_AC_base_solution.gdx'
execute 'GDXXRW.exe %filepath%temp_solution.gdx O=output_voltage_mag.xlsx squeeze=N par=Pmin'
execute 'GDXXRW.exe %filepath%temp_solution.gdx O=output_totalloss.xlsx squeeze=N par=TotalLoss'
execute 'GDXXRW.exe %filepath%temp_solution.gdx O=output_solarreactive.xlsx squeeze=N var=Q_S'
execute 'GDXXRW.exe %filepath%temp_solution.gdx O=output_Qg.xlsx squeeze=N var=V_Q'
execute 'GDXXRW.exe %filepath%temp_solution.gdx O=output_cost.xlsx squeeze=N par=total_cost'
*execute 'GDXXRW.exe %filepath%temp_solution.gdx O=%filepath%output_Pg.xlsx squeeze=N var=V_P'
*execute 'GDXXRW.exe %filepath%temp_solution.gdx O=%excelpath%generatorlocation.xlsx squeeze=N par=atBus'
*execute 'GDXXRW.exe %filepath%temp_solution.gdx O=%excelpath%output_demand_reactive.xlsx squeeze=N par=Qd'
*execute 'GDXXRW.exe %filepath%temp_solution.gdx O=%excelpath%demandreal.xlsx squeeze=N par=Pmin'
*execute 'GDXXRW.exe %filepath%temp_solution.gdx O=%excelpath%line.xlsx squeeze=N par=line'
*execute 'GDXXRW.exe %filepath%temp_solution.gdx O=%excelpath%branchx.xlsx squeeze=N par=x'
*execute 'GDXXRW.exe %filepath%temp_solution.gdx O=%excelpath%branchbc.xlsx squeeze=N par=bc'
*put_utility 'exec' / 'GDXXRW.exe %filepath%temp_solution.gdx O=output_voltage_mag' Nb:0 '.xlsx squeeze=N par=Vm';
if(errorlevel ne 0, abort "Saving solution failed!");
execute 'rm %filepath%temp_solution.gdx'
$endif
);

