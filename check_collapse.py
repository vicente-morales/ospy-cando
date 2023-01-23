import openseespy.opensees as ops
import numpy as np

def check_collapse(ListNodesDrift, dict_elems, tags_walls, dict_walls_floor, WallElPerStory,
                   dict_mats):
    cIndex = 0  # Initially define the control index 
    # (0 for stable, 1 for global collapse, 2 for local collapse)
    
    # Drift limits
    RDC = 0.05
    # IDC = 0.005
    
    # Global collapse due to excesive roof displacement (axial wall failure)
    # Lista de nodos de drift debe estar en orden ascendente
    h_tot = np.amax(ListNodesDrift, axis=0)[-1]
    roof_node = int(ListNodesDrift[ListNodesDrift[:,2] == h_tot][:,0][0])
    roof_disp = ops.nodeDisp(roof_node, 1)
    if abs(roof_disp / h_tot) > RDC:
        cIndex = 1
    
    # # Local collapse due to excessive interstory drift
    # max_drift_piso = np.zeros([len(ListNodesDrift),1])
    # max_drift_tot = 0
    # piso = 0
    # for (nod_ini, nod_end) in zip(ListNodesDrift[:-1, 0], ListNodesDrift[1:, 0]):
    #     nod_ini = int(nod_ini)
    #     nod_end = int(nod_end)
    #     pos_i = ops.nodeCoord(nod_ini, 2)
    #     pos_s = ops.nodeCoord(nod_end, 2)
    #     hpiso = pos_s - pos_i
    #     desp_i = ops.nodeDisp(nod_ini, 1)
    #     desp_s = ops.nodeDisp(nod_end, 1)
    #     desp_piso = abs(desp_s - desp_i)
    #     drift_piso = desp_piso / hpiso
        
    #     # Se guarda el máximo y se revisa el colapso
    #     max_drift_piso[piso][0] = max(max_drift_piso[piso][0], drift_piso)
    #     max_drift_tot = max(max_drift_tot, drift_piso)
    #     if max_drift_tot > IDC and cIndex == 0:
    #         cIndex = 2
    #     piso += 1
            
    # Local collapse due to the failure of at least 50% of a floor's walls
    if cIndex == 0:
        for story_walls in list(dict_walls_floor.values()):
            fallas = 0
            for tag_wall in story_walls:
                # Si falla una discretización del muro, falla el muro completo
                fallas += WallElPerStory * check_wall(tag_wall, dict_elems, dict_mats)
            if fallas >= np.floor(len(story_walls)/2):
                cIndex = 2
                break
    
    return cIndex, roof_disp
    # return cIndex, roof_disp, max_drift_tot, max_drift_piso


def check_wall(tag_wall, dict_elems, dict_mats):
    wall = dict_elems[tag_wall]
    mat_strain_limit = [dict_mats[wall['-matConcrete'][0]]['epsU'], 
                        dict_mats[wall['-matConcrete'][-1]]['epsU']]
    strains = ops.eleResponse(tag_wall,'Fiber_Strain')
    wall_lat_strains = [strains[0], strains[-1]]
    
    falla = 0
    
    # Falla por fractura del acero en tracción
    if wall_lat_strains[0] > 0.05 or wall_lat_strains[1] > 0.05:
        falla = 1
    # Falla por pandeo del acero o aplastamiento del hormigón:
    elif wall_lat_strains[0] < mat_strain_limit[0] or wall_lat_strains[1] < mat_strain_limit[1]:
        falla = 1
    
    return falla
    
    
