#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "apolloData.h"
#include "nasaNonApolloAstroPre1970.h"
#include "astroOnp.h"

// A few methodological notes.
// 73 people, including military astronauts who transferred into NASA, 
// can be considered to be pre-1970 NASA astronauts. However, quite a 
// few (iirc, 8) passed away in accidents during training or off-base.
// Including these in the mc analysis fundamentally skews the pool and
// it's not reflective of reality; i.e. these astronauts couldn't have been
// selected at the time.
//
// However, mostly because I'm a novice programmer who doesn't want to rely
// too much on the machine, then 

// Here's the structure of the nasa astro struct;
// struct nasaAstronaut {
// 	char name[128];
// 	int birthYear;
// 	int deathYear; 
// 	bool lunar;   		--- did they go to the moon at all?
// 	bool stroll;   		--- did they walk on the moon?
// 	bool leo;   		--- did they go to space? (for broader compatibility)
// 	bool trainAcc;  	--- did they die in a training accident?
// 	bool hitEighty; 	--- did they hit 80?
// 	bool spaceGrandpa; 	--- hitEighty == True were they space grandpas?
// };

#define runSize 1000000 // first we specify the size of the run

struct astroLedger{
	int numGrandpa;				// The number of space grandpas in this deck
	int hit80;					// How many people either reached or passed the age of 80?
	int medianAge;				// Median age of the deck.
	double deckSMR;				// against normies
	int index;					// for later iteration / manipulation
};

void printAstro(struct nasaAstronaut astro, int position){
	printf("\n# %d \t %s", position, astro.name);
}

void ageSelectSort(int toSortArray[], int counter){	

	int swapBuffer = 0;
	int candidateIndex = 0;


	 for (int arrayIterate = 0; arrayIterate < counter; arrayIterate++){
	 	
	 	candidateIndex = arrayIterate;
	 	for ( int sortIterate = (arrayIterate + 1); sortIterate < counter; sortIterate++ )
	 		if ( toSortArray[sortIterate] < toSortArray[candidateIndex] )
	 			candidateIndex = sortIterate;	 	

		// at this point we've found the smallest number between now and the end
		// let's swap!
 		if(candidateIndex == arrayIterate)
			continue;

 		swapBuffer 					 = 	toSortArray[candidateIndex];
 		toSortArray[candidateIndex]  = 	toSortArray[arrayIterate];
 		toSortArray[arrayIterate]	 =	swapBuffer;	 	
	 }
}

void fileWrite(const struct astroLedger resultsArray[], const int size, const int seed){
	FILE *resultsFile = fopen("astronaut-monte-carlo-results.tsv", "w");
	fprintf(resultsFile,"# seed number, %d\n\n", seed);
	fprintf(resultsFile, "Deck Index\tNumber of Space Grandpas\tNumber who reached Age 80\tMedian Group Age\tSMR v US Census\n");

	for(int writeIterator = 0; writeIterator < size; writeIterator++){
		fprintf(resultsFile, "%d\t%d\t%d\t%d\t%f\n", resultsArray[writeIterator].index, resultsArray[writeIterator].numGrandpa, 
			resultsArray[writeIterator].hit80, resultsArray[writeIterator].medianAge, resultsArray[writeIterator].deckSMR);
	}
	fclose(resultsFile);
}


