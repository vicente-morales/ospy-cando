# =============================================================================
# Build model
# =============================================================================
import openseespy.opensees as ops
import numpy as np

def build_model():
    ops.wipe()
    ops.model('basic', '-ndm', 2, '-ndf', 3)
    
    # =============================================================================
    # Define Building Geometry
    # =============================================================================
    # Units: MPa, MN, m, sec
    
    # Vertical geometry
    numStories = 20
    Hstory = 2.6 # Story height
    Htotal = numStories * Hstory # Total building height
    WallElPerStory = 2
    
    # Horizontal geometry
    Lw1 = 6.5 # Length wall axis 1
    Lw2_Yt = 2.575 # Centroid position
    Lw3 = 3.5 # Length wall axis 2
    Lpas = 2.0 # Length corridor axes 1 and 3
    Lpas2 = 1.7 # Length corridor axis 2
    Ldep = 1.5 # Length corridor in apartment
    Lsep = 10.0 # Length between frames
    LineaCol5 = Lw1 + Lpas + Lsep # Columna line 5, coordinate x
    LineaCol9 = LineaCol5 + 2.0 * Lw2_Yt + Lpas2 + Lsep # Columna line 9, coordinate x
    
    # Define floor masses
    Mcub = 0.2391
    Ment = 0.2482
    Negligible = 1.0 * 10**(-9)
    
    ListNodes, ListNodesBasal, ListNodesDrift, IDctrlNode, IDctrlDOF = define_nodes(
        numStories, Hstory, WallElPerStory, Lw1, Lpas, LineaCol5, Lw2_Yt, Lpas2, LineaCol9, Lw3, 
        Ldep, Ment, Mcub, Negligible)
    
    conc_tags, steel_tags, shear_tags, Ec_uc = define_materials()
    tags_walls, tags_beams, tags_cols, dict_elems, dict_walls_floor \
        = define_sections(numStories, WallElPerStory, Ec_uc, conc_tags, steel_tags, shear_tags)
    define_gravity_loads(numStories, WallElPerStory)
    
    return numStories, Hstory, Htotal, WallElPerStory, ListNodes, ListNodesBasal, ListNodesDrift, \
        IDctrlNode, IDctrlDOF, tags_walls, tags_beams, tags_cols, dict_elems, dict_walls_floor


#%%
# =============================================================================
# Define nodes, fixes, constrains, and assign masses
# =============================================================================

