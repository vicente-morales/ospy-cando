# =============================================================================
# Gravity Loads & Gravity Analysis
# =============================================================================
# Líneas para comentar antes de correr
# import openseespy.opensees as ops

print('--- Analysis: GravityAnalysis ---')

# Configuraciones del sistema
ops.system('BandGeneral')						# Decirle que es una matriz diagonal de manera de optimizar
ops.numberer('RCM')							# Re-enumera los gdl para optimizar
ops.constraints('Plain')

# Gravity-analysis: load-controlled static analysis
Tol = 1 * 10**(-6)
NstepGravity = 10
DGravity = 1.0 / NstepGravity

ops.test('NormDispIncr',Tol,6)  # Convergence Test 
ops.algorithm('Newton')  # Solution Algorithm 
ops.integrator('LoadControl', DGravity)
ops.analysis('Static')
ops.analyze(NstepGravity)

# Reset for next analysis case 
ops.loadConst('-time', 0.0)
# ops.wipeAnalysis() 

print('--- Finalized: GravityAnalysis ---')
print()
