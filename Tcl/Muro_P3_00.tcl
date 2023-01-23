# ----------------------------------------------------------------
# Define wall model in axis 3
# ----------------------------------------------------------------

# Define shear materials .........................................................................
# Command: uniaxialMaterial Elastic $matTag $E <$eta> <$Eneg>
set Ashweb 1.05; # Gross area of the wall cross section
set G [expr $Ec_uc/(2.*(1.+0.2))]; # Shear Modulus
set GAs [expr (5./6.)*$G*$Ashweb]; # Shear Stiffness; 5/6 para sección rectangular

# Build shear materials
uniaxialMaterial Elastic $matShearP3c01 [expr 0.1*$GAs]; # En Lw/2
uniaxialMaterial Elastic $matShearP3c05 [expr 1.0*$GAs]; # En resto del muro

# Define MVLEM wall elements ......................................................................
set n_fibers 7;
set c_rot 0.4; 
set rouYw1 0.00175; # Y web 
set rouYw2 0.00262; # Y web central
set Twall 0.3; # Espesor de los muros

# Nota para generar los elementos: 
# ----------------------------------------------------------------------------------------------
# Piso 1 0.1G , Armado 10D16 , confinado
# Pisos 2 a 3 1.0G , Armado 10D16 , Confinado 
# Pisos 3 a 6 1.0G , Armado 8D16 , no confinado
# Pisos 7 a 12 1.0G , Armado 8D16 , no confinado
# Pisos 13 a 20 1.0G , Armado 8D12 , no confinado
# ----------------------------------------------------------------------------------------------

# Asigna muros en linea de columna 1 y 14
set k 1
for {set i 1} {$i <= $numStories} {incr i} {
	if {$i == 1} {
		set rouYb 0.01219;
		set matCorte $matShearP3c01
		set matCon1 $matConcCoreP3
		set matCon2 $matConcCover
		set matSt1 $matSteelCoreP3
		set matSt2 $matSteelUnc

	} elseif {$i <= 3} {
		set matCorte $matShearP3c05
	} elseif {$i <= 6} {
		set matCon1 $matConcCover
		set matSt1 $matSteelUnc
	} elseif {$i <= 12} {
		set rouYb 0.00975;
	} else {
		set rouYb 0.00548;
	}
	for {set j 1} {$j <= $WallElPerStory} {incr j} {
		element MVLEM [expr 900 + $k] 0.0 [expr 900 + $k - 1] [expr 900 + $k] \
		$n_fibers $c_rot -thick $Twall $Twall $Twall $Twall $Twall $Twall $Twall -width 0.4 0.45 0.6 0.6 0.6 \
		0.45 0.4 -rho $rouYb $rouYw1 $rouYw2 $rouYw2 $rouYw2 $rouYw1 $rouYb -matConcrete $matCon1 \
		$matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon1 -matSteel $matSt1 $matSt2 $matSt2 \
		$matSt2 $matSt2 $matSt2 $matSt1 -matShear $matCorte;
		
		element MVLEM [expr 1400 + $k] 0.0 [expr 1400 + $k - 1] [expr 1400 + $k] \
		$n_fibers $c_rot -thick $Twall $Twall $Twall $Twall $Twall $Twall $Twall -width 0.4 0.45 0.6 0.6 0.6 \
		0.45 0.4 -rho $rouYb $rouYw1 $rouYw2 $rouYw2 $rouYw2 $rouYw1 $rouYb -matConcrete $matCon1 \
		$matCon2 $matCon2 $matCon2 $matCon2 $matCon2 $matCon1 -matSteel $matSt1 $matSt2 $matSt2 \
		$matSt2 $matSt2 $matSt2 $matSt1 -matShear $matCorte;
		
		set k [expr $k +1]
	}
}