def define_nodes(numStories, Hstory, WallElPerStory, Lw1, Lpas, LineaCol5, Lw2_Yt, Lpas2, LineaCol9,
                 Lw3, Ldep, Ment, Mcub, Negligible):
    # Node List
    ListNodes = []
    
    # Nodos de la base
    ListNodes.append([100, 0.0, 0.0]) # Linea de columna 1 
    ListNodes.append([400, Lw1 + Lpas, 0.0]) # Linea de columna 4
    ListNodes.append([500, LineaCol5, 0.0]) # Linea de columna 5
    ListNodes.append([800, LineaCol5 + 2 * Lw2_Yt + Lpas2, 0.0]) # Linea de columna 8
    ListNodes.append([900, LineaCol9, 0.0]) # Linea de columna 9
    ListNodes.append([1100, LineaCol9 + Lw3/2 + Ldep, 0.0]) # Linea de columna 11
    ListNodes.append([1200, LineaCol9 + Lw3/2 + Ldep + Lpas, 0.0]) # Linea de columna 12
    ListNodes.append([1400, LineaCol9 + Lw3 + 2 * Ldep + Lpas, 0.0]) # Linea de columna 14
    
    # Genera nodos piso por piso
    NodesPerStory = WallElPerStory - 1
    for piso in range(1, numStories + 1):
        # Crear nodos intermedios del entrepiso
        for nodo in range(1, NodesPerStory + 1):
            node_tag1 = nodo + WallElPerStory * (piso - 1)
            y_pos = nodo * Hstory / WallElPerStory + (piso - 1) * Hstory
            ListNodes.append([100 + node_tag1, 0.0, y_pos])
            ListNodes.append([400 + node_tag1, Lw1 + Lpas, y_pos])
            ListNodes.append([500 + node_tag1, LineaCol5, y_pos])
            ListNodes.append([800 + node_tag1, LineaCol5 + 2*Lw2_Yt + Lpas2, y_pos])
            ListNodes.append([900 + node_tag1, LineaCol9, y_pos])
            ListNodes.append([1400 + node_tag1, LineaCol9 + Lw3 + 2*Ldep + Lpas, y_pos])
    
        # Crear nodos de piso
        node_tag2 = WallElPerStory * piso
        node_tag3 = piso
        y_pos = piso * Hstory
        ListNodes.append([100 + node_tag2, 0.0, y_pos])
        ListNodes.append([400 + node_tag2, Lw1 + Lpas, y_pos])
        ListNodes.append([500 + node_tag2, LineaCol5, y_pos])
        ListNodes.append([800 + node_tag2, LineaCol5 + 2*Lw2_Yt + Lpas2, y_pos])
        ListNodes.append([900 + node_tag2, LineaCol9, y_pos])
        ListNodes.append([1100 + node_tag3, LineaCol9 + Lw3/2 + Ldep, y_pos])
        ListNodes.append([1200 + node_tag3, LineaCol9 + Lw3/2 + Ldep + Lpas, y_pos])
        ListNodes.append([1400 + node_tag2, LineaCol9 + Lw3 + 2*Ldep + Lpas, y_pos])
        ListNodes.append([200 + node_tag3, Lw1/2, y_pos])
        ListNodes.append([300 + node_tag3, Lw1/2 + Lpas, y_pos])
        ListNodes.append([600 + node_tag3, LineaCol5 + Lw2_Yt, y_pos])
        ListNodes.append([700 + node_tag3, LineaCol5 + Lw2_Yt + Lpas2, y_pos])
        ListNodes.append([1000 + node_tag3, LineaCol9 + Lw3/2, y_pos])
        ListNodes.append([1300 + node_tag3, LineaCol9 + Lw3/2 + 2*Ldep + Lpas, y_pos])
    
    # Se recuperan los nodos basales y los master de piso
    ListNodes = np.array(ListNodes)
    # n_nodes = len(ListNodes)
    ListNodesBasal = ListNodes[np.where(ListNodes[:, 2] == 0.)]
    ListNodesDrift = ListNodes[np.where(ListNodes[:, 1] == 0.)]
    ListNodesDrift = (ListNodesDrift[np.where(ListNodesDrift[:,0] % 2 == 0)])[1:,:]
    
    # Se crean los nodos
    for nodo in ListNodes:
        ops.node(int(nodo[0]),nodo[1],nodo[2])
    
    # Define boundary conditions at ground nodes
    for nodo in ListNodesBasal:
        ops.fix(int(nodo[0]), 1, 1, 1)
        
    # Apply rigid diaphragm, i.e. all nodes in a floor to have the same lateral displacement
    # Nota: Debido a que todos los nudos se correstringen a los nudos 100, éstos se transforman en nudo 
    # master del piso    
    
    for piso in range(1, numStories + 1):
        master_tag = int(ListNodesDrift[piso-1][0])
        node_tag2 = WallElPerStory * piso
        node_tag3 = piso
        ops.equalDOF(master_tag, 200 + node_tag3, 1)
        ops.equalDOF(master_tag, 300 + node_tag3, 1)
        ops.equalDOF(master_tag, 400 + node_tag2, 1)
        ops.equalDOF(master_tag, 500 + node_tag2, 1)
        ops.equalDOF(master_tag, 600 + node_tag3, 1)
        ops.equalDOF(master_tag, 700 + node_tag3, 1)
        ops.equalDOF(master_tag, 800 + node_tag2, 1)
        ops.equalDOF(master_tag, 900 + node_tag2, 1)
        ops.equalDOF(master_tag, 1000 + node_tag3, 1)
        ops.equalDOF(master_tag, 1100 + node_tag3, 1)
        ops.equalDOF(master_tag, 1200 + node_tag3, 1)
        ops.equalDOF(master_tag, 1300 + node_tag3, 1)
        ops.equalDOF(master_tag, 1400 + node_tag2, 1)
        
        # Asigna masa sísmica al nudo master de cada piso
        if piso < numStories:
            ops.mass(master_tag, Ment, Negligible, Negligible)
        else:
            ops.mass(master_tag, Mcub, Negligible, Negligible)
    
    # Controlling parameters for displacement controlled analysis
    IDctrlNode = 100 + WallElPerStory * numStories
    IDctrlDOF = 1
    
    return ListNodes, ListNodesBasal, ListNodesDrift, IDctrlNode, IDctrlDOF


# # Define nodes, fixes, constraints and assign masses
# exec(open("NODES_00.py").read())



