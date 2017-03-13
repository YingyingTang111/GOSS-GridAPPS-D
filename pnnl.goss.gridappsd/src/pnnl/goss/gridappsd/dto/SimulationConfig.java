package pnnl.goss.gridappsd.dto;

import java.io.Serializable;

public class SimulationConfig  implements Serializable {
	
	//eg, forward backward sweeper
	public String power_flow_solver_method;
	//how long the simulation should last (in seconds), default 1 day 
	public long duration = 86400;
	//simulation id (auto-generated by process manager)
	public String simulation_id;
	//user friendly name for the simulation
	public String simulation_name;
	//??
	public String simulator;
	//time that you want the simulation to start, expected format yyyy-MM-dd HH:mm:ss 
	public String start_time;
	public String getPower_flow_solver_method() {
		return power_flow_solver_method;
	}
	public void setPower_flow_solver_method(String power_flow_solver_method) {
		this.power_flow_solver_method = power_flow_solver_method;
	}
	public long getDuration() {
		return duration;
	}
	public void setDuration(long duration) {
		this.duration = duration;
	}
	public String getSimulation_id() {
		return simulation_id;
	}
	public void setSimulation_id(String simulation_id) {
		this.simulation_id = simulation_id;
	}
	
	public String getSimulation_name() {
		return simulation_name;
	}
	public void setSimulation_name(String simulation_name) {
		this.simulation_name = simulation_name;
	}
	public String getSimulator() {
		return simulator;
	}
	public void setSimulator(String simulator) {
		this.simulator = simulator;
	}
	public String getStart_time() {
		return start_time;
	}
	public void setStart_time(String start_time) {
		this.start_time = start_time;
	}

	
	//TODO change this to more detailed object about output??? maybe not needed
//	public String[] output_object_mrid;
	//Default output, json message per timestep
	
	//getting rid of this for now, only 1 simulation at once
//	public String[] simulator_name;

//	@Override
	public String toString() {
		return "ClassPojo [power_flow_solver_method = "
				+ power_flow_solver_method + ", duration = " + duration
				+ ", simulation_name = " + simulation_name + ", simulator = "
				+ simulator + ", start_time = " + start_time
				+ ", simulator = " + simulator + "]";
	}
	
	
	
}