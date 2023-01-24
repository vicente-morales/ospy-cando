# ----------------------------------------------------------------
# -- Script to Conduct Non-linear Response History Analysis ---
# ----------------------------------------------------------------
# Therefore, the model needs to be built to the point where a modal analysis can be conducted.
# The ground motion timeSeries and pattern need to be setup.

# When conducting the NRHA, this proc will try different options to achieve
# convergence and finish the ground motion. This allows for a relatively robust
# analysis algorithm to be implemented with a single command.

import openseespy.opensees as ops
from check_collapse import check_collapse

def runNRHA2D(Dt, Tmax, ListNodesDrift=[], dict_elems=[], tags_walls=[], dict_walls_floor=[], 
            WallElPerStory = 0, dict_mats=[], log=[]):
    # --------------------------------------------------
    # Description of Parameters
    # --------------------------------------------------
    # Dt:	Analysis time step
    # Tmax:	Length of the record (including padding of 0's)
    # log:	File handle of the logfile
    # --------------------------------------------------
    if type(log) != type([]):
        pflag = 1
    else:
        pflag = 0
        
    if pflag == 1:
        log.write("--- Starting runNRHA ---\n")
        
    if len(ListNodesDrift) != 0 and len(dict_elems) != 0 and len(tags_walls) != 0 and \
        len(dict_walls_floor) != 0 and len(dict_mats) != 0 and WallElPerStory != 0:
        checkFlag = 1
    else:
        checkFlag = 0

    # Define the initial Analysis parameters
    ops.wipeAnalysis()
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandGeneral')
    testType = 'NormDispIncr'
    tolInit = 1.0e-4  # the initial Tolerance, so it can be referred back to
    iterInit = 50  # the initial Max Number of Iterations
    # use Newton solution algorithm: updates tangent stiffness at every iteration
    algorithmType = 'KrylovNewton'  # the algorithm type
    ops.test(testType, tolInit, iterInit)  
    ops.algorithm(algorithmType) 
    NewmarkGamma = 0.5
    NewmarkBeta = 0.25
    ops.integrator('Newmark', NewmarkGamma, NewmarkBeta)
    ops.analysis('Transient')

    # Set up analysis 
    cIndex = 0  # Initially define the control index 
    # (-1 for non-converged, 0 for stable, 1 for global Convecollapse, 2 for local collapse)
    controlTime = 0.0  # Start the controlTime
    ok = 0  # Set the convergence to 0 (initially converged)
    
    # Analysis outputs
    max_drift_techo = 0

    # Run the actual analysis now
    while cIndex == 0 and controlTime <= Tmax and ok == 0:
        # Runs while the building is stable, time is less than that of the length of the record
        # and the analysis is still converging

        # Define standard test and algorithm
        ops.test(testType, tolInit, iterInit)  
        ops.algorithm(algorithmType)  
        
        # Do the analysis
        ok = ops.analyze(1, Dt)
        controlTime = ops.getTime()  # Update the control time

        # If the analysis fails, try the following changes to achieve convergence
        # Analysis will be slower in here though...

        # First changes are to change algorithm to achieve convergence...
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Reduced timestep by half......')
            Dtt = 0.5 * Dt
            ok = ops.analyze(1, Dtt)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Reduced timestep by quarter......')
            Dtt = 0.25 * Dt
            ok = ops.analyze(1, Dtt)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Trying Broyden......')
            ops.algorithm('Broyden')
            ok = ops.analyze(1, Dt)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Trying Newton with Initial Tangent ......')
            ops.algorithm('Newton', '-initial')
            ok = ops.analyze(1, Dt)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Trying NewtonWithLineSearch...... ......')
            ops.algorithm('NewtonLineSearch')
            ok = ops.analyze(1, Dt)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Trying Newton with Initial Tangent & relaxed convergence......')
            ops.test(testType, tolInit * 10, iterInit * 20)
            ops.algorithm('Newton', '-initial')
            ok = ops.analyze(1, Dt)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Trying NewtonWithLineSearch & relaxed convergence......')
            # ops.test(testType, tolInit * 10, iterInit * 20)
            ops.algorithm('NewtonLineSearch')
            ok = ops.analyze(1, Dt)
        if ok != 0:
            # print('~~~ Failed at ', controlTime,
            #       ' - Trying Newton with Initial Tangent, reduced timestep & relaxed convergence......')
            # ops.test(testType, tolInit * 10, iterInit * 20)
            ops.algorithm('Newton', '-initial')
            Dtt = 0.5 * Dt
            ok = ops.analyze(1, Dtt)
        if ok != 0:
            # print('~~~ Failed at ', controlTime,
            #       ' - Trying NewtonWithLineSearch, reduced timestep & relaxed convergence......')
            # ops.test(testType, tolInit * 10, iterInit * 20)
            ops.algorithm('NewtonLineSearch')
            Dtt = 0.5 * Dt
            ok = ops.analyze(1, Dtt)
        # Game over......
        if ok != 0:
            cIndex = -1
        
        # Save run data
        if cIndex == 0 and checkFlag == 1:
            cIndex, roof_disp = check_collapse(
                ListNodesDrift, dict_elems, tags_walls, dict_walls_floor, WallElPerStory, dict_mats) 
            max_drift_techo = max([max_drift_techo, abs(roof_disp)])
        
    # Results
    if pflag > 0:
        if cIndex == 0:
            log.write('... ANALYSIS COMPLETED SUCCESSFULLY ...\n')
        elif cIndex == -1:
            log.write('... ANALYSIS FAILED TO CONVERGE at ', controlTime, ' of ', Tmax, ' ...\n')
        elif cIndex == 1:
            log.write('... GLOBAL COLLAPSE at ', controlTime, ' of ', Tmax, ' ...\n')
        elif cIndex == 2:
            log.write('... LOCAL COLLAPSE at ', controlTime, ' of ', Tmax, ' ...\n')
    
    controlTime = round(controlTime, 3)
    max_drift_techo = round(max_drift_techo, 4)
    
    return cIndex, controlTime, max_drift_techo