#%%
# =============================================================================
# Define Materials
# =============================================================================
def define_materials():
    # Material Tags
    matSteel = 1  # material reinforcement BOUNDARY
    matConcCover = 2  # material unconfined concrete
    matShearP1c01 = 3  # material elastic for Shear modelation in Wall
    matShearP1c05 = 4  # material elastic for Shear modelation in Wall
    matConcCoreP2 = 5  # material confined concrete
    matShearP2c01 = 6  # material elastic for Shear modelation in Wall
    matShearP2c05 = 7  # material elastic for Shear modelation in Wall
    matConcCoreP3 = 8  # material confined concrete
    matShearP3c01 = 9  # material elastic for Shear modelation in Wall
    matShearP3c05 = 10  # material elastic for Shear modelation in Wall
    matSteelUnc = 11     # material steel in unconfined concrete
    matSteelCoreP2 = 12  # material steel in confined concrete
    matSteelCoreP3 = 13  # material steel in confined concrete
    
    # ----------------------------
    # STEEL: Hysterectic model
    # ----------------------------
    fy = 481.899 
    Es = 200000.0  # Young's modulus
    b = 0.015  # strain hardening. Puede ser 0.020 para el acero A630-420H
    ey = fy / Es 
    fr = 0.1 * fy  # Esfuerzo residual del acero, para el Hysteretic
    
    
    # --------------------------
    # Unconfined materials
    # --------------------------
    # Concrete
    fpc_uc = -31.872  # peak compressive stress 
    Ec_uc = 4700 * np.sqrt(-fpc_uc) # 4700 raiz(f'c) ACI-318
    epc_uc = 2 * fpc_uc / Ec_uc  # 2*f'c/Ec
    fc20_uc = 0.2* fpc_uc  # 0.2*f'c
    ec20_uc = -0.008  # 0.008 Pugh 2015
    ft = 0.33 * np.sqrt(-fpc_uc) # 0.33 raiz(f'c) Pugh 2015
    Ets = 0.05 * Ec_uc  # 0.05Ec_uc Pugh 2015
    ops.uniaxialMaterial('Concrete02', matConcCover, fpc_uc, epc_uc, fc20_uc, ec20_uc, 0.1, ft, Ets)
    #uniaxialMaterial Concrete02, matTag, fpc, epsc0, fpcu, epsU, lambda, ft, Ets
    
    # Steel
    eu_p = 0.05  # Ingresar positivas las deformaciones unitarias
    eu_n = abs(ec20_uc)  # Pugh et al. 2015, 2012
    er_p = 0.06 
    er_n = 1.2 * eu_n 
    fu_p = b * Es * (eu_p - ey) + fy 
    fu_n = b * Es * (eu_n - ey) + fy 
    # uniaxialMaterial Hysteretic, matTag, s1p, e1p, s2p, e2p <$s3p, e3p>
    #, s1n, e1n, s2n, e2n <$s3n, e3n>, pinchX, pinchY, damage1, damage2 <$beta>
    ops.uniaxialMaterial('Hysteretic', matSteelUnc, fy, ey, fu_p, eu_p, fr, er_p, -fy, -ey,
                          -fu_n, -eu_n, -fr, -er_n, 1., 1., 0., 0., 0.)  
    
    
    # --------------------------
    # Confined materials in P2
    # --------------------------
    # Concrete
    fpc_c = -46.203  # peak compressive stress
    epc_c = -0.007796  # Saatcioglou y Razvi 1992
    fc20_c = 0.2 * fpc_c  # 0.2*f'c
    ec20_c = -0.05607  # Saatcioglou y Razvi 1992
    ops.uniaxialMaterial('Concrete02', matConcCoreP2, fpc_c, epc_c, fc20_c, ec20_c, 0.1, ft, Ets)
    
    # Steel
    eu_p = 0.05 
    eu_n = abs(ec20_c)
    er_p = 0.06 
    er_n = 1.2 * eu_n 
    fu_p = b * Es * (eu_p - ey) + fy 
    fu_n = b * Es * (eu_n - ey) + fy
    ops.uniaxialMaterial('Hysteretic', matSteelCoreP2, fy, ey, fu_p, eu_p, fr, er_p, -fy, -ey,
                          -fu_n, -eu_n, -fr, -er_n, 1., 1., 0., 0., 0.) 
    
    # --------------------------
    # Confined materials in P3
    # --------------------------
    # Concrete
    fpc_c = -41.481  # peak compressive stress
    epc_c = -0.005988  # Saatcioglou y Razvi 1992
    fc20_c = 0.2 * fpc_c  # 0.2*f'c
    ec20_c = -0.05934  # Saatcioglou y Razvi 1992
    ops.uniaxialMaterial('Concrete02', matConcCoreP3, fpc_c, epc_c, fc20_c, ec20_c, 0.1, ft, Ets)
    
    # Steel
    eu_p = 0.05 
    eu_n = abs(ec20_c)
    er_p = 0.06 
    er_n = 1.2 * eu_n 
    fu_p = b * Es * (eu_p - ey) + fy 
    fu_n = b * Es * (eu_n - ey) + fy  
    ops.uniaxialMaterial('Hysteretic', matSteelCoreP3, fy, ey, fu_p, eu_p, fr, er_p, -fy, -ey,
                          -fu_n, -eu_n, -fr, -er_n, 1., 1., 0., 0., 0.)
    
    # --------------------------
    # Shear materials
    # --------------------------
    # P1
    G = Ec_uc / (2 * (1 + 0.2))  # Shear Modulus
    AshwebP1 = 1.95  # Gross area of the wall cross section
    GAsP1 = 5/6 * G * AshwebP1  # Shear Stiffness  5/6 para sección rectangular
    # Command: uniaxialMaterial Elastic, matTag, E <$eta> <$Eneg>
    ops.uniaxialMaterial('Elastic', matShearP1c01, 0.1 * GAsP1) # En Lw/2
    ops.uniaxialMaterial('Elastic', matShearP1c05, 1.0 * GAsP1) # En resto del muro
    
    # P2
    AshwebP2 = 1.545  # Gross area of the wall cross section
    GAsP2 = G * AshwebP2  # Shear Stiffness, factor de corte = 1 para sección T
    ops.uniaxialMaterial('Elastic', matShearP2c01, 0.1 * GAsP2) # En Lw/2
    ops.uniaxialMaterial('Elastic', matShearP2c05, 1.0 * GAsP2) # En resto del muro
    
    # P3
    AshwebP3 = 1.05  # Gross area of the wall cross section
    GAsP3 = 5/6 * G * AshwebP3  # Shear Stiffness  5/6 para sección rectangular
    ops.uniaxialMaterial('Elastic', matShearP3c01, 0.1 * GAsP3) # En Lw/2
    ops.uniaxialMaterial('Elastic', matShearP3c05, 1.0 * GAsP3) # En resto del muro

    conc_tags = [matConcCover, matConcCoreP2, matConcCoreP3]
    steel_tags = [matSteelUnc, matSteelCoreP2, matSteelCoreP3]
    shear_tags = [matShearP1c01, matShearP1c05, matShearP2c01, matShearP2c05, matShearP3c01,
                  matShearP3c05]
    
    return conc_tags, steel_tags, shear_tags, Ec_uc
