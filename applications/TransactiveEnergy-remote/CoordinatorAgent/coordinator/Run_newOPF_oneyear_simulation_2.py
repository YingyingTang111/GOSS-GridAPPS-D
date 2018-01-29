# -----------------------------------------------------------------------------
# Created by Xiangqi Zhu on Jun 16, 2016
# To run GAMS from python automatically and change the load data every time
# To read in all the data to a list 
# Change P, Q, and generator status
# Modified by xinda ke in results output section in 10/5/2016
# Code is modified by Quan Nguyen in July 2017
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
import os
import time
import sys
import getopt
# import solver
from AC_OPF_class import AC_OPF
# -----------------------------------------------------------------------------

system = "7bus"
#system = "ieee118"


def usage():
    usage_str = (
        """
        python Run_newOPF.py <opts>
        
        options
        -h --help
        -n --num_time_steps
        -s --shuntSwitchingPenalty
        -v --load_bus_voltage_goal
        -d --solar_off
        -b --control_load_off
        -c --solar_q_off
        -a --shunt_switching_off
        -r --load_bus_volt_dead_band
        -u --load_bus_volt_pen_coeff_1
        -t --load_bus_volt_pen_coeff_2
        -p --previous_solution_as_start_point
        -f --file_number
        -b --debug_start_from_certan_point
        """)
    print(usage_str)
    
    

