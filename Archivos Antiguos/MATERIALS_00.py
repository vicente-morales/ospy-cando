# =============================================================================
# Define materials
# =============================================================================
# Comentar antes de correr
import numpy as np
import openseespy.opensees as ops


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

# Para Hysteretic
matSteelUnc = 11 
matSteelCoreP2 = 12 
matSteelCoreP3 = 13 


# ----------------------------
# STEEL: Hysterectic
# ----------------------------
fy = 481.899 
Es = 200000.0  # Young's modulus
b = 0.015  # strain hardening. Puede ser 0.020 para el acero A630-420H
ey = fy / Es 
fr = 0.1 * fy  # Esfuerzo residual del acero, para el Hysteretic


# --------------------------
# CONCRETE: unconfined
# --------------------------
# Hormigón
fpc_uc = -31.872  # peak compressive stress 
Ec_uc = 4700 * np.sqrt(-fpc_uc) # 4700 raiz(f'c) ACI-318
epc_uc = 2 * fpc_uc / Ec_uc  # 2*f'c/Ec
fc20_uc = 0.2* fpc_uc  # 0.2*f'c
ec20_uc = -0.008  # 0.008 Pugh 2015
ft = 0.33 * np.sqrt(-fpc_uc) # 0.33 raiz(f'c) Pugh 2015
Ets = 0.05 * Ec_uc  # 0.05Ec_uc Pugh 2015
ops.uniaxialMaterial('Concrete02', matConcCover, fpc_uc, epc_uc, fc20_uc, ec20_uc, 0.1, ft, Ets)
#uniaxialMaterial Concrete02 $matTag $fpc $epsc0 $fpcu $epsU $lambda $ft $Ets

# Acero
eu_p = 0.05  # Ingresar positivas las deformaciones unitarias
eu_n = abs(ec20_uc)  # Pugh et al. 2015, 2012
er_p = 0.06 
er_n = 1.2 * eu_n 
fu_p = b * Es * (eu_p - ey) + fy 
fu_n = b * Es * (eu_n - ey) + fy 
# uniaxialMaterial Hysteretic $matTag $s1p $e1p $s2p $e2p <$s3p $e3p>
# $s1n $e1n $s2n $e2n <$s3n $e3n> $pinchX $pinchY $damage1 $damage2 <$beta>
ops.uniaxialMaterial('Hysteretic', matSteelUnc, fy, ey, fu_p, eu_p, fr, er_p, -fy, -ey,
                     -fu_n, -eu_n, -fr, -er_n, 1., 1., 0., 0., 0.)


# --------------------------
# CONCRETE: confined P2
# --------------------------
# Hormigón
fpc_c = -46.203  # peak compressive stress
epc_c = -0.007796  # Saatcioglou y Razvi 1992
fc20_c = 0.2 * fpc_c  # 0.2*f'c
ec20_c = -0.05607  # Saatcioglou y Razvi 1992
#uniaxialMaterial Concrete02 $matTag $fpc $epsc0 $fpcu $epsU $lambda $ft $Ets
ops.uniaxialMaterial('Concrete02', matConcCoreP2, fpc_c, epc_c, fc20_c, ec20_c, 0.1, ft, Ets)


# Acero
eu_p = 0.05 
eu_n = abs(ec20_c)
er_p = 0.06 
er_n = 1.2 * eu_n 
fu_p = b * Es * (eu_p - ey) + fy 
fu_n = b * Es * (eu_n - ey) + fy 
uniaxialMaterial Hysteretic $matSteelCoreP2 $fy $ey $fu_p $eu_p $fr $er_p -$fy -$ey -$fu_n -$eu_n -$fr -$er_n 1. 1. 0. 0. 0. 


# --------------------------
# CONCRETE: confined P3
# --------------------------
fpc_c -41.481  # peak compressive stress
epc_c -0.005988  # Saatcioglou y Razvi 1992
fc20_c -8.296  # 0.2*f'c
ec20_c -0.05934  # Saatcioglou y Razvi 1992

#uniaxialMaterial Concrete02 $matTag $fpc $epsc0 $fpcu $epsU $lambda $ft $Ets
uniaxialMaterial Concrete02 $matConcCoreP3 $fpc_c $epc_c $fc20_c $ec20_c 0.1 $ft $Ets

eu_p 0.05 
eu_n   abs($ec20_c)] 
er_p 0.06 
er_n   1.2*$eu_n] 
fu_p   $b*$Es*($eu_p-$ey)+$fy] 
fu_n   $b*$Es*($eu_n-$ey)+$fy] 

# uniaxialMaterial Hysteretic $matTag $s1p $e1p $s2p $e2p <$s3p $e3p> 
# $s1n $e1n $s2n $e2n <$s3n $e3n> $pinchX $pinchY $damage1 $damage2 <$beta>
uniaxialMaterial Hysteretic $matSteelCoreP3 $fy $ey $fu_p $eu_p $fr $er_p -$fy -$ey -$fu_n -$eu_n -$fr -$er_n 1. 1. 0. 0. 0. 

