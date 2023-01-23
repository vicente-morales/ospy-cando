# ----------------------------------------------------------------
# Build model and run Gravity Analysis
# ----------------------------------------------------------------

# ##################################################################################
# Set Up & Source Definition 
# #################################################################################
wipe
model BasicBuilder -ndm 2 -ndf 3;
# source DisplayModel2D.tcl;
# source DisplayPlane.tcl;


# #################################################################################
# Define Building Geometry, Nodes, and Constraint 
# #################################################################################
# Units: MPa, MN, m, sec
# Define basic geometry 

# Vertical geometry
set numStories 20;
set Hstory 2.6; # Story height
set Htotal [expr $numStories*$Hstory]; # Total building height
set WallElPerStory 2;

# Horizontal geometry
set Lw1 6.5; # Length wall axis 1
set Lw2_Yt 2.575; # Centroid position
set Lw3 3.5; # Length wall axis 2
set Lpas 2.0; # Length corridor axes 1 and 3
set Lpas2 1.7; # Length corridor axis 2
set Ldep 1.5; # Length corridor in apartment
set Lsep 10.0; # Length between frames
set LineaCol5 [expr $Lw1 + $Lpas + $Lsep]; # Columna line 5, coordinate x
set LineaCol9 [expr $LineaCol5 + 2.0*$Lw2_Yt + $Lpas2 + $Lsep]; # Columna line 9, coordinate x

# Define floor masses
set Mcub 0.2391;
set Ment 0.2482;
set Negligible 1.0e-9;

# Define nodes, fixes, constraints and assign masses
source NODES_00.tcl


# ##################################################################################
# Define Section Properties and Elements
# ##################################################################################

# Define material properties
source MATERIALS_00.tcl

# Define wall sections & assign 
source Muro_P1_00.tcl
source Muro_P2_00.tcl
source Muro_P3_00.tcl

# Define beam sections & assign 
set kbeam 0.25;

# Beams axis 1
set Dbeam1 0.16;
set Wbeam1 0.5;
set Abeam1 [expr $Dbeam1*$Wbeam1];
set Ibeam1 [expr $kbeam*$Wbeam1*pow($Dbeam1,3.0)/12.0];

# Beams axis 2
set Dbeam2 0.16;
set Wbeam2 6.0;
set Abeam2 [expr $Dbeam2*$Wbeam2];
set Ibeam2 [expr $kbeam*$Wbeam2*pow($Dbeam2,3.0)/12.0];

# Beams axis 3
set Dbeam3 0.16;
set Wbeam3 2.0;
set Abeam3 [expr $Dbeam3*$Wbeam3];
set Ibeam3 [expr $kbeam*$Wbeam3*pow($Dbeam3,3.0)/12.0];

# Define rigid beam/column properties
set A_rigid 1.0e6;
set I_rigid 1.0e6;
set Econ_rigid $Ec_uc;

# Define geometric transformation for beam-column element command: 
# geomTransf Linear $transfTag <-jntOffset $dXi $dYi $dXj $dYj>
set BeamTransTag 1;
geomTransf Linear $BeamTransTag;

