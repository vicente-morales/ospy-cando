# =============================================================================
# Modal Analysis
# =============================================================================

# Líneas para comentar antes de correr
import openseespy.opensees as ops
import numpy as np

print('----- Analysis: ModalAnalysis -----')

# Obtain periods
nEigenJ = 2  # number of modes
lambdaN = np.array(ops.eigen(nEigenJ))
omega = np.sqrt(lambdaN)
Tn = 2 * np.pi / omega

omega1 = omega[0]
omega2 = omega[1]
T1 = Tn[0]
T2 = Tn[1]


# Reset for next analysis case  
ops.loadConst('-time', 0.0)
ops.wipeAnalysis()

print('..... Finalized: ModalAnalysis .....')
print()
