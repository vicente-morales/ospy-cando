# =============================================================================
# IDA Script: Analysis and Post-processing
# =============================================================================
import openseespy.opensees as ops
import numpy as np
import os
from funciones import Sa_spectral
from runNRHA3D import runNRHA3D
ops.wipe()

# Registros y factores
list_GM = ['GM_SURDEPERU2001_ARICA_COSTANERA_SN_5004_L.txt']
GM_names = []
dict_GM = {}
dict_dt = {}
dict_Npts = {}
folder_GM_id = os.path.join(os.getcwd(),'Registros')

for gm in range(len(list_GM)):
    GM_name = list_GM[gm].removeprefix('GM_').removesuffix('.txt')
    GM_names.append(GM_name)
    dict_GM[GM_name] = np.loadtxt(os.path.join(folder_GM_id,list_GM[gm]), ndmin = 2)
    data_fid = 'data' + list_GM[gm].removeprefix('GM')
    GM_fid = open(os.path.join(folder_GM_id,data_fid))
    GM_data = GM_fid.readlines()
    GM_fid.close()
    dict_dt[GM_name] = float(GM_data[5].strip().split()[2])
    dict_Npts[GM_name] = int(GM_data[6].strip().split()[1])

n_GM = len(dict_GM)
# IDA_factor = np.array([0.1, 0.5, 1]) # GM scaling
# n_factor = len(IDA_factor)

firstInt = 0.1   # This is the first intensity to run the elastic run (e.g. 0.05g)
incrStep = 0.1   # This is the increment used during the hunting phase (e.g. 0.10g)
maxRuns = int(5)  # This is the maximum number of runs to use (e.g. 20)


#%%
# =============================================================================
# Modal Analysis
# =============================================================================
exec(open("MODEL_01.py").read())
exec(open("Analysis_Modal_00.py").read())

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
# 1: Ground motion scaling
# Normalization of the  ground motion based on the first period of the structure 
# (as the selected IM is the Sa at T1)
# ScaleFactor = np.zeros((len(dict_GM),len(IDA_factor)))

# folder_IDA_id = os.path.join(os.getcwd(),'IDA')
# pflag = 1


# Open an error file that will log the IDA_HTF errors
error_log = open('IDA/IDA_HTF_error_log.txt', 'w')
error_log.write('^^^^^^^^ STARTING IDA HTF ^^^^^^^^')
# print('^^^^^^^^ STARTING IDA HTF ^^^^^^^^')


# Se recorren todos los registros
for i in range(n_GM):
    GM_name = GM_names[i]
    GM_log = open('IDA/log_Run_' + str(i) + '.txt',"w")
    dt = dict_dt[GM_name]
    npts = dict_Npts[GM_name]
    dur = npts * dt

    # Se debe comenzar definiendo los factores de escala considerando corrección por SaT1
    acclg = dict_GM[GM_name]
    Sa = Sa_spectral(T1, xi, acclg, dt)
    # dict_GM[GM_names[i]] = accIM / GM_Sa
    # ScaleFactor = IDA_factor / GM_Sa * 9.810665 # Para convertir el registro a m / s^2
    
    # Otros valores para el análisis
    j = 1
    IM = []  # Initialise the list of IM used for printing
    IMlist = []  # This is just a list that will be used in filling
    hFlag = 1  # Hunting flag (1 for when we're hunting)
    tFlag = 0  # Tracing flag (0 at first)
    fFlag = 0  # Filling flag (0 at first)
    # Tabla_IDA = open('IDA/Tabla_IDA_Record' + str(i) + '.txt', 'w')
    
    # Se recorren los valores para cada factor de escala
    while j <= maxRuns:
        # As long as the hunting flag is 1, meaning we havent reached a collapse
        if hFlag == 1:
            # Determine the intensity to run at during the hunting
            if j == 1:
                IM = np.append(IM, firstInt)
            else:
                IM = np.append(IM, IM[j - 2] + (j - 1) * incrStep)
            
            # Determine the scale factor that needs to be applied to the record
            sf = IM[j - 1] / Sa * 9.80665
            run = 'Record_' + str(i) + '_Run_' + str(j)  # This is a tag that outputs will be labelled with
            log = open('IDA/log_IDA_' + run + '.txt', 'w')
            
            # The hunting intensity has been determined, now we can analyse
            log.write("--- Generando modelo ---" + "\n")
            exec(open("MODEL_00.py").read())
            ops.rayleigh(alphaM, betaKcurr, betaKinit, betaKcomm)
            log.write("... Modelo generado .." + "\n")
            log.write("\n")
            
            log.write("--- Starting Gravity Analysis ---" + "\n")
            exec(open("Analysis_Gravity_00.py").read())
            log.write("--- Gravity Analysis Done ---" + "\n")
            log.write("\n")
            
            log.write("--- Starting RHA ---" + "\n")
            ops.timeSeries('Path', 2, '-dt', dt, '-filePath', list_GM[i], '-factor', sf)
            ops.pattern('UniformExcitation', 400, 1, '-accel', 2, '-factor', 1)
            cIndex, controlTime = runNRHA3D(dt, dur)
            if cIndex == -1:
                log.write('... ANALYSIS FAILED TO CONVERGE at ', controlTime, ' of ', dur, ' ...')
            if cIndex == 0:
                log.write('... ANALYSIS COMPLETED SUCCESSFULLY ...')
            log.write("\n")
            
            
            
          















error_log.close()

