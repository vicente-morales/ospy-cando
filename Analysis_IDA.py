# =============================================================================
# IDA Script: Analysis and Post-processing
# =============================================================================
import openseespy.opensees as ops
import numpy as np
from getSa import getSa
from MODEL import build_model
from Analysis_Modal import modal_analysis
from Analysis_Gravity import gravity_analysis
from runNRHA2D import runNRHA2D
from datetime import datetime

ops.wipe()

#%%
# =============================================================================
# Registros
# =============================================================================
# Se cargan los registros y su información
# Unidades de registros: cm/s/s
GM_names = []
dict_GM = {}
# dict_dt = {}
# dict_Npts = {}

# Se almacena la info de los registros con los que se trabajará
fid_GM = open('IDA/AA_selected_GM.txt', 'r')
registros = fid_GM.readlines()
for gm in range(len(registros)):
    GM_name = registros[gm].strip()
    GM_names.append(GM_name)
    # dict_GM[GM_name] = np.loadtxt('Processed_GM/GM_' + GM_name + '.txt', ndmin=2)
    fid_data = open('GM_Processed/data_' + GM_name + '.txt', 'r')
    GM_data = fid_data.readlines()
    fid_data.close()
    # dict_dt[GM_name] = float(GM_data[5].strip().split()[2])
    # dict_Npts[GM_name] = int(GM_data[6].strip().split()[1])
    dict_GM[GM_name] = {'acc': np.loadtxt('GM_Processed/acc_' + GM_name + '.txt', ndmin=2), 
                        'dt': float(GM_data[5].strip().split()[2]), 
                        'Npts': int(GM_data[6].strip().split()[1])}
fid_GM.close()
n_GM = len(dict_GM)


#%%
# =============================================================================
# Modal Analysis
# =============================================================================
numStories, Hstory, Htotal, WallElPerStory, ListNodes, ListNodesBasal, ListNodesDrift, \
    IDctrlNode, IDctrlDOF, dict_mats, tags_conc, tags_steel, tags_shear, tags_walls, tags_beams, \
        tags_cols, dict_elems, dict_walls_floor = build_model()
T1, T2, omega1, omega2 = modal_analysis()

# Define critical damping and Switchs
xDamp = 0.02
MpropSwitch = 1.0
KcurrSwitch = 1.0
KcommSwitch = 0.0
KinitSwitch = 0.0
omegaI = 2 * np.pi / (0.2 * T1)
omegaJ = 2 * np.pi / (1.5 * T1)

# Calculate proportionality factors for Rayleigh damping
alphaM = MpropSwitch * xDamp * (2 * omegaI * omegaJ) / (omegaI + omegaJ)
betaKcurr = KcurrSwitch * 2 * xDamp / (omegaI + omegaJ)
betaKcomm = KcommSwitch * 2 * xDamp / (omegaI + omegaJ) 
betaKinit = KinitSwitch * 2 * xDamp / (omegaI + omegaJ) 

# Otros
xi = 0.05
# xi1 = 0.02
# xi2 = 0.02
# a0 = 2 * (omega1 * omega2 * (omega2 * xi1 - omega1 * xi2)) / (omega2**2 - omega1**2)
# a1 = 2 * (omega2 * xi2 - omega1 * xi1) / (omega2**2 - omega1**2)


#%%
# =============================================================================
# Incremental Dynamic Analisis
# =============================================================================
# Resultados de interés
time_start = datetime.now()
time_actual = datetime.now()

# Se definen los valores de la IM que se eligirán
firstInt = 0.1   # This is the first intensity to run the elastic run (e.g. 0.05g)
incrStep = 0.1   # This is the increment used during the hunting phase (e.g. 0.10g)
maxRuns = int(20)  # This is the maximum number of runs to use (e.g. 20)

