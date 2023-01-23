# =============================================================================
# Gravity Loads & Gravity Analysis
# =============================================================================
import openseespy.opensees as ops
# import numpy as np

def gravity_analysis(log=None):
    
    if log != None:
        log.write('----- Analysis: GravityAnalysis -----\n')  
    
    # ops.recorder('Node','-file','Gravity_Reactions.out','-time', '-node', 100, 400, 500, '-dof', 1, 2, 'reaction')
    # Configuraciones del sistema
    ops.system('BandGeneral')						# Decirle que es una matriz diagonal de manera de optimizar
    ops.numberer('RCM')							# Re-enumera los gdl para optimizar
    ops.constraints('Plain')
    
    # Gravity-analysis: load-controlled static analysis
    Tol = 1 * 10**(-6)
    NstepGravity = 10
    DGravity = 1.0 / NstepGravity
    
    ops.test('NormDispIncr',Tol,100)  # Convergence Test 
    ops.algorithm('Newton')  # Solution Algorithm 
    ops.integrator('LoadControl', DGravity)
    ops.analysis('Static')
    ops.analyze(NstepGravity)
    
    # Reset for next analysis case 
    # print(ops.eleResponse(140,*['-time','Fiber_Strain']))
    # print(np.array(ops.eleResponse(140,*['Fiber_Strain'])))
    # awa = np.array(ops.eleResponse(140,*['Fiber_Strain']))
    ops.loadConst('-time', 0.0)
    # ops.remove('recorders')
    ops.wipeAnalysis() 
    
    if log != None:
        log.write('..... Finalized: GravityAnalysis ..... \n')  
        log.write('\n')

    return None
