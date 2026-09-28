#ifndef nasaAstroStructDef
#define nasaAstroStructDef

#include <stdbool.h>

// 
// Updated name. This won't be true if / when expanded to military astronauts
// 

struct nasaAstronaut {
 char name[128];
 int birthYear;
 int deathYear; 
 bool lunar;   		// did they go to the moon at all?
 bool stroll;   	// did they walk on the moon?
 bool leo;   		// did they go to space? (for broader compatibility)
 bool trainAcc;  	// did they die in a training accident?
 bool hitEighty;	// did they hit 80?
 bool spaceGrandpa; // hitEighty == True were they space grandpas?
};

#endif