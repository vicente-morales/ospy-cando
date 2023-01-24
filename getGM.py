from GM_Reader import GMReader_UCh_v2
from GM_Reader import GMReader_VDC_tar
import os

# Se generan todos los registros en la carpeta
list_GM = os.listdir('GM_Raw')
for gm in list_GM:
    if gm[-2:] == "v2":
        GMReader_UCh_v2([gm], in_dir='GM_Raw', out_dir='GM_Processed')
    elif gm[-3:] == 'tar':
        GMReader_VDC_tar([gm], ['VALPARAISO-1985'], in_dir='GM_Raw', out_dir='GM_Processed')

# Se seleccionan los archivos que se utilizan para el IDA -> descartar verticales
list_GM_tot = os.listdir('GM_Processed')
list_GM_IDA = []
fid = open('IDA/AA_selected_GM.txt', 'w')
for gm in list_GM_tot:
    if gm.find('_V.txt') == -1 and gm.find('GM_') != -1 and gm.find('_Z.txt') == -1:
        print(gm[3:-4], file=fid)
fid.close()

# Borrar la última linea en blanco
filename = 'IDA/AA_selected_GM.txt'
with open(filename) as f_input:
    data = f_input.read().rstrip('\n')
with open(filename, 'w') as f_output:    
    f_output.write(data)
