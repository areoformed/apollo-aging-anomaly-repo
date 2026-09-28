#ifndef nasaAstroStructDef
#define nasaAstroStructDef

#include <stdbool.h>

// this is a TERRIBLE name for this struct
// my perfectionism creates the desire in me to change this 
// but gotta ship :(

struct astroApolloSMR {
 char name[128];
 int birthYear;
 int deathYear; 
 bool lunar;   // did they go to the moon at all?
 bool stroll;   // did they walk on the moon?
 bool leo;   // did they go to space? (for broader compatibility)
 bool trainAcc;  // did they die in a training accident?
};

#endif