# =============================================================================
# INCREMENTAL DINAMIC ANALYSIS
# =============================================================================
import openseespy.opensees as ops
import numpy as np
import os


# =============================================================================
# Iniciales
# =============================================================================
ops.wipe()

# Factores de escala para el IDA
# IDA_factors = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75,
#                0.8, 0.85, 0.9, 0.95, 1]
IDA_factor = [0.1, 0.5, 1]

# Datos del sismo a ingresar
GM_file = ['GM_SURDEPERU2001_ARICA_COSTANERA_SN_5004_L.txt']
GM_dt = [0.005]
GM_NP = [15236]
GM_SaT1 = [163.941]

# Crea carpeta para guardar resultados
parent_dir = os.getcwd()
out_dir = "OUT"
out_path = os.path.join(parent_dir, out_dir)
try:
    os.mkdir(out_path)
except FileExistsError:
    None
    
# Crear archivo con info de la corrida
log_file_name = "LOG_" + GM_file
log_file = open(os.path.join(out_path, log_file_name),'w+')
log_file.write("IDA factors............ " + IDA_factor + '\n')
log_file.write("Registro............ " + GM_file + '\n')
log_file.write("Incremento de tiempo............ " + GM_dt + '\n')
log_file.write("Número de puntos............ " + GM_NP + '\n')
log_file.write("SaT1............ " + GM_SaT1)
log_file.close()

# Se deben recorrer todos los factores del IDA
ok_IDA = 0
for i in range(len(GM_file)):
    GMfile = GM_file[i]
    DtSeries = GM_dt[i]
    NSteps = GM_NP[i]
    SaT1 = GM_SaT1[i]
    ok_GM = 0
    numNoConv = 0
    # for IDA_SF in IDA_factor:
        
        
