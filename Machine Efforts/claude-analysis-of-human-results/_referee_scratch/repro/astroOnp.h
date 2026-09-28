#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include "1930CohortSSAData.h"
//
// This is a copy-paste job of my code from Astronaut MR
//
// Note the copy-pasting includes the comments for later
// reading and reference.
//

const int studyYear = 2026; // Defining closest convenient date, June 1st, 2026 as epoch. Redefined from Jan, 2025
const int assumedSelectAge = 30; // the point at which the analysis starts


double calculateSMR(const struct nasaAstronaut inputCohort[], int count, const char *label){

	const int genPopDeathsInit = cohortData_1930[assumedSelectAge].numAlive; 	// allows me to change select age later if needed

	int iterator = 0;

	int observedDeaths = 0;						// So. How many folks died?
	double expectedDeaths = 0.0;				// If they were normies - group X how many do we EXPECT to have died?

	double talliedSMR = 0.0; 					// the number of merit

	while (iterator < count) {

		// making a copy of the Apollo astronaut struct --- not directly changing the data
		// struct definition pulled from the .h file
		// e.g. {"Neil Armstrong", 1930, 2012, true, true, false} 
		// name, birth death, went to moon?, walked on the moon?, died in a training accident?

		struct nasaAstronaut astro = inputCohort[iterator];

		int astroAge = 0; 				// This is meant to be a now recommended C pattern for local scoping

		if (astro.deathYear) { // works because I hardcoded <blank> year of death to 0 in the python pre-processing step
			observedDeaths++;
			astroAge = astro.deathYear - astro.birthYear;
		}
		else {
			astroAge = studyYear - astro.birthYear;
		}

		//
		// 
		expectedDeaths+= -log((double) cohortData_1930[astroAge].numAlive/genPopDeathsInit); 		

		// alright, -ln (alive/start) to get multiplier
		// replicates hand calc done with textbook + Claude's help
		// general note --- coercion to double for the division

		printf("Age %d for %s | ", astroAge, astro.name);	// now new and improved with pretty formatting!
		printf("at-risk window = [30, %d] | ", astroAge);
		printf("observedDeaths = %d\n", observedDeaths);
		iterator++;
	}

	talliedSMR = ((double)observedDeaths)/expectedDeaths;

	printf("\n========= %s =========\n", label);
	printf("\n\n\n Total Observed Deaths the loop saw %d; # of astronauts in the analysis, %d\n", observedDeaths, count);
	printf("\nUsing population data Expected Deaths were %f; \n\n =============SMR=============\n\n SMR = %f\n", expectedDeaths, talliedSMR);

	return(talliedSMR);
}
