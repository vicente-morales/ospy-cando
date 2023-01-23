# =============================================================================
# Modal Analysis
# =============================================================================
import openseespy.opensees as ops
import numpy as np

def modal_analysis(log=None):
    if log != None:
        log.write('----- Analysis: ModalAnalysis -----\n')    
    
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
    ops.setTime(0.0)
    
    if log != None:
        log.write('..... Finalized: ModalAnalysis .....\n')
        log.write('\n')
    
    return T1, T2, omega1, omega2