# Assign beam elements command: element elasticBeamColumn $eleID $iNode $jNode $A $E $I $transfID
for {set i 1} {$i <= $numStories} {incr i} { 

	# Eje 1
	element elasticBeamColumn [expr 2000 + $i] [expr 100 + $WallElPerStory*$i] \
	[expr 200 + $i] $A_rigid $Econ_rigid $I_rigid $BeamTransTag; # 100x - Rigid beam
	element elasticBeamColumn [expr 2100 + $i] [expr 200 + $i] [expr 300 + $i] \
	$Abeam1 $Ec_uc $Ibeam1 $BeamTransTag;
	element elasticBeamColumn [expr 2200 + $i] [expr 300 + $i] [expr 400 + \
	$WallElPerStory*$i] $A_rigid $Econ_rigid $I_rigid $BeamTransTag; # 120x - Rigid beam 

	# Eje 2
	element elasticBeamColumn [expr 3000 + $i] [expr 500 + $WallElPerStory*$i] [expr \
	600 + $i] $A_rigid $Econ_rigid $I_rigid $BeamTransTag; # 200x - Rigid beam
	element elasticBeamColumn [expr 3100 + $i] [expr 600 + $i] [expr 700 + $i] \
	$Abeam2 $Ec_uc $Ibeam2 $BeamTransTag;
	element elasticBeamColumn [expr 3200 + $i] [expr 700 + $i] [expr 800 + \
	$WallElPerStory*$i] $A_rigid $Econ_rigid $I_rigid $BeamTransTag; # 220x - Rigid be

	# Eje 3
	element elasticBeamColumn [expr 4000 + $i] [expr 900 + $WallElPerStory*$i] [expr 1000 + \
	$i] $A_rigid $Econ_rigid $I_rigid $BeamTransTag; # 300x - Rigid beam
	element elasticBeamColumn [expr 4100 + $i] [expr 1000 + $i] [expr 1100 + $i] \
	$Abeam3 $Ec_uc $Ibeam3 $BeamTransTag;
	element elasticBeamColumn [expr 4200 + $i] [expr 1100 + $i] [expr 1200 + $i] \
	$Abeam3 $Ec_uc $Ibeam3 $BeamTransTag; 
	element elasticBeamColumn [expr 4300 + $i] [expr 1200 + $i] [expr 1300 + $i] \
	$Abeam3 $Ec_uc $Ibeam3 $BeamTransTag;
	element elasticBeamColumn [expr 4400 + $i] [expr 1300 + $i] [expr 1400 + \
	$WallElPerStory*$i] $A_rigid $Econ_rigid $I_rigid $BeamTransTag; 
}

# Define column sections & assign 
set kcol 0.7;
set Dcol 0.3; # Wall depth
set Wcol 5.5; # Wall width
set Acol [expr $Dcol*$Wcol];
set Icol [expr $kcol*$Wcol*pow($Dcol,3.0)/12.0];

# Define geometric transformation for beam-column element command: 
# geomTransf Linear $transfTag <-jntOffset $dXi $dYi $dXj $dYj>
set ColTransTag 2;
geomTransf Linear $ColTransTag;

# Assign column elements command: 
# element elasticBeamColumn $eleID $iNode $jNode $A $E $I $transfID
for {set i 1} {$i <= $numStories} {incr i} { 
	element elasticBeamColumn [expr 1100 + $i] [expr 1100 + $i - 1] [expr 1100 + $i] $Acol \
	$Ec_uc $Icol $ColTransTag; 
	element elasticBeamColumn [expr 1200 + $i] [expr 1200 + $i - 1] [expr 1200 + $i] $Acol \
	$Ec_uc $Icol $ColTransTag; 
}


# ###########################################################################
# Gravity Loads & Gravity Analysis
# ###########################################################################

# Define gravity loads
set P1 0.254; 
set P2 0.4939;
set P3 0.2191;
set P4 0.2501;

# Apply gravity loads
# Construct a time series where load factor applied is linearly proportional to the time domain command: 
# pattern PatternType $PatternID TimeSeriesType
pattern Plain 1 "Linear" {
	# Nodal load on walls - Command: load nodeID xForce yForce
	 # Note: 1.157 is eccentricity between Lw/2 and centroid
	for {set i 1} {$i <= $numStories} {incr i} { 
		load [expr 100 + $WallElPerStory*$i] 0.0 -$P1 0.0;
		load [expr 400 + $WallElPerStory*$i] 0.0 -$P1 0.0;
		load [expr 500 + $WallElPerStory*$i] 0.0 -$P2 [expr -1.157*$P2]; 
		load [expr 800 + $WallElPerStory*$i] 0.0 -$P2 [expr 1.157*$P2];
		load [expr 900 + $WallElPerStory*$i] 0.0 -$P3 0.0;
		load [expr 1100 + $i] 0.0 -$P4 0.0;
		load [expr 1200 + $i] 0.0 -$P4 0.0;
		load [expr 1400 + $WallElPerStory*$i] 0.0 -$P3 0.0;
	}
}

# Gravity-analysis: load-controlled static analysis
set Tol 1.0e-6;
set NstepGravity 10;
set DGravity [expr 1.0/$NstepGravity];
constraints Plain;
numberer RCM;
system BandGeneral;
test NormDispIncr $Tol 6;
algorithm Newton;
integrator LoadControl $DGravity;
analysis Static;
analyze $NstepGravity;
