if __name__ == "__main__":
     import iso2flux 
     import cobra
     from cobra import Model, Reaction, Metabolite
     from cobra.manipulation.modify import convert_to_irreversible
     from cobra.flux_analysis.variability import flux_variability_analysis
     from  warnings import warn
     import numpy as np
     #from scipy.integrate import odeint
     #import subprocess
     from timeit import timeit
     import copy
     import math
     import json
     import tkFileDialog
     import Tkinter
     import sys
     #iso2flux imports
     from iso2flux.classes.label_model import Label_model #Import the label_model class
     #from iso2flux.classes.isotopomer import isotopomer #Import the label_model class
     
     #from iso2flux.flux_functions.apply_ratios import apply_ratios, remove_ratio #Functions to apply ratios of fluxes
     #from iso2flux.flux_functions.remove_reflection_co2_reactions import remove_reflection_co2_reactions
     #from iso2flux.flux_functions.get_fluxes import get_fluxes
     #from iso2flux.flux_functions.define_reaction_group import define_reaction_group
     
     #from iso2flux.label_propagation_functions.add_label_reactions import add_label_reactions
     from iso2flux.label_propagation_functions.find_missing_reactions import find_missing_reactions
     
     #from iso2flux.emus_functions.build_emu_model import build_emu_model
     #from iso2flux.emus_functions.check_mass_balance import check_mass_balance
     #from iso2flux.emus_functions.remove_identical_reactions import remove_identical_reactions
     #from iso2flux.emus_functions.split_model import split_model
     #from iso2flux.emus_functions.emu_add_label_ouputs_inputs import emu_add_label_ouputs_inputs
     #from iso2flux.emus_functions.expand_emu_models import expand_emu_models
     #from iso2flux.emus_functions.set_initial_label import set_initial_label
     #from iso2flux.emus_functions.remove_impossible_emus import remove_impossible_emus
     #from iso2flux.emus_functions.build_variables_dict import build_variables_dict
     #from iso2flux.emus_functions.build_emu_reaction_dicts import build_emu_reaction_dicts
     
     #from iso2flux.emus_functions.write_emus_equations import write_emus_equations
     #from iso2flux.emus_functions.compile_c_code import compile_c_code
     #from iso2flux.emus_functions.set_equations_variables import set_equations_variables
     from iso2flux.emus_functions.solver import solver #To do, move it to emu equations
     
     from iso2flux.output_functions.model_to_excel import model_to_excel
     from iso2flux.output_functions.showr import showr
     from iso2flux.output_functions.export_label_results import export_label_results
     from iso2flux.output_functions.write_fva import write_fva
     #from iso2flux.output_functions.print_emu_results import  print_emu_results
     
     from iso2flux.fitting.anneal import annealing
     from iso2flux.fitting.get_objective_function import get_objective_function
     from iso2flux.fitting.apply_parameters import apply_parameters
     from iso2flux.fitting.clear_parameters import clear_parameters 
     from iso2flux.fitting.save_parameters import save_parameters
     from iso2flux.fitting.load_parameters import load_parameters
     from iso2flux.fitting.identify_free_parameters import identify_free_parameters
     from iso2flux.fitting.confidence_intervals import estimate_confidence_intervals
     from iso2flux.fitting.sampling import sampling
     from iso2flux.fitting.clear_parameters import clear_parameters
     
     from iso2flux.misc.check_steady_state import check_steady_state
     from iso2flux.misc.check_simulated_fractions import check_simulated_fractions
     from iso2flux.flux_functions.expression_analysis import integrate_omics_imat,integrate_omics_gim3e
     from iso2flux.flux_functions.minimal_flux import add_flux_limit_constraints
     from iso2flux.misc.save_load_iso2flux_model import save_iso2flux_model,load_iso2flux_model
     from iso2flux.misc.round_functions import round_up, round_down 
     #from iso2flux.misc.convert_model_to_irreversible import convert_to_irreversible_with_indicators
     
     from iso2flux.gui.gui import launch_gui
     
     from iso2flux.input_functions.read_experimental_mid import read_experimental_mid
     from iso2flux.input_functions.read_isotopomer_model import read_isotopomer_model
     from iso2flux.input_functions.read_constraints import read_flux_constraints 
     from iso2flux.input_functions.read_isotoflux_settings import read_isotoflux_settings
     from iso2flux.doc.open_manual import open_manual
     from iso2flux.flux_functions.check_feasibility import check_feasibility
     #from iso2flux.dynamic.interpolate_timecourse import interpolate_timecourse
     #from iso2flux.dynamic.interpolate_timecourse import interpolate_timecourse
     """mid_data_name="CA_34_label_reduit.xlsx" 
     iso_model_file="isotopomer_model_reduit2.xlsx"""
     #model=cobra.io.read_sbml_model("simple_model.sbml")
     p_dict={'reactions_with_forced_turnover': [], 'annealing_cycle_time_limit': 1800, 'confidence_max_absolute_perturbation': 10, 'turnover_exclude_EX': True, 'annealing_n_processes': 1, 'annealing_p0': 0.4, 'identify_free_parameters_add_turnover': True, 'minimum_sd': 0.01, 'annealing_max_perturbation': 1, 'turnover_upper_bound': 0, 'confidence_perturbation': 0.1, 'annealing_m': 1000, 'annealing_n': 20, 'annealing_relative_max_sample': 0.4, 'confidence_min_absolute_perturbation': 0.05, 'annealing_pf': 0.0001, 'confidence_significance': 0.95, 'identify_free_parameters_change_threshold': 0.005, 'parameter_precision': 0.0001, 'fraction_of_optimum': 1, 'lp_tolerance_feasibility': 1e-06, 'identify_free_parameters_n_samples': 200, 'annealing_relative_min_sample': 0.25, 'annealing_iterations': 2}
     model=None
     try:
       mid_data_name=sys.argv[1]
     except:
       quit()
     print mid_data_name
     try:
       iso_model_file=sys.argv[2]
     except:
       quit()
     print iso_model_file
     if len(sys.argv)>3:
        print sys.argv[3]
        try:
          p_dict.update(read_isotoflux_settings(sys.argv[3]))
          
        except: 
          print "Wrong parameters file"
     if len(sys.argv)>4:
        try:
            print sys.argv[4]
            model=cobra.io.read_sbml_model((sys.argv[4]))     
        except:
            print "Wrong model file"
     if len(sys.argv)>5: 
        try:
          model,ratio_dict=read_flux_constraints(model,ratio_dict={},file_name=sys.argv[5])
        except: 
          print "Wrong constraints file"
     if model==None:
         model=cobra.io.read_sbml_model("simple_model.sbml")     
     
     
     
     fraction_of_optimum=p_dict["fraction_of_optimum"]
     
     
     #model,ratio_dict=read_flux_constraints(model,file_name="normoxia_constraints.xlsx")
     fva=flux_variability_analysis(model,fraction_of_optimum=1)
     write_fva(model,fn="unconstrained_fluxes"+mid_data_name,fraction=p_dict["fraction_of_optimum"],remove0=False,change_threshold=0.001,mode="full",lp_tolerance_feasibility=p_dict["lp_tolerance_feasibility"])
     #Remember which reactions can be negative to add them as turnover later as negative lower bound may be removed when minimizing flux
     reactions_with_forced_turnover=p_dict["reactions_with_forced_turnover"]
     """for reaction in model.reactions:
         if "EX_" not in reaction.id and reaction.lower_bound<0:
            reactions_with_forced_turnover.append(reaction.id) 
     reversible_fva=add_flux_limit_constraints(model,fraction_of_optimum_objective=0, fraction_of_flux_minimum=10,boundaries_precision=0.001,solver="cplex")
     write_fva(model,fn="normoxia_minimum_fluxes.xlsx",fraction=1,remove0=False,change_threshold=0.001,mode="full",lp_tolerance_feasibility=1e-6)"""
     label_model=Label_model(model,lp_tolerance_feasibility=p_dict["lp_tolerance_feasibility"],parameter_precision=p_dict["parameter_precision"],reactions_with_forced_turnover=reactions_with_forced_turnover) #initialize the label model class   
     read_isotopomer_model(label_model,iso_model_file,header=True)
     find_missing_reactions(label_model)
     
     emu_dict0,label_model.experimental_dict =read_experimental_mid(label_model,mid_data_name,emu0_dict={},experimental_dict={},minimum_sd=p_dict["minimum_sd"])
     label_model.build(emu_dict0,force_balance=True,recompile_c_code=True,remove_impossible_emus=True,isotopic_steady_state=True,excluded_outputs_inputs=[],turnover_upper_bound=p_dict["turnover_upper_bound"],clear_intermediate_data=False,turnover_exclude_EX=p_dict["turnover_exclude_EX"])
     label_model.turnover_flux_dict["glc6p_pdif"]={"ub":1000,"lb":0,"v":500}
     label_model.turnover_flux_dict["pyr_pdif"]={"ub":1000,"lb":0,"v":500}
     label_model.turnover_flux_dict["gludxm"]={"ub":1000,"lb":0,"v":500}
     check_steady_state(label_model,only_initial_m0=True,threshold=1e-9)#Check initial dy for steady state deviations
     check_simulated_fractions(label_model) #Checks that the simulation can be succesfully run and that there are not negative or larger than 1 fractions
     
     #launch_gui(label_model)
     
     a,b=solver(label_model,mode="fsolve")
     get_objective_function(label_model,output=True)
     
     def test1(): solver(label_model,mode="fsolve")
     
     timeit(test1,number=1)
     #model=label_model.constrained_model=copy.deepcopy(label_model.metabolic_model)
     best_parameters=parameters=identify_free_parameters(label_model,parameter_dict={},fraction_of_optimum=fraction_of_optimum,change_threshold=p_dict["identify_free_parameters_change_threshold"],add_turnover=p_dict["identify_free_parameters_add_turnover"],parameter_precision=label_model.parameter_precision,n_samples=p_dict["identify_free_parameters_n_samples"])
     relative_max_sample=p_dict["annealing_relative_max_sample"]
     relative_min_sample=p_dict["annealing_relative_min_sample"]
     print p_dict
     max_random_sample=int(relative_max_sample*len(best_parameters))
     min_random_sample=int(relative_min_sample*len(best_parameters))
     for x in range(0,p_dict["annealing_iterations"]):
         best_parameters,best_flux_dict,f_best=annealing(label_model,max_random_sample=max_random_sample,min_random_sample=min_random_sample,n=p_dict["annealing_n"],m=p_dict["annealing_m"],p0=p_dict["annealing_p0"],pf=p_dict["annealing_pf"],parameter_precision=label_model.parameter_precision,max_perturbation=p_dict["annealing_max_perturbation"],      fraction_of_optimum=fraction_of_optimum,parameter_dict=best_parameters,n_processes=p_dict["annealing_n_processes"],output=True)
     parameters_to_evaluate=[]
     for paramater in parameters:
         if "turnover" not in paramater:
             parameters_to_evaluate.append(paramater)
     export_label_results(label_model,fn=("bestlabel_"+mid_data_name),show_chi=True)
     write_fva(label_model.constrained_model,fn="best_fluxes"+mid_data_name,fraction=1,remove0=False,change_threshold=0.001,mode="full",lp_tolerance_feasibility=1e-6)
     parameter_confidence_interval_dict,flux_confidence_interval_dict,chi_parameters_sets_dict=estimate_confidence_intervals(label_model,significance=p_dict["confidence_significance"],perturbation=p_dict["confidence_perturbation"],min_absolute_perturbation=p_dict["confidence_min_absolute_perturbation"],max_absolute_perturbation=p_dict["confidence_max_absolute_perturbation"],parameter_precision=label_model.parameter_precision,best_parameter_dict=best_parameters,parameter_list=parameters_to_evaluate,fraction_of_optimum=fraction_of_optimum,relative_max_random_sample=relative_max_sample, relative_min_random_sample= relative_min_sample,annealing_n=p_dict["annealing_n"],annealing_m=p_dict["annealing_m"],annealing_p0=p_dict["annealing_p0"],annealing_pf=p_dict["annealing_pf"],output=True,annealing_n_processes=p_dict["annealing_n_processes"],annealing_cycle_time_limit=p_dict["annealing_cycle_time_limit"], annealing_cycle_max_attempts=5,annealing_iterations=p_dict["annealing_iterations"],fname="confidence"+mid_data_name)
     