# Se recorren todos los registros
for i in range(n_GM):
    GM_name = GM_names[i]
    acc_GM = dict_GM[GM_name]['acc'].flatten().tolist()
    log_GM = open('IDA/log_Record_' + "{:02d}".format(i + 1) + '.txt',"w")
    log_GM.write('^^^^^^^^^^ STARTING IDA HTF ^^^^^^^^^^\n')
    log_GM.write('-> Registro: ' + GM_name + "\n")
    log_GM.write("\n")
    dt = dict_GM[GM_name]['dt']
    npts = dict_GM[GM_name]['Npts']
    dur = npts * dt

    # Se debe comenzar definiendo los factores de escala considerando corrección por SaT1
    acclg = dict_GM[GM_name]['acc']
    Sa = getSa(T1, xi, acclg, dt)
    IM = [] # Initialise the list of IM used for printing
    IMlist = []  # This is just a list that will be used in filling
    drift_roof_max = []

    # Set up the initial indices for HTF
    j = 1
    hFlag = 1  # Hunting flag (1 for when we're hunting)
    tFlag = 0  # Tracing flag (0 at first)
    fFlag = 0  # Filling flag (0 at first)    
    
    # Se recorren los valores para cada factor de escala
    while j <= maxRuns:
        
        # As long as the hunting flag is 1, meaning we havent reached a collapse
        if hFlag == 1:
            
            # Determine the intensity to run at during the hunting
            if j == 1:
                IM = np.append(IM, firstInt)
            else:
                # The variation will be incremented in each step in order to force the collapse
                # IM = np.append(IM, round(IM[j - 2] + (j - 1) * incrStep, 4))
                IM = np.append(IM, round(IM[j - 2] + incrStep, 4))
                
            log_GM.write("########## STARTING RUN #" + str(j) + " ##########\n")
            log_GM.write('-> IM: ' + str(IM[j - 1]) + "\n")
            
            # Determine the scale factor that needs to be applied to the record
            sf = IM[j - 1] / Sa * 9.80665
            
            # The hunting intensity has been determined, now we can analyse
            # This is a tag that outputs will be labelled with
            run = 'Record_' + "{:02d}".format(i + 1) + '_Run_' + "{:02d}".format(j)  
            log_run = open('IDA/log_' + run + '.txt', 'w')
            log_run.write("########## STARTING RUN #" + str(j) + " ##########\n")
            log_run.write('-> IM: ' + str(IM[j - 1]) + "\n")
            log_run.write("\n")
            
            # Modelo
            build_model()
            log_run.write("-> Creating Model\n")
            log_GM.write("-> Creating Model\n")
            ops.logFile('IDA/log_' + run + '.txt', '-noEcho')
            ops.rayleigh(alphaM, betaKcurr, betaKinit, betaKcomm)
            # log_run.write("... Modelo generado\n")
            # log_run.write("\n")
            
            # Se comienza aplicando las cargas gravitacionales
            log_run.write("-> Starting Gravity Analysis\n")
            log_GM.write("-> Starting Gravity Analysis\n")
            gravity_analysis()
            # log_run.write("... Gravity Analysis Done\n")
            # log_run.write("\n")
            
            # Ahora se corre el RHA
            log_run.write("-> Starting RHA\n")
            log_GM.write("-> Starting RHA\n")
            # ops.timeSeries('Path', 2, '-dt', dt, '-filePath','Processed_GM/GM_' + GM_name + '.txt', 
            #                '-factor', sf)
            ops.timeSeries('Path', 2, '-dt', dt, '-values', *acc_GM, '-factor', sf)
            ops.pattern('UniformExcitation', 400, 1, '-accel', 2, '-fact', 1)
            cIndex, controlTime, max_drift_techo \
                = runNRHA2D(dt, dur, ListNodesDrift, dict_elems, tags_walls, dict_walls_floor, 
                          WallElPerStory, dict_mats)
            # j += 1
            
            # Check for convergence
            if cIndex == -1:
                log_run.write('-> RHA Analysis Failed to Converge at ' + str(controlTime) + 's of '
                              + str(dur) + 's\n')
                log_GM.write('-> WARNING: RHA Analysis Failed to Converge at ' + str(controlTime)
                             + 's of ' + str(dur) + '\n')
            else:
                log_run.write('-> RHA Analysis Completed Successfully\n')
                log_run.write('\n')
            
            # Check the hunted run for collapse
            if cIndex in [1, 2]:
                # log_GM.write('-> Collapse was found with IM = '+ str(IM[j - 2]) +': tracing lower IM\n')
                log_GM.write('-> Collapse ('+ str(cIndex) +') was found at ' + str(controlTime)
                             + 's of ' + str(dur) + 's : tracing lower IM\n')
                # log_run.write('-> Collapse was found: tracing lower IM\n')
                log_run.close()
                hFlag = 0  # Stop hunting
                tFlag = 1  # Start tracing
                # j -= 1  # Reduce by 1 because j was increased before and we want to redo that point
                jhunt = j  # The value of j we hunted to
                if jhunt == 2:
                    log_GM.write('-> WARNING: Collapsed achieved on first increment, reduce increment\n')
                log_GM.write('\n')
            else:
                drift_roof_max.append(max_drift_techo)
                log_run.write('-> DT: ' + str(max_drift_techo) + '\n')
                log_run.write("########## END OF RUN #" + str(j) + " ##########\n")
                log_run.close()
                log_GM.write('-> DT: ' + str(max_drift_techo) + '\n')
                log_GM.write("########## END OF RUN #" + str(j) + " ##########\n")
                log_GM.write('\n')
                j += 1


        # When the first collapse is reached, we start tracing between last convergence and the first collapse
        # The idea is to try to get a little closer to collapse 
        if tFlag == 1 and j <= maxRuns:
            # The first phase is to trace the last DeltaIM to get within the resolution
            if j == jhunt:
                firstC = IM[j - 1]  # This is the IM of the hunting collapse
                IM = IM[:-1]  # Remove that value of IM from the array (it's already been appended)
            if j == 1:
                diff = firstC
            else:
                diff = firstC - IM[j - 2]  # Difference between the noncollapse and collapse IM
            
            delta_IM_tr = max([0.2 * diff, 0.025]) # Take 0.2 of the difference, 
            # Place a lower threshold on the increment so it doesnt start tracing too fine
            
            # Calculate new tracing IM, which is previous noncollapse plus increment
            if j == 1:
                IMtr = round(delta_IM_tr, 4)
            else:
                IMtr = round(IM[j - 2] + delta_IM_tr, 4) 
            IM = np.append(IM, IMtr)
            sf = IMtr / Sa * 9.80665
            
            if j != jhunt:
                log_GM.write("########## STARTING RUN #" + str(j) + " ##########\n")
            
            # The trace intensity has been determined, now we can analyse
            log_GM.write('-> IM: ' + str(IMtr) + "\n")
            run = 'Record_' + "{:02d}".format(i + 1) + '_Run_' + "{:02d}".format(j)
            log_run = open('IDA/log_' + run + '.txt', 'w')
            log_run.write("##### STARTING RUN #" + str(j) + " #####\n")
            log_run.write('-> IM: ' + str(IMtr) + "\n")
            log_run.write("\n")
            
            # Modelo
            build_model()
            log_run.write("-> Creating Model\n")
            log_GM.write("-> Creating Model\n")
            ops.logFile('IDA/log_' + run + '.txt', '-noEcho')
            ops.rayleigh(alphaM, betaKcurr, betaKinit, betaKcomm)
            # log_run.write("... Modelo generado\n")
            # log_run.write("\n")
            
            # Se comienza aplicando las cargas gravitacionales
            log_run.write("-> Starting Gravity Analysis\n")
            log_GM.write("-> Starting Gravity Analysis\n")
            gravity_analysis()
            # log_run.write("... Gravity Analysis Done\n")
            # log_run.write("\n")
            
            # Ahora se corre el RHA
            log_run.write("-> Starting RHA\n")
            log_GM.write("-> Starting RHA\n")
            ops.timeSeries('Path', 2, '-dt', dt, '-values', *acc_GM, '-factor', sf)
            ops.pattern('UniformExcitation', 400, 1, '-accel', 2, '-fact', 1)
            cIndex, controlTime, max_drift_techo \
                = runNRHA2D(dt, dur, ListNodesDrift, dict_elems, tags_walls, dict_walls_floor, 
                          WallElPerStory, dict_mats)           

            # Check for convergence
            if cIndex == -1:
                log_run.write('-> RHA Analysis Failed to Converge at ' + str(controlTime) + 's of '
                              + str(dur) + 's\n')
                log_GM.write('-> WARNING: RHA Analysis Failed to Converge at ' + str(controlTime)
                             + 's of ' + str(dur) + 's\n')
            else:
                log_run.write('-> RHA Analysis Completed Successfully\n')
                log_run.write('\n')
            
            # Check the hunted run for collapse
            if cIndex in [1, 2]:
                # Not sure if this is the best way, to just trace back up to collapse again
                log_GM.write('-> Collapse ('+ str(cIndex) +') was found at ' + str(controlTime)
                             + 's of ' + str(dur) + 's : starting filling IM\n')
                tFlag = 0  # Stop tracing
                fFlag = 1  # Start filling
                jtrace = j  # The value of j we hunted to
                IMlist = IM  # Get the list of IMs
                if j == jhunt:
                    log_GM.write('-> WARNING: First trace for collapse resulted in collapse\n')
            
            # All the runs need to be accounted for, even if its a collapse
            drift_roof_max.append(max_drift_techo)
            log_run.write('-> DT: ' + str(max_drift_techo) + '\n')
            log_run.write("########## END OF RUN #" + str(j) + " ##########\n")
            log_run.close() 
            log_GM.write('-> DT: ' + str(max_drift_techo) + '\n')   
            log_GM.write("########## END OF RUN #" + str(j) + " ##########\n")
            log_GM.write('\n') 
            j += 1 
            
        
        # When the required resolution is reached, we start filling
        # The available runs are used to fill in the biggest gaps in the intensity steps
        if fFlag == 1 and j <= maxRuns:
            # if j == jtrace + 1: # Aumentamos j+=1 al final del tracing
            #     log_GM.write("##### STARTING FILLING ##### \n")
            #     log_GM.write('\n') 
            
            # Reorder the list so we can account for filled runs
            IMlist = np.sort(IMlist)
            
            # Determine the biggest gap in IM for the hunted runs
            gap = 0.0       
            
            # We go to the end of the list minus 1 because, 
            # if not we would be filling between a noncollapsing and a collapsing run
            for ii in range(len(IMlist) - 1):
                temp = IMlist[ii] - IMlist[ii - 1]
                if temp > gap:
                    gap = temp # Update to maximum gap
                    IMfil = round(IMlist[ii - 1] + gap / 2, 4)  # Determine new filling IM
            
            # Generates new IM and scale factor to analyze
            IM = np.append(IM, IMfil)
            IMlist = np.append(IMlist, IMfil)
            sf = IMfil / Sa * 9.80665
            
            # The trace intensity has been determined, now we can analyse
            log_GM.write("########## STARTING RUN #" + str(j) + " ##########\n")
            log_GM.write('-> IM: ' + str(IMfil) + "\n")
            
            run = 'Record_' + "{:02d}".format(i + 1) + '_Run_' + "{:02d}".format(j)
            log_run = open('IDA/log_' + run + '.txt', 'w')
            log_run.write("########## STARTING RUN #" + str(j) + " ##########\n")
            log_run.write('-> IM: ' + str(IMfil) + "\n")
            log_run.write("\n")
            
            # Modelo
            build_model()
            log_run.write("-> Creating Model\n")
            log_GM.write("-> Creating Model\n")
            ops.logFile('IDA/log_' + run + '.txt', '-noEcho')
            ops.rayleigh(alphaM, betaKcurr, betaKinit, betaKcomm)
            # log_run.write("... Modelo generado\n")
            # log_run.write("\n")
            
            # Se comienza aplicando las cargas gravitacionales
            log_run.write("-> Starting Gravity Analysis\n")
            log_GM.write("-> Starting Gravity Analysis\n")
            gravity_analysis()
            # log_run.write("... Gravity Analysis Done\n")
            # log_run.write("\n")
            
            # Ahora se corre el RHA
            log_run.write("-> Starting RHA\n")
            log_GM.write("-> Starting RHA\n")
            ops.timeSeries('Path', 2, '-dt', dt, '-values', *acc_GM, '-factor', sf)
            ops.pattern('UniformExcitation', 400, 1, '-accel', 2, '-fact', 1)
            cIndex, controlTime, max_drift_techo \
                = runNRHA2D(dt, dur, ListNodesDrift, dict_elems, tags_walls, dict_walls_floor, 
                          WallElPerStory, dict_mats)           
            j += 1
            
            # Check for convergence
            if cIndex == -1:
                log_run.write('-> RHA Analysis Failed to Converge at ' + str(controlTime) + 's of '
                              + str(dur) + 's\n')
                log_GM.write('-> WARNING: RHA Analysis Failed to Converge at ' + str(controlTime)
                             + 's of ' + str(dur) + 's\n')
            else:
                log_run.write('-> RHA Analysis Completed Successfully\n')
                log_run.write('\n')
            
            # Save info
            drift_roof_max.append(max_drift_techo)
            log_run.write('-> DT: ' + str(max_drift_techo) + "\n")
            log_run.write("########## END OF RUN #" + str(j) + " ##########\n")
            log_run.close() 
            log_GM.write('-> DT: ' + str(max_drift_techo) + "\n")
            log_GM.write("########## END OF RUN #" + str(j) + " ##########\n")
            log_GM.write('\n') 

        # Wrap it up and finish
        if j == maxRuns + 1:
            if hFlag == 1:
                log_GM.write('-> WARNING: Collapse not achieved, increase increment or number of runs\n')
                log_GM.write('\n')
            elif fFlag == 0:
                log_GM.write(
                    '-> WARNING: No filling, algorithm still tracing for collapse (increase runs)\n')
                log_GM.write('\n')

    # Time
    time_GM = datetime.now() - time_actual
    time_actual = datetime.now()
    time_elapsed = time_actual - time_start
    # print('RUN ' + str(i+1) + ' DONE')
    # print('Run Analysis time (hh:mm:ss.ms) {}'.format(time_GM))
    # print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
    
    # End of analysis of one GM
    log_GM.write('-> Run analysis time (hh:mm:ss.ms) {}'.format(time_GM) + "\n")
    log_GM.write('-> Total time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed) + "\n")
    log_GM.write('\n')
    log_GM.write('^^^^^^^^^^ FINISHED IDA HTF ^^^^^^^^^^')
    log_GM.close()
    dict_GM[GM_name]['IM'] = IM
    dict_GM[GM_name]['drift_roof_max'] = drift_roof_max
    np.savetxt('IDA/results_Run_' + "{:02d}".format(i + 1) + '.txt', np.vstack((IM,drift_roof_max)))
    

# time_elapsed = datetime.now() - start_time
# print()
# print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))

