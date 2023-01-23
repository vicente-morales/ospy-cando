# ----------------------------------------------------------------
# Incremental Dynamic Analysis
# ----------------------------------------------------------------
wipe all;
wipeAnalysis;
# Set star time
set startTime [clock clicks -milliseconds]

# Define factores de escala para el IDA
# set IDA_factor [list 0.05 0.1 0.15 0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95 1];
set IDA_factor [list 0.1 0.5 1];

# Ingresa cada sismo a analizar 
set GM_file {GM_SURDEPERU2001_ARICA_COSTANERA_SN_5004_L.txt};
set GM_dt [list 0.005];
set GM_NP [list 15236];
set GM_SaT1 [list 163.941];

# Crea carpeta para guardar los resultados
set dataDir "OUT";
file mkdir $dataDir;

# Abre archivo LOG para información de la corrida
set FileName "LOG_$GM_file";
set fileId [open $dataDir/$FileName "w"];

# Escribe información de la corrida
puts $fileId "IDA factors............ $IDA_factor"
puts $fileId "Registro............... $GM_file"
puts $fileId "Incremento de tiempo... $GM_dt"
puts $fileId "Número de puntos....... $GM_NP"
puts $fileId "SaT1................... $GM_SaT1"
puts $fileId ""

set ok_IDA 0;
foreach GMfile $GM_file DtSeries $GM_dt NSteps $GM_NP SaT1 $GM_SaT1 {
	set ok_GM 0;
	set numNoConv 0;
	foreach IDA_SF $IDA_factor {
		
		puts $fileId "Analizando $GMfile para un SaT1= $IDA_SF g"

		# Perform gravity & modal analysis. Define Rayleigh Parameters
		source MODAL_00.tcl

		# First, set gravity loads acting constant and time in domain to 0.0
		loadConst -time 0.0


		# ###############################################################
		# Recorders 
		# ###############################################################
		
		# Record floor displacement & rotations
		set LengthString [string length $GMfile]
		set GM_Name [string range $GMfile 0 [expr $LengthString-5]]
		set FileName "Disp_${GM_Name}_${IDA_SF}"
		recorder Node -file $dataDir/$FileName.out -time -node 102 104 106 108 110 112 114 116 118 120 122 124 126 128 130 132 134 136 138 140 -dof 1 disp;
		set FileName "Rot_${GM_Name}_${IDA_SF}"
		recorder Node -file $dataDir/$FileName.out -time -node 102 104 106 108 110 112 114 116 118 120 122 124 126 128 130 132 134 136 138 140 -dof 3 disp; 

		# Strains wall P1, all stories
		# set FileName "strainP1i_Story_${GM_Name}_${IDA_SF}"
		# recorder Element -file $dataDir/$FileName.out -time -eleRange 101 140 fiber_strain;
		# set FileName "strainP1d_Story_${GM_Name}_${IDA_SF}"
		# recorder Element -file $dataDir/$FileName.out -time -eleRange 401 440 fiber_strain;

		# Strains wall P2, all stories
		# set FileName "strainP2i_Story_${GM_Name}_${IDA_SF}"
		# recorder Element -file $dataDir/$FileName.out -time -eleRange 501 540 fiber_strain; 
		# set FileName "strainP2d_Story_${GM_Name}_${IDA_SF}"
		# recorder Element -file $dataDir/$FileName.out -time -eleRange 801 840 fiber_strain; 

		# Strains wall P3, all stories
		# set FileName "strainP3i_Story_${GM_Name}_${IDA_SF}"
		# recorder Element -file $dataDir/$FileName.out -time -eleRange 901 940 fiber_strain; 
		# set FileName "strainP3d_Story_${GM_Name}_${IDA_SF}"
		# recorder Element -file $dataDir/$FileName.out -time -eleRange 1401 1440 fiber_strain; 


		# ##################################################################
		# Define ground motion & create load pattern 
		# ##################################################################
		
		# Ground motion scaling factor. Record units: cm/s2
		set Scalefactor [expr $IDA_SF/$SaT1*9.80665];
		
		set DtAnalysis $DtSeries;
		# Time-step Dt for lateral analysis
		set TmaxAnalysis [expr $DtSeries*$NSteps];

		# Define the acceleration series for the ground motion
		set accelSeries "Series -dt $DtSeries -filePath $GMfile -factor $Scalefactor";

		# Create load pattern: apply acceleration to all fixed nodes with UniformExcitation
		set GMdirection 1;
		pattern UniformExcitation 5 $GMdirection -accel $accelSeries;


		# ################################################################
		# Perform Time History Analysis
		# ################################################################
		
		# Define parameters for transient analysis
		set TolPred 1.0e-4; # Default tolerance
		set lisTol [list 1.0e-3 1.0e-2 1.0e-1]; # Additional tolerance
		# set NumIterMin 10; # Minimum iterations number
		set NumIterMax 1000; # Maximum iterations number
		set NumIterPred 100; # Default iterations number
		set printFlag 0; # Print convergence information flag
		set TestType NormDispIncr; # Test type

		# Algorithm
		set algorithmType Newton;

		# Newmark-integrator parameters 
		set NewmarkGamma 0.5;
		set NewmarkBeta 0.25;
		
		constraints Transformation;
		numberer RCM;
		system BandGeneral;
		test $TestType $TolPred $NumIterPred $printFlag;
		algorithm $algorithmType -initial; 
		integrator Newmark $NewmarkGamma $NewmarkBeta;
		analysis Transient;

		# Begin transient analyisis
		set ok 0
		set controlTime [getTime];
		
		while {$controlTime < $TmaxAnalysis && $ok == 0} {
			
			set ok [analyze 1 $DtAnalysis]
			
			if {$ok != 0} {
			
				foreach Tol $lisTol {
					
					puts ""
					puts "Trying Newton -initial $Tol .."
					test $TestType $Tol $NumIterMax $printFlag;
					algorithm $algorithmType -initial
					set ok [analyze 1 $DtAnalysis]
					
					if {$ok != 0} {
						puts "Trying ModifiedNewton $Tol .."
						test $TestType $Tol $NumIterPred $printFlag
						algorithm ModifiedNewton 
						set ok [analyze 1 $DtAnalysis]
					}
					if {$ok != 0} {
						puts "Trying Broyden $Tol .."
						algorithm Broyden 8
						set ok [analyze 1 $DtAnalysis]
					}
					if {$ok != 0} {
						puts "Trying NewtonWithLineSearch $Tol .."
						algorithm NewtonLineSearch .8
						set ok [analyze 1 $DtAnalysis]
					}
					if {$ok != 0} {
						puts "Trying BFGS $Tol .."
						algorithm BFGS
						set ok [analyze 1 $DtAnalysis]
					}
					if {$ok == 0} {
						puts ""
						puts "***** It worked .. return algotithm default"
						puts ""
						test $TestType $TolPred $NumIterMax $printFlag
						algorithm $algorithmType -initial
						if {$Tol > 1.0e-3} {puts $fileId "Tol = $Tol worked at Time= $controlTime"}
						break
					}
				}
			}
			# set controlTime [getTime]
			# puts "Analizando $GMfile para un SaT1= $IDA_SF g Current time = $controlTime"
		}

		# Display whether INDIVIDUAL analysis was successful
		if {$ok == 0} {
			set numNoConv 0
			#puts "\nAnalysis for $GMfile completed SUCCESSFULLY";
			#puts ""
		} else {
			puts "\nIDA Analysis for $GMfile FAILED. SaT1= $IDA_SF g, Time = $controlTime"; # Show information on screen
			puts ""
			puts $fileId "IDA Analysis for $GMfile FAILED. SaT1= $IDA_SF g, Time = $controlTime"; # Save information on file LOG 
			puts $fileId ""
			set ok_GM 1
			set ok_IDA 1
			set numNoConv [expr $numNoConv + 1]
		}


		# If twenty runs do not converge then run another earthquake
		if {$numNoConv == 20} {
			puts "\nATTENTION: Twenty runs do not converge. Analysis discontinued";
			# Show information on screen
			puts ""
			puts $fileId "ATTENTION: Ten runs do not converge. Analysis discontinued";
			# Save information on file LOG 
			puts $fileId ""
			break
		}
	}

	# Display whether INDIVIDUAL analysis was successful
	if {$ok_GM == 0} {
		puts ""
		puts "\nIDA Analysis for $GMfile completed SUCCESSFULLY";
		puts ""
		puts $fileId ""
		puts $fileId "IDA Analysis for $GMfile completed SUCCESSFULLY";
		puts $fileId ""
	} else {
		puts "\nIDA Analysis for $GMfile FAILED";
		puts ""
		puts $fileId "IDA Analysis for $GMfile FAILED";
		puts $fileId ""
	}
}

# Display whether GLOBAL analysis was successful
if {$ok_IDA == 0} {
	puts "\nIDA Done";
	puts $fileId "IDA Done";
} else {
	puts "\nIDA Failed";
	puts $fileId "IDA Failed";
}

# Final time
set finishTime [clock clicks -milliseconds];
set Time [expr ($finishTime-$startTime)/1000.]; # Total time in sec
set TimeHr [expr int(floor($Time/3600.))]; # Complete hours
set TimeMin [expr int(floor($Time/60.-$TimeHr*60))]; # Remaining complete minutes
set TimeSec [expr int($Time-$TimeHr*3600-$TimeMin*60)]; # Remaining seconds
puts "\n\t\tTOTAL TIME: $TimeHr : $TimeMin : $TimeSec";
puts $fileId "TOTAL TIME: $TimeHr : $TimeMin : $TimeSec";

# Close file LOG 
close $fileId