import openseespy.opensees as ops
# import numpy as np  # load the numpy module, calling it np

# ----------------------------------------------------------------
# -- Script to Conduct 3D Non-linear Response History Analysis ---
# ----------------------------------------------------------------
# Copyright by Gerard J. O'Reilly, 2017
# EUCENTRE and IUSS Pavia, Italy
# Date Created: April 2012
# Last Updated: May 2017

# This procedure is a simple script that executes the NRHA of a 3D model. It
# requires that the model has the dynamic analysis objects defined and just the
# 'analyze' of a regular OpenSees model needs to be executed. Therefore, the model
# needs to be built to the point where a modal analysis can be conducted. The
# ground motion timeSeries and pattern need to be setup and the constraints,
# numberer and system analysis objects also need to be predefined.

# When conducting the NRHA, this proc will try different options to achieve
# convergence and finish the ground motion. This allows for a relatively robust
# analysis algorithm to be implemented with a single command.

# In addition, the analysis requires that a deformation capacity be specified
# to define a limit that upon exceedance, will stop the NRHA and mark the
# analysis as a collapse case. It monitors the current deformation of a number
# of specified nodes and flags collapse based on their deforormation. This
# prevents the models getting 'stuck' trying to converge a model that has
# essentially collapsed, or would be deemed a collapse case in post processing.
# These are defined in terms of both the local storey drifts and also the roof
# drift in either direction. For 3D analysis, the absolute maximum drift in
# either direction is used. Other definitions are possible but not yet implemented.

# Lastly, a log file identifier is also required in the input. This will log
# all of the essential information about the maximum storey drifts. This script
# was developed for analysing buildings so the deformation capacity typically
# corresponds to a drift capacity and the top and bottom nodes would typically
# correspond to the centreline nodes of the floorslabs.

# WARNING: The acceleration values that are ouput from this are the relative
# accelerations. For some reason, you cant get the current absolute values with
# inline commands.

