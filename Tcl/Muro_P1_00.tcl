# ----------------------------------------------------------------
# Define wall model in axis 1
# ----------------------------------------------------------------

# Define shear materials .........................................................................
# Command: uniaxialMaterial Elastic $matTag $E <$eta> <$Eneg>
set Ashweb 1.95; # Gross area of the wall cross section
set G [expr $Ec_uc/(2.*(1.+0.2))]; # Shear Modulus
set GAs [expr (5./6.)*$G*$Ashweb]; # Shear Stiffness; 5/6 para sección rectangular

# Build shear materials
uniaxialMaterial Elastic $matShearP1c01 [expr 0.1*$GAs]; # En Lw/2
uniaxialMaterial Elastic $matShearP1c05 [expr 1.0*$GAs]; # En resto del muro

# Define MVLEM wall elements ......................................................................
set n_fibers 11;
set c_rot 0.4; 
set rouYw1 0.00233; # Y web 
set rouYw2 0.00262; # Y web central
set Twall 0.3; # Espesor de los muros

# Nota para generar los elementos: 
# ----------------------------------------------------------------------------------------------
# Piso 1 0.1G , Armado 10D16 , no confinado
# Pisos 2 a 6 1.0G , Armado 10D16 , no confinado
# Pisos 6 a 12 1.0G , Armado 10D16 , no confinado
# Pisos 13 a 20 1.0G , Armado 10D12 , no confinado
# ----------------------------------------------------------------------------------------------

# Asigna muros en linea de columna 1
set k 1
for {set i 1} {$i <= $numStories} {incr i} {
	if {$i == 1} {
		set rouYb 0.00957
		set matCorte $matShearP1c01
		set matCon $matConcCover
		set matSt $matSteelUnc
	} elseif {$i <= 12} {
		set matCorte $matShearP1c05
	} else {
		set rouYb 0.00539
	}
	for {set j 1} {$j <= $WallElPerStory} {incr j} {
		element MVLEM [expr 100 + $k] 0.0 [expr 100 + $k - 1] [expr 100 + $k] $n_fibers \
		$c_rot -thick $Twall $Twall $Twall $Twall $Twall $Twall $Twall $Twall $Twall $Twall $Twall -width \
		0.7 0.45 0.6 0.6 0.6 0.6 0.6 0.6 0.6 0.45 0.7 -rho $rouYb $rouYw1 $rouYw2 $rouYw2 $rouYw2 $rouYw2 \
		$rouYw2 $rouYw2 $rouYw2 $rouYw1 $rouYb -matConcrete $matCon $matCon $matCon $matCon \
		$matCon $matCon $matCon $matCon $matCon $matCon $matCon -matSteel $matSt $matSt $matSt \
		$matSt $matSt $matSt $matSt $matSt $matSt $matSt $matSt -matShear $matCorte;
		
		element MVLEM [expr 400 + $k] 0.0 [expr 400 + $k - 1] [expr 400 + $k] $n_fibers \
		$c_rot -thick $Twall $Twall $Twall $Twall $Twall $Twall $Twall $Twall $Twall $Twall $Twall -width \
		0.7 0.45 0.6 0.6 0.6 0.6 0.6 0.6 0.6 0.45 0.7 -rho $rouYb $rouYw1 $rouYw2 $rouYw2 $rouYw2 $rouYw2 \
		$rouYw2 $rouYw2 $rouYw2 $rouYw1 $rouYb -matConcrete $matCon $matCon $matCon $matCon \
		$matCon $matCon $matCon $matCon $matCon $matCon $matCon -matSteel $matSt $matSt $matSt \
		$matSt $matSt $matSt $matSt $matSt $matSt $matSt $matSt -matShear $matCorte;
		
		set k [expr $k +1]
	}
}
