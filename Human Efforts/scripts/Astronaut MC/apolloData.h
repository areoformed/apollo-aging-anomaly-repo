#include <stdbool.h>
#include "nasaAstroStructDefv2.h"

static struct nasaAstronaut apolloAstros[] ={ 

	{"Neil Armstrong", 1930, 2012, true, true, true, false, true, true},
	{"Buzz Aldrin", 1930, 0, true, true, true, false, true, true},
	{"Pete Conrad", 1930, 1999, true, true, true, false, false, false},
	{"Alan Bean", 1932, 2018, true, true, true, false, true, true},
	{"Alan Shepard", 1923, 1998, true, true, true, false, false, false},
	{"Edgar Mitchell", 1930, 2016, true, true, true, false, true, false},
	{"David Scott", 1932, 0, true, true, true, false, true, true},
	{"James Irwin", 1930, 1991, true, true, true, false, false, false},
	{"John Young", 1930, 2018, true, true, true, false, true, true},
	{"Charles Duke", 1935, 0, true, true, true, false, true, true},
	{"Eugene Cernan", 1934, 2017, true, true, true, false, true, true},
	{"Harrison Schmitt", 1935, 0, true, true, true, false, true, true},
	{"Frank Borman", 1928, 2023, true, false, true, false, true, true},
	{"Jim Lovell", 1928, 2025, true, false, true, false, true, true},
	{"Bill Anders", 1933, 2024, true, false, true, false, true, true},
	{"Tom Stafford", 1930, 2024, true, false, true, false, true, true},
	{"Michael Collins", 1930, 2021, true, false, true, false, true, true},
	{"Dick Gordon", 1929, 2017, true, false, true, false, true, true},
	{"Jack Swigert", 1931, 1982, true, false, true, false, false, false},
	{"Fred Haise", 1933, 0, true, false, true, false, true, true},
	{"Stuart Roosa", 1933, 1994, true, false, true, false, false, false},
	{"Alfred Worden", 1932, 2020, true, false, true, false, true, true},
	{"Ken Mattingly", 1936, 2023, true, false, true, false, true, false},
	{"Ronald Evans", 1933, 1990, true, false, true, false, false, false},
	{"Walter M. Schirra Jr.", 1923, 2007, false, false, true, false, true, true},
	{"Donn F. Eisele", 1930, 1987, false, false, true, false, false, false},
	{"R. Walter Cunningham", 1932, 2023, false, false, true, false, true, false},
	{"James A. McDivitt", 1929, 2022, false, false, true, false, true, true},
	{"Russell L. \"Rusty\" Schweickart", 1935, 0, false, false, true, false, true, true},
};

#define apolloAstrosCount 29