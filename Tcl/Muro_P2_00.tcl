# ----------------------------------------------------------------
# Define wall model in axis 2
# ----------------------------------------------------------------

# Define shear materials .........................................................................
# Command: uniaxialMaterial Elastic $matTag $E <$eta> <$Eneg>
set Ashweb 1.545; # Gross area of the wall cross section
set G [expr $Ec_uc/(2.*(1.+0.2))]; # Shear Modulus
set GAs $G*$Ashweb; # Shear Stiffness; factor de corte= 1 para sección T

# Build shear materials
uniaxialMaterial Elastic $matShearP2c01 [expr 0.1*$GAs]; # En Lw/2
uniaxialMaterial Elastic $matShearP2c05 [expr 1.0*$GAs]; # En resto del muro

# Define MVLEM wall elements ......................................................................
set n_fibers 19;
set c_rot 0.4; 
set rouYw1 0.00299; # fibra 4 
set rouYw2 0.00262; # fibra 5 a 9
set rou0 0.0; # fibras 11 y 19 ; 14 a 17 Un valor muy pequeño
set Talma 0.3; # espesor del alma del muro T
set Tpatin 5.0; # espesor del patin del muro T

# Nota para generar los elementos: 
# ----------------------------------------------------------------------------------------------
# Piso 1 0.1G , Armado 27D18 , confinado borde del alma 
# Pisos 2 a 3 1.0G , Armado 27D18 , confinado borde del alma
# Pisos 4 a 6 1.0G , Armado 27D18 , no confinado
# Pisos 7 a 12 1.0G , Armado 18D18 , no confinado
# Pisos 13 a 20 1.0G , Armado 18D12 , no confinado
# ----------------------------------------------------------------------------------------------

# Asigna muros en linea de columna 5
set k 1
for {set i 1} {$i <= $numStories} {incr i} {
	if {$i == 1} {
		set rouYb1 0.01909; # fibras 1 y 3 (Armado 1 con D18)
		set rouYb2 0.01527; # fibra 2
		set rouYw3 0.01357; # fibra 10
		set rouYp1 0.02281; # fibra 12
		set rouYp2 0.00305; # fibra 13
		set rouYp3 0.02586; # fibra 18
		set matCorte $matShearP2c01
		set matCon1 $matConcCoreP2
		set matCon2 $matConcCover
		set matSt1 $matSteelCoreP2
		set matSt2 $matSteelUnc
	} elseif {$i <= 3} {
		set matCorte $matShearP2c05
	} elseif {$i <= 6} {
		set matCon1 $matConcCover
		set matSt1 $matSteelUnc
	} elseif {$i <= 12} {
		set rouYb1 0.01272; # fibras 1 y 3 (Armado 2 con D18)
		set rouYb2 0.01018; # fibra 2
		set rouYw3 0.01357; # fibra 10
		set rouYp1 0.02281; # fibra 12
		set rouYp2 0.00305; # fibra 13
		set rouYp3 0.02586; # fibra 18
	} else {
		set rouYb1 0.00565; # fibras 1 y 3 (Armado 3 con D12)
		set rouYb2 0.00452; # fibra 2
		set rouYw3 0.00603; # fibra 10
		set rouYp1 0.01433; # fibra 12
		set rouYp2 0.00136; # fibra 13
		set rouYp3 0.01568; # fibra 18
	}
	for {set j 1} {$j <= $WallElPerStory} {incr j} {
	
		element MVLEM [expr 500 + $k] 0.0 [expr 500 + $k - 1] [expr 500 + $k] \
		$n_fibers $c_rot -thick $Talma $Talma $Talma $Talma $Talma $Talma $Talma $Talma $Talma $Talma \
		$Tpatin $Tpatin $Tpatin $Tpatin $Tpatin $Tpatin $Tpatin $Tpatin $Tpatin -width 0.4 0.5 0.4 0.175 0.6 \
		0.6 0.6 0.6 0.6 0.375 0.03333 0.03333 0.03333 0.03333 0.03333 0.03333 0.03333 0.03333 0.03333 -rho \
		$rouYb1 $rouYb2 $rouYb1 $rouYw1 $rouYw2 $rouYw2 $rouYw2 $rouYw2 $rouYw2 $rouYw3 $rou0 \
		$rouYp1 $rouYp2 $rou0 $rou0 $rou0 $rou0 $rouYp3 $rou0 -matConcrete $matCon1 $matCon1 \
		$matCon1 $matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon2 \
		$matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon2 -matSteel $matSt1 \
		$matSt1 $matSt1 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 \
		$matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 -matShear $matCorte;
		
		set k [expr $k +1]
	}
}

# Asigna muros en linea de columna 8
set k 1
for {set i 1} {$i <= $numStories} {incr i} {
	if {$i == 1} {
		set rouYb1 0.01909; # fibras 1 y 3 (Armado 1 con D18)
		set rouYb2 0.01527; # fibra 2
		set rouYw3 0.01357; # fibra 10
		set rouYp1 0.02281; # fibra 12
		set rouYp2 0.00305; # fibra 13
		set rouYp3 0.02586; # fibra 18
		set matCorte $matShearP2c01
		set matCon1 $matConcCoreP2
		set matCon2 $matConcCover
		set matSt1 $matSteelCoreP2
		set matSt2 $matSteelUnc
	} elseif {$i <= 3} {
		set matCorte $matShearP2c05
	} elseif {$i <= 6} {
		set matCon1 $matConcCover
		set matSt1 $matSteelUnc
	} elseif {$i <= 12} {
		set rouYb1 0.01272; # fibras 1 y 3 (Armado 2 con D18)
		set rouYb2 0.01018; # fibra 2
		set rouYw3 0.01357; # fibra 10
		set rouYp1 0.02281; # fibra 12
		set rouYp2 0.00305; # fibra 13
		set rouYp3 0.02586; # fibra 18
	} else {
		set rouYb1 0.00565; # fibras 1 y 3 (Armado 3 con D12)
		set rouYb2 0.00452; # fibra 2
		set rouYw3 0.00603; # fibra 10
		set rouYp1 0.01433; # fibra 12
		set rouYp2 0.00136; # fibra 13
		set rouYp3 0.01568; # fibra 18
	}
	for {set j 1} {$j <= $WallElPerStory} {incr j} {
		element MVLEM [expr 800 + $k] 0.0 [expr 800 + $k - 1] [expr 800 + $k] \
		$n_fibers $c_rot -thick $Tpatin $Tpatin $Tpatin $Tpatin $Tpatin $Tpatin $Tpatin $Tpatin $Tpatin $Talma \
		$Talma $Talma $Talma $Talma $Talma $Talma $Talma $Talma $Talma -width 0.03333 0.03333 \
		0.03333 0.03333 0.03333 0.03333 0.03333 0.03333 0.03333 0.375 0.6 0.6 0.6 0.6 0.6 0.175 0.4 0.5 0.4 \
		-rho $rou0 $rouYp3 $rou0 $rou0 $rou0 $rou0 $rouYp2 $rouYp1 $rou0 $rouYw3 $rouYw2 $rouYw2 \
		$rouYw2 $rouYw2 $rouYw2 $rouYw1 $rouYb1 $rouYb2 $rouYb1 -matConcrete $matCon2 $matCon2 \
		$matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon2 \
		$matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon1 $matCon1 $matCon1 -matSteel $matSt2 \
		$matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 $matSt2 \
		$matSt2 $matSt2 $matSt2 $matSt1 $matSt1 $matSt1 -matShear $matCorte;
		
		set k [expr $k +1]
	}
}