if __name__ == '__main__':
    
    # get options from python call --------------------------------------------
    try:
        opts, args = getopt.getopt(
            [],
            "hn:s:v:d:b:c:a:r:u:t:p:f:b:",
            ["help",
             "num_time_steps",
             "shuntSwitchingPenalty1",
             "load_bus_voltage_goal",
             "solar_off",
             "control_load_off",
             "solar_q_off",
             "shunt_switching_off",
             "load_bus_volt_dead_band",
             "load_bus_volt_pen_coeff_1",
             "load_bus_volt_pen_coeff_2",
             "previous_solution_as_start_point"
             "file_number"
             "debug_start_from_certan_point"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-n", "--num_time_steps"):
            Nbend = int(arg) 
        elif opt in ("-s", "--shuntSwitchingPenalty1"):
            shuntSwitchingPenalty1 = float(arg)
        elif opt in ("-v", "--load_bus_voltage_goal"):
            load_bus_voltage_goal = float(arg)
        elif opt in ("-d", "--solar_off"):
            solar_off = int(arg)
        elif opt in ("-b", "--control_load_off"):
            control_load_off = int(arg)
        elif opt in ("-c", "--solar_q_off"):
            solar_q_off = int(arg)
        elif opt in ("-a", "--shunt_switching_off"):
            shunt_switching_off = int(arg)
        elif opt in ("-r", "--load_bus_volt_dead_band"):
            load_bus_volt_dead_band = float(arg)
        elif opt in ("-u", "--load_bus_volt_pen_coeff_1"):
            load_bus_volt_pen_coeff_1 = float(arg)
        elif opt in ("-t", "--load_bus_volt_pen_coeff_2"):
            load_bus_volt_pen_coeff_2 = float(arg)
        elif opt in ("-p", "--previous_solution_as_start_point"):
            previous_solution_as_start_point = int(arg)
        elif opt in ("-f", "--file_number"):
            fileorder = int(arg)   
        elif opt in ("-b", "--debug_start_from_certan_point"):
            startrow = int(arg)  
    # -------------------------------------------------------------------------
    
    # Calculate the program running time
    ACOPF_start_time = time.time()  
    
    # For Editing Excel
    if os.path.isfile(mypath + "switched_shunt_current.gdx"):
        os.remove(mypath + "switched_shunt_current.gdx")           
    # Temporary invalid for test purpose
    if os.path.isfile(mypath + "one_step_solution.gdx"):
        os.remove(mypath + "one_step_solution.gdx")
    

    try:
            
        if system == "7bus":
            # 118-BUS SYSTEM PARAMETERS ----------------------------------------------
            system_folder                           = mypath + '7bus'
            sum_bus_num                             = 7
            sum_load_num                            = 3
            sum_gennum                              = 1 
            # Define the location of solar bus and solar apparent power
            definegenlocation                       = True
            sum_distributed_gen                     = 2
            control_load_BusID                      = 18    
            solar_qlimit_busID                      = 18
            # Nbend is for the number of steps we'd like to run
            Nbend                                   = 1 #(12*duration[hour]+1)  
            # Define start row
            startrow                                = 2   #(12*stating_hour+1)    
            Nbend2                                  = 5   # DR step size
            #nbend2 is the column of the price signal    
            # file order specify the date   
            fileorder                               = 1
            simuyear                                = 2006
            simutimestep                            = 5
            GDXcaseName                             = mypath + '7bus.gdx'
            # Time-stamp in the input excel file? (this option is temporary)
            TimeStamp                               = False
            solar_curtail_busid                     = 84
            #-------------------------------------------------------------------------
            
        else:
            assert False, "specify system in main python code"

    except NameError:
        assert False, "specify system in main python code"

 
    ## OPTIMIZATION PROBLEM PARAMETERS ----------------------------------------
    load_bus_voltage_goal                   = 1.0
    solar_curtailment_off                   = 1
    control_load_off                        = 0
    solar_q_off                             = 0
    shunt_switching_off                     = 1
    previous_solution_as_start_point        = 0 
    # Penalty terms
    shuntSwitchingPenalty1                  = 1e-3
    demand_response_decrease_penalty        = 10
    demand_response_increase_penalty        = 10
    solar_curtail_penalty                   = 50
    generator_voltage_deviation_penalty     = 1e5
    load_bus_volt_pen_coeff_1               = 1
    load_bus_volt_pen_coeff_2               = 0
    load_bus_volt_dead_band                 = 1e-2
    DRnum                                  = 2

    # can use values 0,1,2,3,9, where 0 start from last solution point, 1 from random all, 2 from flat start, 3 is random voltage, 9 is for given starting point
    icset                                   = [9, 2, 9, 3, 1, 0, 0, 0]    
    max_iter                                = 4
    # Control voltage of generators and loads at scheduled values or not
    opt_Vgen_dev                            = 1
    opt_Vload_dev                           = 1        
    # -------------------------------------------------------------------------    
    
    
    ## OPTIONS FOR PLOTTING RESULTS -------------------------------------------
    # export the result to spreadsheet or not
    export_to_spreadsheet                   = True

    # -------------------------------------------------------------------------
                
    # Input excel files
    bus_list_file                           = mypath + '/7bus/bus_list.xlsx'      
    distrb_gen_index_file                   = mypath + '/7bus/distribu_index2.xlsx'
    solar_oneyear_file                      = mypath + '/7bus/solar_s_oneyeartest.xlsx'
    GAMS_OptionSolution_GDXfile             = mypath + "one_step_solution.gdx"
    demand_response_file                    = mypath + '/7bus/demand_response_load_price.xlsx'
    GAMS_OPF_file                           = mypath + "iv_acopf_reformulation_lop_adj.gms"    
     

    """ CALL AC_OPF object"""                    
    System = AC_OPF(Nbend, Nbend2, DRnum, fileorder, simuyear, simutimestep, startrow, definegenlocation, sum_bus_num, sum_load_num, sum_gennum, sum_distributed_gen,\
                    solar_curtail_busid, control_load_BusID,solar_qlimit_busID, load_bus_voltage_goal, solar_curtailment_off, control_load_off, solar_q_off, shunt_switching_off,\
                    shuntSwitchingPenalty1, demand_response_decrease_penalty, demand_response_increase_penalty, solar_curtail_penalty, generator_voltage_deviation_penalty,\
                    load_bus_volt_pen_coeff_1, load_bus_volt_pen_coeff_2, load_bus_volt_dead_band, opt_Vgen_dev, opt_Vload_dev, previous_solution_as_start_point, icset, max_iter,\
                    bus_list_file, distrb_gen_index_file, solar_oneyear_file, GAMS_OptionSolution_GDXfile, GAMS_OPF_file, demand_response_file,\
                    export_to_spreadsheet, mypath, GDXcaseName, TimeStamp, feederLoad, self.P, self.Q, self.DRquantity, self.DRprice)


    print("--- Total running time: %s seconds ---" % (time.time() - start_time))
