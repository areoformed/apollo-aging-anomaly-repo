#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "./Machine Efforts/toy problem/toy-deck-73.h"

void main(){
	// Technically this is living in sin, because it's not truly random, but
	// pure randomness doesn't really matter for my use case?

	srand(time(NULL));

	int deckSize = 0;
	deckSize = sizeof(deck)/sizeof(deck[0]); // fixed pre-allocated size in memory, so easy to get this

	int randomOrder[deckSize];

	for (int iterator = 0; iterator < deckSize; iterator++){
		randomOrder[iterator] = iterator;
		printf("assigned, %d \n", randomOrder[iterator]);
	}

	printf("\n\n second loop \n\n");

	for (int secondIterator = (deckSize - 1); secondIterator >= 0; secondIterator--) {
		int randomInt = rand() % (secondIterator + 1);
		int tempShuffle = randomOrder[secondIterator];
		randomOrder[secondIterator] = randomOrder[randomInt];
		randomOrder[randomInt] = tempShuffle;
		printf("second loop assigned, %d \n", randomOrder[secondIterator]);
	}

	printf("roll call = %d", deckSize);
}