# def runNRHA3D(Dt, Tmax, Dc, log, pflag, ListNodesDrift, ListNodesBasal):
def runNRHA3D(Dt, Tmax):
    # --------------------------------------------------
    # Description of Parameters
    # --------------------------------------------------
    # Dt:		Analysis time step
    # Tmax:	Length of the record (including padding of 0's)
    # Dc:		Deformation capacity (radians or metres)
    # tNode:	List of top nodes (e.g. {2 3 4 5})
    # bNode:	List of bottom node (e.g. {1 2 3 4})
    # log:	File handle of the logfile
    # --------------------------------------------------

    # Make the control index available outside the proc
    # Define the initial Analysis parameters

    # if pflag > 0:
    #     print("Starting runNRHA")
    ops.wipeAnalysis()
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandGeneral')

    testType = 'NormDispIncr'
    tolInit = 1.0e-6  # the initial Tolerance, so it can be referred back to
    iterInit = 50  # the initial Max Number of Iterations
    algorithmType = 'KrylovNewton'  # the algorithm type

    ops.test(testType, tolInit, iterInit)  # determine if convergence has been achieved at the end of an iteration step
    ops.algorithm(algorithmType)  # use Newton solution algorithm: updates tangent stiffness at every iteration
    NewmarkGamma = 0.5
    NewmarkBeta = 0.25
    ops.integrator('Newmark', NewmarkGamma, NewmarkBeta)
    ops.analysis('Transient')

    # Set up analysis parameters
    # Nsteps = int(Tmax / Dt)  # integer of the number of steps needed
    cIndex = 0  # Initially define the control index (-1 for non-converged, 0 for stable, 1 for global
    # collapse, 2 for local collapse)
    controlTime = 0.0  # Start the controlTime
    ok = 0  # Set the convergence to 0 (initially converged)
    # md = 0.0  # Set the initial storey drift
    # mflr = 0  # Set the initial storey collapse location

    # Set up the storey drift and acceleration values
    # maxDriftPiso = 0.0
    # htot = np.amax(ListNodesDrift[:,2],axis=0)
    # VBasal_v = []
    # DriftTecho_v = []
    # maxDriftPiso_v = []

    # Run the actual analysis now
    while cIndex == 0 and controlTime <= Tmax and ok == 0:
        # Runs while the building is stable, time is less
        # than that of the length of the record (plus buffering)
        # and the analysis is still converging

        # Do the analysis
        ok = ops.analyze(1, Dt)
        controlTime = ops.getTime()  # Update the control time
        # if pflag > 1:
        #     print('Completed', controlTime, 'of', Tmax, 'seconds')

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
            ops.algorithm('Broyden', 8)
            ok = ops.analyze(1, Dt)
            ops.algorithm(algorithmType)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Trying Newton with Initial Tangent ......')
            ops.algorithm('Newton', '-initial')
            ok = ops.analyze(1, Dt)
            ops.algorithm(algorithmType)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Trying NewtonWithLineSearch...... ......')
            ops.algorithm('NewtonLineSearch', 0.8)
            ok = ops.analyze(1, Dt)
            ops.algorithm(algorithmType)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Trying Newton with Initial Tangent & relaxed convergence......')
            ops.test(testType, tolInit * 0.1, iterInit * 50)
            ops.algorithm('Newton', '-initial')
            ok = ops.analyze(1, Dt)
            ops.test(testType, tolInit, iterInit)
            ops.algorithm(algorithmType)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Trying Newton with Initial Tangent & relaxed convergence......')
            ops.test(testType, tolInit * 0.1, iterInit * 50)
            ops.algorithm('Newton', '-initial')
            ok = ops.analyze(1, Dt)
            ops.test(testType, tolInit, iterInit)
            ops.algorithm(algorithmType)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Trying Newton with Initial Tangent & relaxed convergence......')
            ops.test(testType, tolInit * 0.1, iterInit * 50)
            ops.algorithm('Newton', '-initial')
            ok = ops.analyze(1, Dt)
            ops.test(testType, tolInit, iterInit)
            ops.algorithm(algorithmType)
        if ok != 0:
            # print('~~~ Failed at ', controlTime, ' - Trying NewtonWithLineSearch & relaxed convergence......')
            ops.test(testType, tolInit * 0.1, iterInit * 50)
            ops.algorithm('NewtonLineSearch', '-initial')
            ok = ops.analyze(1, Dt)
            ops.test(testType, tolInit, iterInit)
            ops.algorithm(algorithmType)
        if ok != 0:
            # print('~~~ Failed at ', controlTime,
            #        ' - Trying Newton with Initial Tangent, reduced timestep & relaxed convergence......')
            ops.test(testType, tolInit * 0.1, iterInit * 50)
            ops.algorithm('Newton', '-initial')
            Dtt = 0.5 * Dt
            ok = ops.analyze(1, Dtt)
            ops.test(testType, tolInit, iterInit)
            ops.algorithm(algorithmType)
        if ok != 0:
            # print('~~~ Failed at ', controlTime,
            #        ' - Trying Newton with Initial Tangent, reduced timestep & relaxed convergence......')
            ops.test(testType, tolInit * 0.1, iterInit * 50)
            ops.algorithm('Newton', '-initial')
            Dtt = 0.5 * Dt
            ok = ops.analyze(1, Dtt)
            ops.test(testType, tolInit, iterInit)
            ops.algorithm(algorithmType)
        if ok != 0:
            # print('~~~ Failed at ', controlTime,
            #       ' - Trying NewtonWithLineSearch, reduced timestep & relaxed convergence......')
            ops.test(testType, tolInit * 0.1, iterInit * 50)
            ops.algorithm('NewtonLineSearch', 0.8)
            Dtt = 0.5 * Dt
            ok = ops.analyze(1, Dtt)
            ops.test(testType, tolInit, iterInit)
            ops.algorithm(algorithmType)
        # Game over......
        if ok != 0:
            # log.write('~~~ Failed at ', controlTime, ' - exit analysis......')
            cIndex = -1

    #     # Check the actual state of the model with respect to the limits provided

    #     # Calculation of maximum Drift between floors
    #     for (nod_ini, nod_end) in zip(ListNodesDrift[:-1, 0], ListNodesDrift[1:, 0]):
    #         # print('nod_ini ', nod_ini, 'nod_end', nod_end)
    #         nod_ini = int(nod_ini)
    #         nod_end = int(nod_end)
    #         pos_i = ops.nodeCoord(nod_ini, 2)
    #         pos_s = ops.nodeCoord(nod_end, 2)
    #         hpiso = pos_s - pos_i
    #         desp_i = ops.nodeDisp(nod_ini, 1)
    #         desp_s = ops.nodeDisp(nod_end, 1)
    #         desp_piso = abs(desp_s - desp_i)
    #         drift_piso = desp_piso / hpiso
    #         if drift_piso >= maxDriftPiso:
    #             maxDriftPiso = drift_piso
    #     maxDriftPiso_v = np.append(maxDriftPiso_v, maxDriftPiso)
    #     VBasal = 0.
    #     ops.reactions()
    #     for node in ListNodesBasal:
    #         # print('ind Basal ', node[0])
    #         VBasal = VBasal + ops.nodeReaction(node[0], 1)
    #     ctrlNode = int(ListNodesDrift[-1, 0])
    #     VBasal_v = np.append(VBasal_v, VBasal)
    #     DriftTecho = ops.nodeDisp(ctrlNode, 1) / htot
    #     DriftTecho_v = np.append(DriftTecho_v, DriftTecho)
    # # DriftTecho_v = np.array(DriftTecho_v)
    # maxDriftTecho = np.abs(DriftTecho_v).max()
    # maxDriftPisoBdg = np.abs(maxDriftPiso_v).max()
    # maxVBasal = np.abs(VBasal_v).max()
    # md = maxDriftPisoBdg
    # print('maxDriftTecho={0:.3f} maxDriftPisoBdg={1:.3f} maxVBasal={2:.3f}'.format(maxDriftTecho, maxDriftPisoBdg, maxVBasal))

    # if md >= Dc:
    #     cIndex = 1  # Set the state of the model to local collapse (=1)
    #     md = Dc
    #     ops.wipe

    # # Create some output
    # log.write('\n' + 'FinalState:{0:d} at {1:.3f} of {2:.3f} seconds'.format(cIndex, controlTime, Tmax))
    # log.write('\n' + 'PeakDemand:{0:.5f}'.format(md))

    # Print to the max interstorey drifts

    # if pflag > 0:
    #     print('PeakDemand:{0:.5f}'.format(md))  # Print to the max demand
    # if cIndex == -1:
    #     print(':::::: ANALYSIS FAILED TO CONVERGE at ', controlTime, ' of ', Tmax, ' :::::')
    # if cIndex == 0:
    #     print('######## ANALYSIS COMPLETED SUCCESSFULLY #####')
    # if cIndex == 1:
    #     print('========== LOCAL STRUCTURE COLLAPSE ==========')

    # return cIndex, maxDriftTecho, maxDriftPisoBdg, maxVBasal
    return cIndex, controlTime
