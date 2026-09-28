#
# These are astronauts who were selected by NASA pre-1970 who
# didn't fly under Apollo. Some of these astronauts flew under
# Project Mercury, Gemini (and/or) Shuttle. Others never flew at
# all. They are meant to provide a useful comparator to the Apollo
# dataset.
#

import os
import csv
from datetime import date

def returnGroupInt(groupString):
	atomizedString = groupString.split()
	return(int(atomizedString[1])) # takes advantage of the fact that Claude wrote the groups as, Group N


# the meat and potatoes of it, starting the header file as string,

nonApolloAstroBlob = """
#include <stdbool.h>
#include "nasaAstroStructDef.h"

static struct astroApolloSMR nasaAstros[] = {
"""

#
# From Claude's and 5.5's dataset, this is the path + structure 
# 
# 'Machine Efforts/Claude Compiled - Opus 4-6 and GPT 5-5 Processed Data/Final - Analysis - Enriched Datasets/03E-non-apollo-enriched.tsv'
#      0 Name, 1 Astronaut Group, 2 Date of Birth, 3 Date of Selection, 4 Age at Selection, 
# 5 Went to Space, 6 Moonwalker, 7 Missions Flown, 8 Number of Flights, 9 Time in Space, 
# 10 Date of Death, 11 Current Age or Age at Death, 12 Status, 13 Accidental Death, 
# 14 Mort / cause note, 15 Space Grandpa, 16 Space Grandpa Citation, 17 Military Branch, 
# 18 Pre-NASA Career, 19 Education, 20 Post-NASA Career, 21 Birth Year, 22 Citations
# 
# From Fable's dataset,
# 'Machine Efforts/Fable Replication/Fable 5 – One Shot Data - Analysis/apollo_era_astronaut_cohort_v2.csv'
#    ———— subtract columns by 1 for 0 index
#  1 full_name 2 cohort 3 nasa_group 4 birth_date 5 death_date 6 vital_status_20260601 7 apollo_missions 
# 8 first_spaceflight_year 9 birth_source_url 10 death_source_url 11 confidence 12 notes 
# 13 cognitive_status_20260601 14 documentation_depth 15 cognitive_source_url 16 cognitive_notes
#

claudeNasaAstrosTSV = open('./Machine Efforts/Claude Compiled - Opus 4-6 and GPT 5-5 Processed Data/Final - Analysis - Enriched Datasets/03E-non-apollo-enriched.tsv', newline='')
fableNasaAstrosCSV = open('./Machine Efforts/Fable Replication/Fable 5 – One Shot Data - Analysis/apollo_era_astronaut_cohort_v2.csv', newline='')

# Separating them into two because the filenames are so long

claudeNasaAstros = list(csv.reader(claudeNasaAstrosTSV, delimiter='\t'))
fableNasaAstros = list(csv.reader(fableNasaAstrosCSV, delimiter=','))

claudeNasaAstrosHeaders = claudeNasaAstros.pop(0)
fableNasaAstrosHeaders = fableNasaAstros.pop(0)

#
# making two dictionaries and seeing what the results are:
#
# Just a note, this wasn't supposed to be kabuki, but rather
# I wanted to write in a way where I knew that the data generated
# by different machine models (Opus, Fable, GPT 5.5, GPT 5.6) didn't
# have an obvious issue that was overlooked by checking the one fact
# that I do know --- there were 44 other astronauts.
#
# Rest is hand checking / sanity checking
#

lookupClaudeAstros = {}
lookupFableAstros = {}

for astro in claudeNasaAstros:	
	claudeAstroFingerprint =  (astro[2], returnGroupInt( astro[1]))
	lookupClaudeAstros[claudeAstroFingerprint] = astro	

for astro in fableNasaAstros:
	if astro[1] != "APOLLO_FLEW":
		fableAstroFingerprint = (astro[3],int(astro[2]))
		lookupFableAstros[fableAstroFingerprint] = astro


fableNonApolloRows = sum(1 for astro in fableNasaAstros if astro[1] != "APOLLO_FLEW")

print("The number of rows for the Claude datast is, ", len(claudeNasaAstros), " and the number of fingerprints are ", len(lookupClaudeAstros))
print("And for Fable's dataset the number of rows is, ", fableNonApolloRows, " and the number of fingerprints are ", len(lookupFableAstros))

if (set(lookupClaudeAstros) == set(lookupFableAstros)):

	keepingCount = 0 		# Yeah... I could do a len... but why not?

	for (birthDate, groupNum), astro in lookupFableAstros.items():
		name = astro[0].replace('"', '\\"')
		# identical as the other files
		# the replace " with \\" means that it won't throw errors as a header in C if someone's nickname is there like "Buzz"
		# note: implemented this rule with Claude's help.

		birthYear = date.fromisoformat(birthDate).year

		if astro[4] != '':
			deathYear = date.fromisoformat(astro[4]).year
		else:
			deathYear = 0

		lunar = 'false' 	# known because this is the NON Apollo dataset
		stroll = 'false'	# same as the above

		if astro[7] == '': 	# nothing usually means they never flew, note will change from dataset to dataset
			leo = 'false'
		else:
			leo = 'true'

		# this check SHOULD catch all the training accidents...

		if deathYear <= 1970 and deathYear != 0:
			trainAcc = 'true'
		else:
			trainAcc = 'false'

		effString = f'	{{"{name.strip()}", {birthYear}, {deathYear}, {lunar}, {stroll}, {leo}, {trainAcc}}},\n'

		nonApolloAstroBlob = nonApolloAstroBlob + effString

		keepingCount += 1

	nonApolloAstroBlob = nonApolloAstroBlob + '};\n'
	nonApolloAstroBlob = nonApolloAstroBlob + '\n' + f'#define nasaAstrosCount {keepingCount}'

	with open('./Human Efforts/scripts/nasaNonApolloAstroPre1970.h', 'w') as output:
		output.write(nonApolloAstroBlob)




