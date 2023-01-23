# =============================================================================
# Define nodes
# =============================================================================
# Comentar esta línea antes de correr
import openseespy.opensees as ops

# Nodos de la base
ops.node(100, 0.0, 0.0) # Linea de columna 1 
ops.node(400, Lw1 + Lpas, 0.0) # Linea de columna 4
ops.node(500, LineaCol5, 0.0) # Linea de columna 5
ops.node(800, LineaCol5 + 2 * Lw2_Yt + Lpas2, 0.0) # Linea de columna 8
ops.node(900, LineaCol9, 0.0) # Linea de columna 9
ops.node(1100, LineaCol9 + Lw3/2 + Ldep, 0.0) # Linea de columna 11
ops.node(1200, LineaCol9 + Lw3/2 + Ldep + Lpas, 0.0) # Linea de columna 12
ops.node(1400, LineaCol9 + Lw3 + 2 * Ldep + Lpas, 0.0) # Linea de columna 14

# Genera nodos piso por piso
NodesPerStory = WallElPerStory - 1
for piso in range(1, numStories + 1):
    # Crear nodos intermedios del entrepiso
    for nodo in range(1, NodesPerStory + 1):
        node_tag1 = nodo + WallElPerStory*(piso-1)
        y_pos1 = nodo * Hstory / WallElPerStory + (piso-1)*Hstory
        ops.node(100 + node_tag1, 0.0, y_pos1)
        ops.node(400 + node_tag1, Lw1 + Lpas, y_pos1)
        ops.node(500 + node_tag1, LineaCol5, y_pos1)
        ops.node(800 + node_tag1, LineaCol5 + 2*Lw2_Yt + Lpas2, y_pos1)
        ops.node(900 + node_tag1, LineaCol9, y_pos1)
        ops.node(1400 + node_tag1, LineaCol9 + Lw3 + 2*Ldep + Lpas, y_pos1)

    # Crear nodos de piso
    node_tag2 = WallElPerStory * piso
    node_tag3 = piso
    y_pos2 = piso * Hstory
    ops.node(100 + node_tag2, 0.0, y_pos)
    ops.node(400 + node_tag2, Lw1 + Lpas, y_pos)
    ops.node(500 + node_tag2, LineaCol5, y_pos)
    ops.node(800 + node_tag2, LineaCol5 + 2*Lw2_Yt + Lpas2, y_pos)
    ops.node(900 + node_tag2, LineaCol9, y_pos)
    ops.node(1100 + node_tag3, LineaCol9 + Lw3/2 + Ldep, y_pos)
    ops.node(1200 + node_tag3, LineaCol9 + Lw3/2.0 + Ldep + Lpas, y_pos)
    ops.node(1400 + node_tag2, LineaCol9 + Lw3 + 2*Ldep + Lpas, y_pos)
    ops.node(200 + node_tag3, Lw1/2, y_pos)
    ops.node(300 + node_tag3, Lw1/2 + Lpas, y_pos)
    ops.node(600 + node_tag3, LineaCol5 + Lw2_Yt, y_pos)
    ops.node(700 + node_tag3, LineaCol5 + Lw2_Yt + Lpas2, y_pos)
    ops.node(1000 + node_tag3, LineaCol9 + Lw3/2, y_pos)
    ops.node(1300 + node_tag3, LineaCol9 + Lw3/2 + 2*Ldep + Lpas, y_pos)
    
# Define boundary conditions at ground nodes
ops.fix(100, 1, 1, 1)
ops.fix(400, 1, 1, 1)
ops.fix(500, 1, 1, 1)
ops.fix(800, 1, 1, 1)
ops.fix(900, 1, 1, 1)
ops.fix(1100, 1, 1, 1)
ops.fix(1200, 1, 1, 1)
ops.fix(1400, 1, 1, 1)  
    
# Apply rigid diaphragm, i.e. all nodes in a floor to have the same lateral displacement
# Nota: Debido a que todos los nudos se correstringen a los nudos 100, éstos se transforman en nudo master del piso    
for piso in range(1, numStories + 1):
    master_tag = 100 + WallElPerStory * piso
    node_tag2 = WallElPerStory * piso
    node_tag3 = piso
    ops.equalDOF(node_tag2, 200 + node_tag3, 1)
    ops.equalDOF(node_tag2, 300 + node_tag3, 1)
    ops.equalDOF(node_tag2, 400 + node_tag2, 1)
    ops.equalDOF(node_tag2, 500 + node_tag2, 1)
    ops.equalDOF(node_tag2, 600 + node_tag3, 1)
    ops.equalDOF(node_tag2, 700 + node_tag3, 1)
    ops.equalDOF(node_tag2, 800 + node_tag2, 1)
    ops.equalDOF(node_tag2, 900 + node_tag2, 1)
    ops.equalDOF(node_tag2, 1000 + node_tag3, 1)
    ops.equalDOF(node_tag2, 1100 + node_tag3, 1)
    ops.equalDOF(node_tag2, 1200 + node_tag3, 1)
    ops.equalDOF(node_tag2, 1300 + node_tag3, 1)
    ops.equalDOF(node_tag2, 1400 + node_tag2, 1)

# Asigna masa sísmica al nudo master de cada piso 
for piso in range(1, numStories + 1):
    master_tag = 100 + WallElPerStory * piso
    if piso < numStories:
        ops.mass(master_tag, Ment, Negligible, Negligible)
    else:
        ops.mass(master_tag, Mcub, Negligible, Negligible)

# Set controlling parameters for displacement controlled analysis
IDctrlNode = 100 + WallElPerStory * numStories
IDctrlDOF = 1



