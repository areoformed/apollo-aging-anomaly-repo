#include <stdio.h>
#include <stdbool.h>

struct astroApollo {
	char name[128];
	bool lunar;    // catch all for going to the moon 
	bool active;   // the morbid q
	bool stroll;   // Did they take a walk on the moon?
	bool space;    // for folks who didn't make it to the moon
	double age;    // age reached
};

int main(void){
	struct astroApollo Neil = {"Neil Armstrong", true, false, true, true, 82};

	printf("Kaplan Meir survival analysis with %s", Neil.name);
	return 0;
}