# ----------------------------------------------------
# Modal Analysis
# ----------------------------------------------------

# Generate the model and run gravity analysis
source GEOM_00.tcl
# Para el análisis modal no necesito el análisis gravitacional primero
# ----------------------------------Eigenvalue Analysis --------------------------------

set nEigenJ 2; 
# Show initial periods T1 and T2
set pi 3.141593;
set lambdaN [eigen $nEigenJ]
set T {};
foreach lam $lambdaN {
	lappend Tperiod [expr (2.0*$pi)/sqrt($lam)];
}

# puts ""
# puts "T1 = [lindex $Tperiod 0] s"
# puts "T2 = [lindex $Tperiod 1] s"

set T1 [lindex $Tperiod 0]; # Save fundamental period

# # Display Deformed Shape
# set ViewScale 10; 
# DisplayModel2D nill $ViewScale;

# --------------------------------- Rayleigh Damping ------------------------------------

# Define critical damping and Switchs 
set xDamp 0.02;
set MpropSwitch 1.0;
set KcurrSwitch 1.0;
set KcommSwitch 0.0;
set KinitSwitch 0.0;

set omegaI [expr 2.0*$pi/(0.2*$T1)]
set omegaJ [expr 2.0*$pi/(1.5*$T1)]

# Calculate proportionality factors for Rayleigh damping
set alphaM [expr $MpropSwitch*$xDamp*(2*$omegaI*$omegaJ)/($omegaI+$omegaJ)];
set betaKcurr [expr $KcurrSwitch*2.0*$xDamp/($omegaI+$omegaJ)]; 
set betaKcomm [expr $KcommSwitch*2.0*$xDamp/($omegaI+$omegaJ)]; 
set betaKinit [expr $KinitSwitch*2.0*$xDamp/($omegaI+$omegaJ)]; 

# Apply reyleigh damping 
rayleigh $alphaM $betaKcurr $betaKinit $betaKcomm;