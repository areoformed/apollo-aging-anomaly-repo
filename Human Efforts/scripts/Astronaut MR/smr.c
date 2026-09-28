#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include "apolloData.h"
#include "1930CohortSSAData.h"
#include "nasaNonApolloAstroPre1970.h"

const int studyYear = 2026; // Defining closest convenient date, June 1st, 2026 as epoch. Redefined from Jan, 2025
const int assumedSelectAge = 30; // the point at which the analysis starts


double calculateSMR(const struct astroApolloSMR inputCohort[], int count, const char *label){

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

		struct astroApolloSMR astro = inputCohort[iterator];

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

// oh my god... this is such a hack.
// We're relying on the fact that C passes memory locations not variables
// aka bad baaaaad code

int filterCohort(
	const struct astroApolloSMR dataToFilter[], 
	int preFilterCount, 
	struct astroApolloSMR postFilter[],
	bool trainAccFlag)
{
	int kept = 0;

	for(int iterator = 0; iterator < preFilterCount; iterator++){
		
		if(trainAccFlag && dataToFilter[iterator].trainAcc){
			continue; // Basically if they died in a training accident, let's continue this
		}

		postFilter[kept] = dataToFilter[iterator];
		kept++;

	}
	return kept;

}


int main(void){

	// Let's run the calc for Apollo Astronauts
	double apolloSMR = calculateSMR(apolloAstros, apolloAstrosCount, "Apollo Only");

	// Non-Apollo NASA astronauts
	double nasaOtherAstroSMR = calculateSMR(nasaAstros, nasaAstrosCount, "Rest of NASA");

	// Basically they're from the same period and we're comparing them to the same reference population
	// and so we can essentially just use this as a shortcut instead odoing
	double smrRatioApolloToNasa = apolloSMR / nasaOtherAstroSMR;

	// But there's a confounding factor here. :) 
	// When we count the people who died in the training accidents, 
	// we're making a fair comparison against the general population, 
	// but it's not a fair comparison for Apollo
	// Only the survivors got to be a part of Apollo

	struct astroApolloSMR nasaAstroSurvivorGroup[100]; // hacky will write explanation later, which will never happen...
	// C works in defined memory units. As the total amount of astronauts never exceeds 100
	// Therefore, without biasing ourselves that can be 100

	int survivorCount = filterCohort(
		nasaAstros,
		nasaAstrosCount,
		nasaAstroSurvivorGroup,
		true);

	double cleanedNasaAstroSMR = calculateSMR(nasaAstroSurvivorGroup, survivorCount, "The no Accidents NASA Cohort");

	double cleanRatio = apolloSMR / cleanedNasaAstroSMR;
	

	printf("\n\n Final Count.\n\n");
	printf("The SMR for Apollo astronauts = %f\n", apolloSMR);
	printf("The SMR for other NASA astronauts = %f\n\n", nasaOtherAstroSMR);
	printf("Running the dirty comparison = %f", smrRatioApolloToNasa);
	printf("\n\n====================\n\n");
	printf("The corrected NASA Cohort smr = %f\n", cleanedNasaAstroSMR);
	printf("\n\n Tada! The correct ratio is, %f", cleanRatio);
}

