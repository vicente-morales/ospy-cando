# ----------------------------------------------------------------
# Define nodes
# ----------------------------------------------------------------
# Command: node nodeID x-coord y-coord -mass mass_dof1 mass_dof2 mass_dof3

# Genera los nudos de la cimentación
node 100 0.0 0.0; # Linea de columna 1 
node 400 [expr $Lw1 + $Lpas] 0.0; # Linea de columna 4
node 500 $LineaCol5 0.0; # Linea de columna 5
node 800 [expr $LineaCol5 + 2.0*$Lw2_Yt + $Lpas2] 0.0; # Linea de columna 8
node 900 $LineaCol9 0.0; # Linea de columna 9
node 1100 [expr $LineaCol9 + $Lw3/2.0 + $Ldep] 0.0; # Linea de columna 11
node 1200 [expr $LineaCol9 + $Lw3/2.0 + $Ldep + $Lpas] 0.0; # Linea de columna 12
node 1400 [expr $LineaCol9 + $Lw3 + 2.0*$Ldep + $Lpas] 0.0; # Linea de columna 14

# Genera nudos piso por piso
set NodesPerStory [expr $WallElPerStory-1]; 
for {set j 1} {$j <= $numStories} {incr j} { 

	# Crea nudos intermedios del entrepiso
	for {set i 1} {$i <= $NodesPerStory} {incr i} { 
		node [expr 100 + $i + $WallElPerStory*($j-1)] 0.0 [expr $i*$Hstory/$WallElPerStory + ($j-1)*$Hstory];
		node [expr 400 + $i + $WallElPerStory*($j-1)] [expr $Lw1 + $Lpas] [expr $i*$Hstory/$WallElPerStory + ($j-1)*$Hstory];
		node [expr 500 + $i + $WallElPerStory*($j-1)] $LineaCol5 [expr $i*$Hstory/$WallElPerStory + ($j-1)*$Hstory];
		node [expr 800 + $i + $WallElPerStory*($j-1)] [expr $LineaCol5 + 2.0*$Lw2_Yt + $Lpas2] [expr $i*$Hstory/$WallElPerStory + ($j-1)*$Hstory];
		node [expr 900 + $i + $WallElPerStory*($j-1)] $LineaCol9 [expr $i*$Hstory/$WallElPerStory + ($j-1)*$Hstory];
		node [expr 1400 + $i + $WallElPerStory*($j-1)] [expr $LineaCol9 + $Lw3 + 2.0*$Ldep + $Lpas] [expr $i*$Hstory/$WallElPerStory + ($j-1)*$Hstory];
	}

	#Crea nudos del piso
	node [expr 100 + $WallElPerStory*$j] 0.0 [expr $j*$Hstory]; 
	node [expr 400 + $WallElPerStory*$j] [expr $Lw1 + $Lpas] [expr $j*$Hstory]; 
	node [expr 500 + $WallElPerStory*$j] $LineaCol5 [expr $j*$Hstory]; 
	node [expr 800 + $WallElPerStory*$j] [expr $LineaCol5 + 2.0*$Lw2_Yt + $Lpas2] [expr $j*$Hstory];
	node [expr 900 + $WallElPerStory*$j] $LineaCol9 [expr $j*$Hstory];
	node [expr 1100 + $j] [expr $LineaCol9 + $Lw3/2.0 + $Ldep] [expr $j*$Hstory];
	node [expr 1200 + $j] [expr $LineaCol9 + $Lw3/2.0 + $Ldep + $Lpas] [expr $j*$Hstory];
	node [expr 1400 + $WallElPerStory*$j] [expr $LineaCol9 + $Lw3 + 2.0*$Ldep + $Lpas] [expr $j*$Hstory];
	node [expr 200 + $j] [expr $Lw1/2.0] [expr $j*$Hstory];
	node [expr 300 + $j] [expr $Lw1/2.0 + $Lpas] [expr $j*$Hstory];
	node [expr 600 + $j] [expr $LineaCol5 + $Lw2_Yt] [expr $j*$Hstory];
	node [expr 700 + $j] [expr $LineaCol5 + $Lw2_Yt + $Lpas2] [expr $j*$Hstory];
	node [expr 1000 + $j] [expr $LineaCol9 + $Lw3/2.0] [expr $j*$Hstory];
	node [expr 1300 + $j] [expr $LineaCol9 + $Lw3/2.0 + 2.0*$Ldep + $Lpas] [expr $j*$Hstory];
}

# Define boundary conditions at ground nodes
fix 100 1 1 1;
fix 400 1 1 1;
fix 500 1 1 1;
fix 800 1 1 1;
fix 900 1 1 1;
fix 1100 1 1 1;
fix 1200 1 1 1;
fix 1400 1 1 1;

# Apply rigid diaphragm, i.e. all nodes in a floor to have the same lateral displacement
# Nota: Debido a que todos los nudos se correstringen a los nudos 100, éstos se transforman en nudo master del piso
for {set i 1} {$i <= $numStories} {incr i} { 
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 200 + $i] 1; 
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 300 + $i] 1;
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 400 + $WallElPerStory*$i] 1;
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 500 + $WallElPerStory*$i] 1;
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 600 + $i] 1;
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 700 + $i] 1;
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 800 + $WallElPerStory*$i] 1;
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 900 + $WallElPerStory*$i] 1;
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 1000 + $i] 1;
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 1100 + $i] 1;
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 1200 + $i] 1;
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 1300 + $i] 1;
	equalDOF [expr 100 + $WallElPerStory*$i] [expr 1400 + $WallElPerStory*$i] 1;
}

# Asigna masa sísmica al nudo master de cada piso 
for {set i 1} {$i <= $numStories} {incr i} { 
	if {$i == $numStories} {
		mass [expr 100 + $WallElPerStory*$i] $Mcub $Negligible $Negligible
	} else {
		mass [expr 100 + $WallElPerStory*$i] $Ment $Negligible $Negligible
	}
}

# Set controlling parameters for displacement controlled analysis
set IDctrlNode [expr 100 + $WallElPerStory*$numStories];
set IDctrlDOF 1;
