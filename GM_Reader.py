import numpy as np
import os

# GM from http://terremotos.ing.uchile.cl/
def GMReader_UCh_V2(filename_list, in_dir=os.getcwd(), out_dir=os.getcwd()):
    for filename in filename_list:
        file = open(os.path.join(in_dir, filename), "r")
        lineas = file.readlines()
        file.close()
        n_lineas = len(lineas)
        evento = lineas[2].strip()
        canales_str = lineas[5].split()
        num_canales = min(int(canales_str[7].strip()[-1]), 3)
        # num_canales = int(lineas[5].split()[7].strip()[-1])
        estacion = lineas[6].strip()
        
        i = 0
        for canal in range(num_canales):
            direccion_linea = lineas[7+i].strip().split()
            num_canal = int(direccion_linea[1].strip()[0])
            direccion = direccion_linea[2]
            duracion_linea = lineas[11+i].strip().split()
            try:
                duracion = float(duracion_linea[-2])
            except ValueError:
                duracion = float(duracion_linea[-2][1:])
            timestep = float(lineas[16+i].strip().split()[4])
            n_puntos = int(round(duracion / timestep))
            
            data_txt_name = "data_" + evento.replace(" ","") + "_" + estacion.replace(
                " ","_") + "_" + direccion + ".txt"
            data_txt_name = os.path.join(out_dir, data_txt_name.replace("/",""))
            data = open(data_txt_name,'w+')

            data.write("Evento:" + " " + evento + "\n")
            data.write("Estación:" + " " + estacion + "\n")
            data.write("Canal:" + " " + str(num_canal) + "\n")
            data.write("Direccion:" + " " + direccion + "\n")
            data.write("Duración:" + " " + str(duracion) + "\n")
            data.write("Time Step:" + " " + str(timestep) + "\n")
            data.write("Puntos:" + " " + str(n_puntos) + "\n")
            data.close()
            
            i += 45
            linea = lineas[i].strip().split()
            acc = np.zeros(int(linea[0]))
            i += 1
            linea = lineas[i].strip().split()
            j = 0
            error = False
            while error == False:
                try:
                    elems = np.array(linea,dtype=float)
                except ValueError:
                    error = True
                    break
                num_elem = len(elems)
                for n in range(num_elem):
                    acc[j+n] = elems[n]
                j += num_elem
                i += 1
                if i <= n_lineas:
                    linea = lineas[i].strip().split()
            GM_txt_name = "GM_" + evento.replace(" ","") + "_" + estacion.replace(
                " ","_") + "_" + direccion + ".txt"
            GM_txt_name = os.path.join(out_dir, GM_txt_name.replace("/",""))
            np.savetxt(GM_txt_name, acc, newline=" ")
            # np.savetxt(GM_txt_name,acc.reshape(1, acc.shape[0]))
            
            vel = np.zeros(int(linea[0]))
            i += 1
            linea = lineas[i].strip().split()
            j = 0
            error = False
            while error == False:
                try:
                    elems = np.array(linea,dtype=float)
                except ValueError:
                    error = True
                    break
                num_elem = len(elems)
                for n in range(num_elem):
                    vel[j+n] = elems[n]
                j += num_elem
                i += 1
                if i <= n_lineas:
                    linea = lineas[i].strip().split()
            
            disp = np.zeros(int(linea[0]))
            i += 1
            linea = lineas[i].strip().split()
            j = 0
            error = False
            while error == False and linea[0] != "/&":
                try:
                    elems = np.array(linea,dtype=float)
                except ValueError:
                    error = True
                    break
                num_elem = len(elems)
                for n in range(num_elem):
                    disp[j+n] = elems[n]
                j += num_elem
                i += 1
                if i <= n_lineas:
                    linea = lineas[i].strip().split()
            i += 1


# GM from https://www.strongmotioncenter.org/vdc/scripts/default.plx                                
def GMReader_VDC_tar(filename_list, event_names, in_dir=os.getcwd(), out_dir=os.getcwd()):
    for n in range(len(filename_list)):
        file = open(os.path.join(in_dir, filename_list[n]), "r")
        lineas = file.readlines()
        file.close()
        n_lineas = len(lineas)
        evento = event_names[n]

        i = 0
        end = False         
        while end != True:        
            linea_est_dir = lineas[i + 1].strip().split(',')
            estacion = linea_est_dir.strip()
            direccion = linea_est_dir[2].strip().
        


            direccion_linea = lineas[7+i].strip().split()
            num_canal = int(direccion_linea[1].strip()[0])
            direccion = direccion_linea[2]
            duracion_linea = lineas[11+i].strip().split()
            try:
                duracion = float(duracion_linea[-2])
            except ValueError:
                duracion = float(duracion_linea[-2][1:])
            timestep = float(lineas[16+i].strip().split()[4])
            n_puntos = int(round(duracion / timestep))
            
            data_txt_name = "data_" + evento.replace(" ","") + "_" + estacion.replace(
                " ","_") + "_" + direccion + ".txt"
            data_txt_name = os.path.join(out_dir, data_txt_name.replace("/",""))
            data = open(data_txt_name,'w+')

            data.write("Evento:" + " " + evento + "\n")
            data.write("Estación:" + " " + estacion + "\n")
            data.write("Canal:" + " " + str(num_canal) + "\n")
            data.write("Direccion:" + " " + direccion + "\n")
            data.write("Duración:" + " " + str(duracion) + "\n")
            data.write("Time Step:" + " " + str(timestep) + "\n")
            data.write("Puntos:" + " " + str(n_puntos) + "\n")
            data.close()
            
            i += 45
            linea = lineas[i].strip().split()
            acc = np.zeros(int(linea[0]))
            i += 1
            linea = lineas[i].strip().split()
            j = 0
            error = False
            while error == False:
                try:
                    elems = np.array(linea,dtype=float)
                except ValueError:
                    error = True
                    break
                num_elem = len(elems)
                for n in range(num_elem):
                    acc[j+n] = elems[n]
                j += num_elem
                i += 1
                if i <= n_lineas:
                    linea = lineas[i].strip().split()
            GM_txt_name = "GM_" + evento.replace(" ","") + "_" + estacion.replace(
                " ","_") + "_" + direccion + ".txt"
            GM_txt_name = os.path.join(out_dir, GM_txt_name.replace("/",""))
            np.savetxt(GM_txt_name, acc, newline=" ")
            # np.savetxt(GM_txt_name,acc.reshape(1, acc.shape[0]))
            
            vel = np.zeros(int(linea[0]))
            i += 1
            linea = lineas[i].strip().split()
            j = 0
            error = False
            while error == False:
                try:
                    elems = np.array(linea,dtype=float)
                except ValueError:
                    error = True
                    break
                num_elem = len(elems)
                for n in range(num_elem):
                    vel[j+n] = elems[n]
                j += num_elem
                i += 1
                if i <= n_lineas:
                    linea = lineas[i].strip().split()
            
            disp = np.zeros(int(linea[0]))
            i += 1
            linea = lineas[i].strip().split()
            j = 0
            error = False
            while error == False and linea[0] != "/&":
                try:
                    elems = np.array(linea,dtype=float)
                except ValueError:
                    error = True
                    break
                num_elem = len(elems)
                for n in range(num_elem):
                    disp[j+n] = elems[n]
                j += num_elem
                i += 1
                if i <= n_lineas:
                    linea = lineas[i].strip().split()
            i += 1
