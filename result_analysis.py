import numpy as np  
import matplotlib.pylab as plt  
import os

# Se cargan los resultados
results_folder = "IDA/Results"
file_list = os.listdir(results_folder)
GM_names = []
dict_GM = {}
fid_GM = open('IDA/AA_selected_GM.txt', 'r')
registros = fid_GM.readlines()
for gm in range(len(registros)):
    GM_name = registros[gm].strip()
    GM_names.append(GM_name)
    result_data = np.loadtxt(open(results_folder + "/" + file_list[gm], 'r'))
    result_data = np.transpose(np.transpose(result_data)[result_data[0,:].argsort()]) # Ordenarlos de forma ascendente
    # dict_GM[GM_name] = {"IM": result_data[0,:], "drift": result_data[1,:] / 52 * 100}
    dict_GM[GM_name] = {"IM": result_data[0,:], "drift": result_data[1,:]}
fid_GM.close()


# Se corta la curva donde ocurre no convergencia
cortar = [9, 14, 20,]


# Se genera una curva para cada sismo
plt.figure()
# plt.axes().set_aspect('equal')
for gm in dict_GM.keys():
    plt.plot(dict_GM[gm]["drift"], dict_GM[gm]["IM"], label=str(gm))
plt.show()