# # Define material properties
# exec(open("MATERIALS.py").read())



#%%
# =============================================================================
# Define Seccion Properties and Elements
# =============================================================================

def define_sections(numStories, WallElPerStory, Ec_uc, conc_tags, steel_tags, shear_tags):
    matConcCover, matConcCoreP2, matConcCoreP3 = conc_tags
    matSteelUnc, matSteelCoreP2, matSteelCoreP3 = steel_tags
    matShearP1c01, matShearP1c05, matShearP2c01, matShearP2c05, matShearP3c01, matShearP3c05 \
        = shear_tags
        
    # Define MVLEM wall elements
    n_fibers = [11,19,7]
    c_rot = 0.4
    rouYw1 = [0.00233, 0.00299, 0.00175]; # Y web (P1 y P3) y fibra 4 (P2)
    rouYw2 = 0.00262 # Y web central (P1 y P3) y fibra 5 a 9(P2)
    rou0 = 0.0  # fibras 11 y 19 ; 14 a 17 Un valor muy pequeño
    Twall = 0.3  # Espesor del muro en P1 y P3, y del alma de P2
    Tpatin = 5.0  # espesor del patin del muro T
    
    # Other output info
    tags_walls = []
    dict_elems = {}
    dict_walls_floor = {}
    for piso in range(1, numStories + 1):
        dict_walls_floor[piso] = []
    # n_wall_elems = 0
    
    # ----------------------------------------------------------------
    # Define wall model in axis 1
    # ----------------------------------------------------------------
    # Nota para generar los elementos: 
    # Piso 1 0.1G , Armado 10D16 , no confinado
    # Pisos 2 a 6 1.0G , Armado 10D16 , no confinado
    # Pisos 6 a 12 1.0G , Armado 10D16 , no confinado
    # Pisos 13 a 20 1.0G , Armado 10D12 , no confinado
    
    # Asigna muros en linea de columna 1
    n_elem = 1    
    for piso in range(1, numStories + 1):
        if piso == 1:
            rouYb = 0.00957
            matCorte = matShearP1c01
            matCon = matConcCover
            matSt = matSteelUnc 
        elif piso <= 12:
            matCorte = matShearP1c05
        else:
            rouYb = 0.00539
        
        for e in range(WallElPerStory):
            tags_walls.append(100 + n_elem)
            dict_walls_floor[piso].append(100 + n_elem)
            dict_elems[100 + n_elem] = {
                'eleType': 'MVLEM',
                'Dens': 0.0,
                'eleNodes': [100 + n_elem - 1, 100 + n_elem],
                'm': n_fibers[0],
                'c':c_rot,
                '-thick': [Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall,Twall],
                '-width': [0.7, 0.45, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.45, 0.7],
                '-rho': [rouYb, rouYw1[0], rouYw2, rouYw2, rouYw2, rouYw2, rouYw2, rouYw2, rouYw2, 
                         rouYw1[0], rouYb],
                '-matConcrete': [matCon, matCon, matCon, matCon, matCon, matCon, matCon, matCon, 
                                 matCon, matCon, matCon],
                '-matSteel': [matSt, matSt, matSt, matSt, matSt, matSt, matSt, matSt, matSt, matSt, 
                              matSt],
                '-matShear': matCorte,
                'floor': piso
                    }
            tags_walls.append(400 + n_elem)
            dict_walls_floor[piso].append(400 + n_elem)
            dict_elems[400 + n_elem] = {
                'eleType': 'MVLEM',
                'Dens': 0.0,
                'eleNodes': [400 + n_elem - 1, 400 + n_elem],
                'm': n_fibers[0],
                'c':c_rot,
                '-thick': [Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall],
                '-width': [0.7, 0.45, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.45, 0.7],
                '-rho': [rouYb, rouYw1[0], rouYw2, rouYw2, rouYw2, rouYw2, rouYw2, rouYw2, rouYw2, 
                         rouYw1[0], rouYb],
                '-matConcrete': [matCon, matCon, matCon, matCon, matCon, matCon, matCon, matCon, 
                                 matCon, matCon, matCon],
                '-matSteel': [matSt, matSt, matSt, matSt, matSt, matSt, matSt, matSt, matSt, matSt, 
                              matSt],
                '-matShear': matCorte,
                'floor': piso
                    }            
            n_elem += 1                                
            # n_wall_elems += 2
    
    
    # ----------------------------------------------------------------
    # Define wall model in axis 2
    # ----------------------------------------------------------------
    # Nota para generar los elementos: 
    # Piso 1 0.1G , Armado 27D18 , confinado borde del alma 
    # Pisos 2 a 3 1.0G , Armado 27D18 , confinado borde del alma
    # Pisos 4 a 6 1.0G , Armado 27D18 , no confinado
    # Pisos 7 a 12 1.0G , Armado 18D18 , no confinado
    # Pisos 13 a 20 1.0G , Armado 18D12 , no confinado
    
    # Asigna muros en linea de columna 5
    n_elem = 1    
    for piso in range(1, numStories + 1):
        if piso == 1:
            rouYb1 = 0.01909  # fibras 1 y 3 (Armado 1 con D18)
            rouYb2 = 0.01527  # fibra 2
            rouYw3 = 0.01357  # fibra 10
            rouYp1 = 0.02281  # fibra 12
            rouYp2 = 0.00305  # fibra 13
            rouYp3 = 0.02586  # fibra 18        
            matCorte = matShearP2c01
            matCon1 = matConcCoreP2
            matCon2 = matConcCover
            matSt1 = matSteelCoreP2
            matSt2 = matSteelUnc
        elif piso <= 3:
            matCorte = matShearP2c05
        elif piso <= 6:
            matCon1 = matConcCover
            matSt1 = matSteelUnc
        elif piso <= 12:
             rouYb1 = 0.01272  # fibras 1 y 3 (Armado 2 con D18)
             rouYb2 = 0.01018  # fibra 2
             rouYw3 = 0.01357  # fibra 10
             rouYp1 = 0.02281  # fibra 12
             rouYp2 = 0.00305  # fibra 13
             rouYp3 = 0.02586  # fibra 18
        else:
            rouYb1 = 0.00565  # fibras 1 y 3 (Armado 3 con D12)
            rouYb2 = 0.00452  # fibra 2
            rouYw3 = 0.00603  # fibra 10
            rouYp1 = 0.01433  # fibra 12
            rouYp2 = 0.00136  # fibra 13
            rouYp3 = 0.01568  # fibra 18
        
        for e in range(WallElPerStory):
            tags_walls.append(500 + n_elem)
            dict_walls_floor[piso].append(500 + n_elem)
            dict_elems[500 + n_elem] = {
                'eleType': 'MVLEM',
                'Dens': 0.0,
                'eleNodes': [500 + n_elem - 1, 500 + n_elem],
                'm': n_fibers[1],
                'c':c_rot,
                '-thick': [Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall, 
                           Tpatin, Tpatin, Tpatin, Tpatin, Tpatin, Tpatin, Tpatin, Tpatin, Tpatin],
                '-width': [0.4, 0.5, 0.4, 0.175, 0.6, 0.6, 0.6, 0.6, 0.6, 0.375, 0.03333, 0.03333, 
                           0.03333, 0.03333, 0.03333, 0.03333, 0.03333, 0.03333, 0.03333],
                '-rho': [rouYb1, rouYb2, rouYb1, rouYw1[1], rouYw2, rouYw2, rouYw2, rouYw2, rouYw2, 
                         rouYw3, rou0, rouYp1, rouYp2, rou0, rou0, rou0, rou0, rouYp3, rou0],
                '-matConcrete': [matCon1, matCon1, matCon1, matCon2, matCon2, matCon2, matCon2, 
                                 matCon2, matCon2, matCon2, matCon2, matCon2, matCon2, matCon2, 
                                 matCon2, matCon2, matCon2, matCon2, matCon2],
                '-matSteel': [matSt1, matSt1, matSt1, matSt2, matSt2, matSt2, matSt2, matSt2, 
                              matSt2, matSt2, matSt2, matSt2, matSt2, matSt2, matSt2, matSt2, matSt2, 
                              matSt2, matSt2],
                '-matShear': matCorte,
                'floor': piso
                    }
            n_elem += 1
            # n_wall_elems += 1
    
    
    # Asigna muros en linea de columna 8
    n_elem = 1    
    for piso in range(1, numStories + 1):
        if piso == 1:
            rouYb1 = 0.01909  # fibras 1 y 3 (Armado 1 con D18)
            rouYb2 = 0.01527  # fibra 2
            rouYw3 = 0.01357  # fibra 10
            rouYp1 = 0.02281  # fibra 12
            rouYp2 = 0.00305  # fibra 13
            rouYp3 = 0.02586  # fibra 18        
            matCorte = matShearP2c01
            matCon1 = matConcCoreP2
            matCon2 = matConcCover
            matSt1 = matSteelCoreP2
            matSt2 = matSteelUnc
        elif piso <= 3:
            matCorte = matShearP2c05
        elif piso <= 6:
            matCon1 = matConcCover
            matSt1 = matSteelUnc
        elif piso <= 12:
             rouYb1 = 0.01272  # fibras 1 y 3 (Armado 2 con D18)
             rouYb2 = 0.01018  # fibra 2
             rouYw3 = 0.01357  # fibra 10
             rouYp1 = 0.02281  # fibra 12
             rouYp2 = 0.00305  # fibra 13
             rouYp3 = 0.02586  # fibra 18
        else:
            rouYb1 = 0.00565  # fibras 1 y 3 (Armado 3 con D12)
            rouYb2 = 0.00452  # fibra 2
            rouYw3 = 0.00603  # fibra 10
            rouYp1 = 0.01433  # fibra 12
            rouYp2 = 0.00136  # fibra 13
            rouYp3 = 0.01568  # fibra 18
        
        for e in range(WallElPerStory):
            tags_walls.append(800 + n_elem)
            dict_walls_floor[piso].append(800 + n_elem)
            dict_elems[800 + n_elem] = {
                'eleType': 'MVLEM',
                'Dens': 0.0,
                'eleNodes': [800 + n_elem - 1, 800 + n_elem],
                'm': n_fibers[1],
                'c':c_rot,
                '-thick': [Tpatin, Tpatin, Tpatin, Tpatin, Tpatin, Tpatin, Tpatin, Tpatin, Tpatin, 
                           Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall, Twall],
                '-width': [0.03333, 0.03333, 0.03333, 0.03333, 0.03333, 0.03333, 0.03333, 0.03333, 
                           0.03333, 0.375, 0.6, 0.6, 0.6, 0.6, 0.6, 0.175, 0.4, 0.5, 0.4],
                '-rho': [rou0, rouYp3, rou0, rou0, rou0, rou0, rouYp2, rouYp1, rou0, rouYw3, rouYw2, 
                         rouYw2, rouYw2, rouYw2, rouYw2, rouYw1[1], rouYb1, rouYb2, rouYb1],
                '-matConcrete': [matCon2, matCon2, matCon2, matCon2, matCon2, matCon2, matCon2, 
                                 matCon2, matCon2, matCon2, matCon2, matCon2, matCon2, matCon2, 
                                 matCon2, matCon2, matCon1, matCon1, matCon1],
                '-matSteel': [matSt2, matSt2, matSt2, matSt2, matSt2, matSt2, matSt2, matSt2, matSt2, 
                              matSt2, matSt2, matSt2, matSt2, matSt2, matSt2, matSt2, matSt1, matSt1,
                              matSt1],
                '-matShear': matCorte,
                'floor': piso
                    }
            n_elem += 1
            # n_wall_elems += 1
    
    
    # ----------------------------------------------------------------
    # Define wall model in axis 3
    # ----------------------------------------------------------------
    # Nota para generar los elementos: 
    # Piso 1 0.1G , Armado 10D16 , confinado
    # Pisos 2 a 3 1.0G , Armado 10D16 , Confinado 
    # Pisos 3 a 6 1.0G , Armado 8D16 , no confinado
    # Pisos 7 a 12 1.0G , Armado 8D16 , no confinado
    # Pisos 13 a 20 1.0G , Armado 8D12 , no confinado
    
    # Asigna muros en linea de columna 1 y 14
    n_elem = 1    
    for piso in range(1, numStories + 1):
        if piso == 1:
            rouYb = 0.01219
            matCorte = matShearP3c01
            matCon1 = matConcCoreP3
            matCon2 = matConcCover
            matSt1 = matSteelCoreP3
            matSt2 = matSteelUnc
        elif piso <= 3:
            matCorte = matShearP3c05
        elif piso <= 6:
            matCon1 = matConcCover
            matSt1 = matSteelUnc
        elif piso <= 12:
            rouYb = 0.00975
        else:
            rouYb = 0.00548
        
        for e in range(WallElPerStory):
            tags_walls.append(900 + n_elem)
            dict_walls_floor[piso].append(900 + n_elem)
            dict_elems[900 + n_elem] = {
                'eleType': 'MVLEM',
                'Dens': 0.0,
                'eleNodes': [900 + n_elem - 1, 900 + n_elem],
                'm': n_fibers[2],
                'c':c_rot,
                '-thick': [Twall, Twall, Twall, Twall, Twall, Twall, Twall],
                '-width': [0.4, 0.45, 0.6, 0.6, 0.6, 0.45, 0.4],
                '-rho': [rouYb, rouYw1[2], rouYw2, rouYw2, rouYw2, rouYw1[2], rouYb],
                '-matConcrete': [matCon1, matCon2, matCon2, matCon2, matCon2, matCon2, matCon1],
                '-matSteel': [matSt1, matSt2, matSt2, matSt2, matSt2, matSt2, matSt1],
                '-matShear': matCorte
                    }
            tags_walls.append(1400 + n_elem)
            dict_walls_floor[piso].append(1400 + n_elem)
            dict_elems[1400 + n_elem] = {
                'eleType': 'MVLEM',
                'Dens': 0.0,
                'eleNodes': [1400 + n_elem - 1, 1400 + n_elem],
                'm': n_fibers[2],
                'c':c_rot,
                '-thick': [Twall, Twall, Twall, Twall, Twall, Twall, Twall],
                '-width': [0.4, 0.45, 0.6, 0.6, 0.6, 0.45, 0.4],
                '-rho': [rouYb, rouYw1[2], rouYw2, rouYw2, rouYw2, rouYw1[2], rouYb],
                '-matConcrete': [matCon1, matCon2, matCon2, matCon2, matCon2, matCon2, matCon1],
                '-matSteel': [matSt1, matSt2, matSt2, matSt2, matSt2, matSt2, matSt1],
                '-matShear': matCorte,
                'floor': piso
                    }
            n_elem += 1
            # n_wall_elems += 2
    
    for tag in tags_walls:
        wall = dict_elems[tag]
        if wall['eleType'] == 'MVLEM':
            ops.element(wall['eleType'], tag, wall['Dens'], *wall['eleNodes'], wall['m'], wall['c'],
                        '-thick', *wall['-thick'], '-width', *wall['-width'], '-rho', *wall['-rho'], 
                        '-matConcrete', *wall['-matConcrete'], '-matSteel', *wall['-matSteel'],
                        '-matShear', wall['-matShear'])
        
    
    # ----------------------------------------------------------------
    # Define beam sections
    # ----------------------------------------------------------------
    # Properties for elastic beam
    kbeam = 0.25
    Dbeam = np.array([0.16, 0.16, 0.16])  # Height
    Wbeam = np.array([0.5, 6.0, 2.0])  # Equivalent width
    Abeam = Dbeam * Wbeam
    Ibeam = kbeam * Wbeam * np.power(Dbeam,3.0) / 12
    
    # Properties for rigid beam and column
    A_rigid = 1 * 10**6
    I_rigid = 1 * 10**6
    Econ_rigid = Ec_uc
    
    # Define geometric transformation for beam-column element command: 
    # geomTransf Linear $transfTag <-jntOffset $dXi $dYi $dXj $dYj>
    BeamTransTag = 1
    ops.geomTransf('Linear', BeamTransTag)
    
    # Assign beam elements command: element elasticBeamColumn $eleID $iNode $jNode $A $E $I $transfID
    tags_beams = []
    for piso in range(1, numStories + 1):
        
        # Eje 1
        tags_beams.append(2000 + piso) # 100x - Rigid beam
        dict_elems[2000 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [100 + WallElPerStory * piso, 200 + piso],
            'Area': A_rigid, 
            'E_mod': Econ_rigid, 
            'Iz': I_rigid, 
            'transfTag': BeamTransTag
            }
        tags_beams.append(2100 + piso)
        dict_elems[2100 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [200 + piso, 300 + piso],
            'Area': Abeam[0], 
            'E_mod': Ec_uc, 
            'Iz': Ibeam[0], 
            'transfTag': BeamTransTag
            }        
        tags_beams.append(2200 + piso) # 120x - Rigid beam
        dict_elems[2200 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [300 + piso, 400 + WallElPerStory * piso],
            'Area': A_rigid, 
            'E_mod': Econ_rigid, 
            'Iz': I_rigid, 
            'transfTag': BeamTransTag
            }        
    
        # Eje 2
        tags_beams.append(3000 + piso) # 200x - Rigid beam
        dict_elems[3000 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [500 + WallElPerStory * piso, 600 + piso],
            'Area': A_rigid, 
            'E_mod': Econ_rigid, 
            'Iz': I_rigid, 
            'transfTag': BeamTransTag
            }
        tags_beams.append(3100 + piso)
        dict_elems[3100 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [600 + piso, 700 + piso],
            'Area': Abeam[1], 
            'E_mod': Ec_uc, 
            'Iz': Ibeam[1], 
            'transfTag': BeamTransTag
            }        
        tags_beams.append(3200 + piso) # 220x - Rigid beam    
        dict_elems[3200 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [700 + piso, 800 + WallElPerStory * piso],
            'Area': A_rigid, 
            'E_mod': Econ_rigid, 
            'Iz': I_rigid, 
            'transfTag': BeamTransTag
            }    
    
        # Eje 3
        tags_beams.append(4000 + piso) # 300x - Rigid beam
        dict_elems[4000 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [900 + WallElPerStory * piso, 1000 + piso],
            'Area': A_rigid, 
            'E_mod': Econ_rigid, 
            'Iz': I_rigid, 
            'transfTag': BeamTransTag
            }
        tags_beams.append(4100 + piso)
        dict_elems[4100 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [1000 + piso, 1100 + piso],
            'Area': Abeam[2], 
            'E_mod': Ec_uc, 
            'Iz': Ibeam[2], 
            'transfTag': BeamTransTag
            }           
        tags_beams.append(4200 + piso)
        dict_elems[4200 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [1100 + piso, 1200 + piso],
            'Area': Abeam[2], 
            'E_mod': Ec_uc, 
            'Iz': Ibeam[2], 
            'transfTag': BeamTransTag
            } 
        tags_beams.append(4300 + piso)
        dict_elems[4300 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [1200 + piso, 1300 + piso],
            'Area': Abeam[2], 
            'E_mod': Ec_uc, 
            'Iz': Ibeam[2], 
            'transfTag': BeamTransTag
            }           
        tags_beams.append(4400 + piso)
        dict_elems[4400 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [1300 + piso, 1400 + piso],
            'Area': A_rigid, 
            'E_mod': Econ_rigid, 
            'Iz': I_rigid, 
            'transfTag': BeamTransTag
            }  
    
    for tag in tags_beams:
        beam = dict_elems[tag]
        if beam['eleType'] == 'elasticBeamColumn':
            ops.element(beam['eleType'], tag, *beam['eleNodes'], beam['Area'], beam['E_mod'], 
                        beam['Iz'],beam['transfTag'])
    
    
    # ----------------------------------------------------------------
    # Define column sections
    # ----------------------------------------------------------------
    # Properties for elastic columna
    kcol = 0.7
    Dcol = 0.3  # Wall depth
    Wcol = 5.5  # Wall width
    Acol = Dcol * Wcol
    Icol = kcol * Wcol * Dcol**3 / 12
    
    # Define geometric transformation for beam-column element command: 
    # geomTransf Linear $transfTag <-jntOffset $dXi $dYi $dXj $dYj>
    ColTransTag = 2
    ops.geomTransf('Linear', ColTransTag)
    
    # Assign column elements command: 
    # element elasticBeamColumn $eleID $iNode $jNode $A $E $I $transfID
    tags_cols = []
    for piso in range(1, numStories + 1):
        tags_cols.append(1100 + piso) 
        dict_elems[1100 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [1100 + piso - 1, 1100 + piso],
            'Area': Acol, 
            'E_mod': Ec_uc, 
            'Iz': Icol, 
            'transfTag': ColTransTag
            }
        tags_cols.append(1200 + piso) # 100x - Rigid beam
        dict_elems[1200 + piso] = {
            'eleType': 'elasticBeamColumn', 
            'eleNodes': [1200 + piso - 1, 1200 + piso],
            'Area': Acol, 
            'E_mod': Ec_uc, 
            'Iz': Icol, 
            'transfTag': ColTransTag
            }
        
    for tag in tags_cols:
        col = dict_elems[tag]
        if col['eleType'] == 'elasticBeamColumn':
            ops.element(col['eleType'], tag, *col['eleNodes'], col['Area'], col['E_mod'], 
                        col['Iz'], col['transfTag'])    


    return tags_walls, tags_beams, tags_cols, dict_elems, dict_walls_floor

