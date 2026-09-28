#include <stdbool.h>
#include "nasaAstroStructDef.h"

static struct astroApolloSMR apolloAstros[] ={ 

	{"Neil Armstrong", 1930, 2012, true, true, true, false},
	{"Buzz Aldrin", 1930, 0, true, true, true, false},
	{"Pete Conrad", 1930, 1999, true, true, true, false},
	{"Alan Bean", 1932, 2018, true, true, true, false},
	{"Alan Shepard", 1923, 1998, true, true, true, false},
	{"Edgar Mitchell", 1930, 2016, true, true, true, false},
	{"David Scott", 1932, 0, true, true, true, false},
	{"James Irwin", 1930, 1991, true, true, true, false},
	{"John Young", 1930, 2018, true, true, true, false},
	{"Charles Duke", 1935, 0, true, true, true, false},
	{"Eugene Cernan", 1934, 2017, true, true, true, false},
	{"Harrison Schmitt", 1935, 0, true, true, true, false},
	{"Frank Borman", 1928, 2023, true, false, true, false},
	{"Jim Lovell", 1928, 2025, true, false, true, false},
	{"Bill Anders", 1933, 2024, true, false, true, false},
	{"Tom Stafford", 1930, 2024, true, false, true, false},
	{"Michael Collins", 1930, 2021, true, false, true, false},
	{"Dick Gordon", 1929, 2017, true, false, true, false},
	{"Jack Swigert", 1931, 1982, true, false, true, false},
	{"Fred Haise", 1933, 0, true, false, true, false},
	{"Stuart Roosa", 1933, 1994, true, false, true, false},
	{"Alfred Worden", 1932, 2020, true, false, true, false},
	{"Ken Mattingly", 1936, 2023, true, false, true, false},
	{"Ronald Evans", 1933, 1990, true, false, true, false},
	{"Walter M. Schirra Jr.", 1923, 2007, false, false, true, false},
	{"Donn F. Eisele", 1930, 1987, false, false, true, false},
	{"R. Walter Cunningham", 1932, 2023, false, false, true, false},
	{"James A. McDivitt", 1929, 2022, false, false, true, false},
	{"Russell L. \"Rusty\" Schweickart", 1935, 0, false, false, true, false},
};

#define apolloAstrosCount 29