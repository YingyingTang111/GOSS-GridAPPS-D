
# write by xinda ke in results output section in 10/5/2016

## For GAMS API
from __future__ import print_function



#define some class over here

class Form_header:
    def __init__(self):
        self.busindex = []
        self.genindex = []
        self.genatbus = []
        self.solaratbus = []
        self.loadindex = []
        self.switched_shunt_susceptance_buses = []
        self.switched_shunt_susceptance_shunts = []
    def add_solaratbus(self, x):
        self.solaratbus.append(x)
    def return_solaratbus(self):
        return self.solaratbus
    def add_loadindex(self, x):
        self.loadindex.append(x)
    def return_loadindex(self):
        return self.loadindex
    def add_genatbus(self, x):
        self.genatbus.append(x)
    def return_genatbus(self):
        return self.genatbus
    def add_busindex(self, x):
        self.busindex=list(set(range(1, x+1, 1)))
    def return_busindex(self):
        return self.busindex
    def add_genindex(self, x):
        self.genindex.append(x)
    def return_genindex(self):
        return self.genindex
    
class Solutiondata:
    def __init__(self):
        self.token1_vm=[]
        self.token2_Reac_P=[]
        self.token3_Reac_Solar=[]
        self.token4_tot_cost=[]
        self.token5_tot_loss=[]
        self.token6_tot_swit=[]
        self.token7_v_devi_loadbus=[]
        self.token8_solver_stat=[]
        self.token9_model_stat=[]
        self.token10_solar_p_curt=[]
        self.token11_DR_inc_P=[]
        self.token12_DR_dec_P=[]
        self.token13_DR_inc_Q=[]
        self.token14_DR_dec_Q=[]
        self.pgen=[]
        self.demand=[]
        self.generator_voltage=[]
        self.nongenerator_voltage=[]
        self.genvoltage_deviation=[]
        self.nongenvoltage_deviation=[]
        self.Vschedule=[]
        self.genatbus=[]
        self.solarQlimit_Up=[]
        self.solarQlimit_Down=[]
        self.bus_va_degrees = []
        self.switched_shunt_susceptance_values=[]
        self.switched_shunt_susceptance_by_bus_values=[]
    def add_vm(self, x):
        self.token1_vm.append(x)
    def return_vm(self):
        return self.token1_vm
    
    def add_Reac_P(self, x):
        self.token2_Reac_P.append(x)
    def return_Reac_P(self):
        return self.token2_Reac_P
    
    def add_Reac_Solar(self, x):
        self.token3_Reac_Solar.append(x)
    def return_Reac_Solar(self):
        return self.token3_Reac_Solar  
        
    def add_tot_cost(self, x):
        self.token4_tot_cost.append(x)
    def return_tot_cost(self):
        return self.token4_tot_cost   
    
    def add_tot_loss(self, x):
        self.token5_tot_loss.append(x)
    def return_tot_loss(self):
        return self.token5_tot_loss  
    
    def add_tot_swit(self, x):
        self.token6_tot_swit.append(x)
    def return_tot_swit(self):
        return self.token6_tot_swit   
        
    def add_v_devi_loadbus(self, x):
        self.token7_v_devi_loadbus.append(x)
    def return_v_devi_loadbus(self):
        return self.token7_v_devi_loadbus  
      
    def add_solver_stat(self, x):
        self.token8_solver_stat.append(x)
    def return_solver_stat(self):
        return self.token8_solver_stat 

    def add_model_stat(self, x):
        self.token9_model_stat.append(x)
    def return_model_stat(self):
        return self.token9_model_stat
    
    def add_solar_p_curt(self, x):
        self.token10_solar_p_curt.append(x)
    def return_solar_p_curt(self):
        return self.token10_solar_p_curt
    
    def add_DR_inc_P(self, x):
        self.token11_DR_inc_P.append(x)
    def return_DR_inc_P(self):
        return self.token11_DR_inc_P
    
    def add_DR_dec_P(self, x):
        self.token12_DR_dec_P.append(x)
    def return_DR_dec_P(self):
        return self.token12_DR_dec_P

    def add_DR_inc_Q(self, x):
        self.token13_DR_inc_Q.append(x)
    def return_DR_inc_Q(self):
        return self.token13_DR_inc_Q
    
    def add_DR_dec_Q(self, x):
        self.token14_DR_dec_Q.append(x)
    def return_DR_dec_Q(self):
        return self.token14_DR_dec_Q

    def add_pgen(self, x):
        self.pgen.append(x)
    def return_pgen(self):
        return self.pgen

    def add_demand(self, x):
        self.demand.append(x)
    def return_demand(self):
        return self.demand

    def add_generator_voltage(self, x):
        self.generator_voltage.append(x)
    def return_generator_voltage(self):
        return self.generator_voltage

    def add_nongenerator_voltage(self, x):
        self.nongenerator_voltage.append(x)
    def return_nongenerator_voltage(self):
        return self.nongenerator_voltage
    
    def add_Vschedule(self, x):
        self.Vschedule.append(x)
    def return_Vschedule(self):
        return self.Vschedule
    
    def add_solarQlimit_Up(self, x):
        self.solarQlimit_Up.append(x)
    def return_solarQlimit_Up(self):
        return self.solarQlimit_Up

    def add_solarQlimit_Down(self, x):
        self.solarQlimit_Down.append(x)
    def return_solarQlimit_Down(self):
        return self.solarQlimit_Down

    def add_bus_va_degrees(self, x):
        self.bus_va_degrees.append(x)
    def return_bus_va_degrees(self):
        return self.bus_va_degrees
    
    def add_switched_shunt_susceptance_values(self, x):
        self.switched_shunt_susceptance_values.append(x)
    def return_switched_shunt_susceptance_values(self):
        return self.switched_shunt_susceptance_values

    def add_switched_shunt_susceptance_by_bus_values(self, x):
        self.switched_shunt_susceptance_by_bus_values.append(x)
    def return_switched_shunt_susceptance_by_bus_values(self):
        return self.switched_shunt_susceptance_by_bus_values