int main(){

	int timeSeed = 424242; /* REFEREE COPY: fixed to the recorded seed */
	// Technically this is living in sin, because it's not truly random, but
	// pure randomness doesn't really matter for my use case?

	srand(timeSeed);

	printf("The seed is, %d", timeSeed);

	int astroDeckSize = 0;
	astroDeckSize = nasaAstrosCount + apolloAstrosCount;

	struct nasaAstronaut astroDeck[astroDeckSize];	

	printf("\n\n=====---===== straight deck =====---===== \n\n");

	for (int iterator = 0; iterator < astroDeckSize; iterator++){
		// behold we zip merge!
		if (iterator <= (apolloAstrosCount - 1)){
			astroDeck[iterator] = apolloAstros[iterator];
		}
		if ((iterator >= apolloAstrosCount) && (iterator < (nasaAstrosCount + apolloAstrosCount))){
			astroDeck[iterator] = nasaAstros[(iterator-apolloAstrosCount)];
		}
		printAstro(astroDeck[iterator], iterator);
	}


	

	struct nasaAstronaut possibleApollo[29];

	// start of the monte carlo

	static struct astroLedger mcOutput[runSize]; // output goes here. McScience for y'all

	for (int monteTheCarlo = 0; monteTheCarlo < runSize; monteTheCarlo++) {

		// astroDeck has 73 astronauts in it. It's time to shuffle the shuffle.

		// DECK SHUFFLE
		for (int backIterator = (astroDeckSize - 1); backIterator > 0; backIterator--){		
			int randomInt = rand() % (backIterator + 1); // without the +1, when we are at position 70 on the 0 indexed array, 
														// it's not possible to get 70. Therefore, 73x fewer permutations

			struct nasaAstronaut astroSwap = astroDeck[randomInt];
			astroDeck[randomInt] = astroDeck[backIterator];
			astroDeck[backIterator] = astroSwap;
		}

		//
		// Making the synthetic cohort.
		// Care needs to be taken while making this cohort;
		// 

		int shuffleIterate = 0;
		int possibleApolloIndex = 0;		

		// MAKING SHUFFLED APOLLO DECK
		while(possibleApolloIndex < 29){

			//
			// this should be "obvious" but it often isn't, but in general, the pool of astronauts who 
			// got to participate in Apollo were the survivors who didn't die in a training accident / pre-1970
			// weren't excluded via accident.
			// 
			// Therefore to resemble the possibilities available at the time, we're skipping past people who 
			// died during training
			//
			// note - hard coded to 1970 because there are no deaths post 1970
			// also sweeps a handful of car accidents into the same category. trainAcc = death during training
			//

			bool trainingAccident = astroDeck[shuffleIterate].trainAcc;

			if(trainingAccident){
				shuffleIterate++;
				continue;			
			} else {
				possibleApollo[possibleApolloIndex] = astroDeck[shuffleIterate];
				shuffleIterate++;
				possibleApolloIndex++;
				continue;
			}
		}

		//
		// Let's process the results!! Extremely simple, we're going to iterate over the deck, and do the calcs.
		//

		struct astroLedger strangeResults = {0, 0, 0, 0, monteTheCarlo};
		int astroAgeArray[29] = {0};

		//
		// Iterating through the synthetic cohort
		//

		// SHUFFLED DECK ITERATION
		for(int printIterator = 0; printIterator < 29; printIterator++){
			// Keeping track of the space grandpas			
			if (possibleApollo[printIterator].hitEighty){			
				strangeResults.hit80++;

				if (possibleApollo[printIterator].spaceGrandpa)
					strangeResults.numGrandpa++;
			}

			// let's track age!!
			// this is harder than you'd think as I with totally impressive
			// foresight didn't add age to the raw data.
			//
			// More honestly, I didn't want to add age to the astro data as that's
			// a calculation that can change depending on how you slice it.
			//
			// Hence we need to figure out their age first.
			//

			// AGE ARRAY
			if (possibleApollo[printIterator].deathYear)
				astroAgeArray[printIterator] = possibleApollo[printIterator].deathYear - possibleApollo[printIterator].birthYear;
			else
				astroAgeArray[printIterator] = 2026 - possibleApollo[printIterator].birthYear;
			}

		ageSelectSort(astroAgeArray, 29);
		strangeResults.medianAge = astroAgeArray[14];	// Median literally means middle most value...
														// for a batch of 29 that's 14 or 15

		char deckLabel[20];
		snprintf(deckLabel, 20, "Deck #%d", monteTheCarlo);

		strangeResults.deckSMR = calculateSMR(possibleApollo, 29, deckLabel);

		mcOutput[monteTheCarlo] = strangeResults;
		printf("\n\nGrandpa count = %d", strangeResults.numGrandpa);
	} // end of Monte Carlo loop
	fileWrite(mcOutput, runSize, timeSeed);
}