# # Define elements
# exec(open("ELEMENTS.py").read())



#%%
# =============================================================================
# Gravity loads
# =============================================================================

def define_gravity_loads(numStories, WallElPerStory):
    # Define gravity loads
    P1 = 0.254
    P2 = 0.4939
    P3 = 0.2191
    P4 = 0.2501
    
    # Apply gravity loads
    # Construct a time series where load factor applied is linearly proportional to the time domain command: 
    # pattern PatternType $PatternID TimeSeriesType
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)
    
    # Nodal load on walls - Command: load nodeID xForce yForce
    # Note: 1.157 is eccentricity between Lw/2 and centroid
    for piso in range(1, numStories + 1):
        load_tag = WallElPerStory * piso
        ops.load(100 + load_tag, 0.0, -P1, 0.0)
        ops.load(400 + load_tag, 0.0, -P1, 0.0)
        ops.load(500 + load_tag, 0.0, -P2, -1.157 * P2)
        ops.load(800 + load_tag, 0.0, -P2, 1.157 * P2)
        ops.load(900 + load_tag, 0.0, -P3, 0.0)
        ops.load(1100 + piso, 0.0, -P4, 0.0)
        ops.load(1200 + piso, 0.0, -P4, 0.0)
        ops.load(1400 + load_tag, 0.0, -P3, 0.0)

