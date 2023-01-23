# ----------------------------------------------------------------
# Define materials
# ----------------------------------------------------------------

# ------------------------------------- Material Tags --------------------------------------
set matSteel 1; # material reinforcement BOUNDARY
set matConcCover 2; # material unconfined concrete
set matShearP1c01 3; # material elastic for Shear modelation in Wall
set matShearP1c05 4; # material elastic for Shear modelation in Wall
set matConcCoreP2 5; # material confined concrete
set matShearP2c01 6; # material elastic for Shear modelation in Wall
set matShearP2c05 7; # material elastic for Shear modelation in Wall
set matConcCoreP3 8; # material confined concrete
set matShearP3c01 9; # material elastic for Shear modelation in Wall
set matShearP3c05 10; # material elastic for Shear modelation in Wall

# Para Hysteretic
set matSteelUnc 11;
set matSteelCoreP2 12;
set matSteelCoreP3 13;


# ----------------------------
# STEEL: Hysterectic
# ----------------------------
set fy 481.899;
set Es 200000.0; # Young's modulus
set b 0.015; # strain hardening. Puede ser 0.020 para el acero A630-420H
set ey [expr $fy/$Es];
set fr [expr 0.1*$fy]; # Esfuerzo residual del acero, para el Hysteretic


# --------------------------
# CONCRETE: unconfined
# --------------------------
set fpc_uc -31.872; # peak compressive stress 
set epc_uc -0.0024; # 2*f'c/Ec
set fc20_uc -6.374; # 0.2*f'c
set ec20_uc -0.008; # 0.008 Pugh 2015
set ft 1.863; # 0.33 raiz(f'c) Pugh 2015
set Ets 1326.699; # 0.05Ec_uc Pugh 2015
set Ec_uc 26533.987; # 4700 raiz(f'c) ACI-318

#uniaxialMaterial Concrete02 $matTag $fpc $epsc0 $fpcu $epsU $lambda $ft $Ets
uniaxialMaterial Concrete02 $matConcCover $fpc_uc $epc_uc $fc20_uc $ec20_uc 0.1 $ft $Ets

set eu_p 0.05; # Ingresar positivas las deformaciones unitarias
set eu_n [expr abs($ec20_uc)]; # Pugh et al. 2015, 2012
set er_p 0.06;
set er_n [expr 1.2*$eu_n];
set fu_p [expr $b*$Es*($eu_p-$ey)+$fy] 
set fu_n [expr $b*$Es*($eu_n-$ey)+$fy] 

# uniaxialMaterial Hysteretic $matTag $s1p $e1p $s2p $e2p <$s3p $e3p>
# $s1n $e1n $s2n $e2n <$s3n $e3n> $pinchX $pinchY $damage1 $damage2 <$beta>
uniaxialMaterial Hysteretic $matSteelUnc $fy $ey $fu_p $eu_p $fr $er_p -$fy -$ey -$fu_n -$eu_n -$fr -$er_n 1. 1. 0. 0. 0. 


# --------------------------
# CONCRETE: confined P2
# --------------------------
set fpc_c -46.203; # peak compressive stress
set epc_c -0.007796; # Saatcioglou y Razvi 1992
set fc20_c -9.241; # 0.2*f'c
set ec20_c -0.05607; # Saatcioglou y Razvi 1992

#uniaxialMaterial Concrete02 $matTag $fpc $epsc0 $fpcu $epsU $lambda $ft $Ets
uniaxialMaterial Concrete02 $matConcCoreP2 $fpc_c $epc_c $fc20_c $ec20_c 0.1 $ft $Ets
set eu_p 0.05;
set eu_n [expr abs($ec20_c)];
set er_p 0.06;
set er_n [expr 1.2*$eu_n];
set fu_p [expr $b*$Es*($eu_p-$ey)+$fy] 
set fu_n [expr $b*$Es*($eu_n-$ey)+$fy] 

# uniaxialMaterial Hysteretic $matTag $s1p $e1p $s2p $e2p <$s3p $e3p> 
# $s1n $e1n $s2n $e2n <$s3n $e3n> $pinchX $pinchY $damage1 $damage2 <$beta>
uniaxialMaterial Hysteretic $matSteelCoreP2 $fy $ey $fu_p $eu_p $fr $er_p -$fy -$ey -$fu_n -$eu_n -$fr -$er_n 1. 1. 0. 0. 0. 


# --------------------------
# CONCRETE: confined P3
# --------------------------
set fpc_c -41.481; # peak compressive stress
set epc_c -0.005988; # Saatcioglou y Razvi 1992
set fc20_c -8.296; # 0.2*f'c
set ec20_c -0.05934; # Saatcioglou y Razvi 1992

#uniaxialMaterial Concrete02 $matTag $fpc $epsc0 $fpcu $epsU $lambda $ft $Ets
uniaxialMaterial Concrete02 $matConcCoreP3 $fpc_c $epc_c $fc20_c $ec20_c 0.1 $ft $Ets

set eu_p 0.05;
set eu_n [expr abs($ec20_c)];
set er_p 0.06;
set er_n [expr 1.2*$eu_n];
set fu_p [expr $b*$Es*($eu_p-$ey)+$fy] 
set fu_n [expr $b*$Es*($eu_n-$ey)+$fy] 

# uniaxialMaterial Hysteretic $matTag $s1p $e1p $s2p $e2p <$s3p $e3p> 
# $s1n $e1n $s2n $e2n <$s3n $e3n> $pinchX $pinchY $damage1 $damage2 <$beta>
uniaxialMaterial Hysteretic $matSteelCoreP3 $fy $ey $fu_p $eu_p $fr $er_p -$fy -$ey -$fu_n -$eu_n -$fr -$er_n 1. 1. 0. 0. 0. 