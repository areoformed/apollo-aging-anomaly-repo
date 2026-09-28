#
# These are astronauts who were selected by NASA pre-1970 who
# didn't fly under Apollo. Some of these astronauts flew under
# Project Mercury, Gemini (and/or) Shuttle. Others never flew at
# all. They are meant to provide a useful comparator to the Apollo
# dataset.
#
# This uses machine determinations that were spot checked by me. 
# The level of confidence for this file is low / lower than the 
# other ones. Manual effort / review is needed here to increase
# confidence.
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
#include "nasaAstroStructDefv2.h"

static struct nasaAstronaut nasaAstros[] = {
"""

# This builds on,
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

# removing the header rows from both and 
# dumping them into a variable. can be used for debugging
# most likely won't.
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
	claudeAstroFingerprint =  (astro[2], returnGroupInt( astro[1])) # as sol pointed out this isn't actually perfect, but not touching for now.
	lookupClaudeAstros[claudeAstroFingerprint] = astro	

for astro in fableNasaAstros:
	if astro[1] != "APOLLO_FLEW":
		fableAstroFingerprint = (astro[3],int(astro[2]))
		lookupFableAstros[fableAstroFingerprint] = astro


#
# steps for sanity checking what's being inputted for future work.
# 

fableNonApolloRows = sum(1 for astro in fableNasaAstros if astro[1] != "APOLLO_FLEW") #experiment in dissimilar redundancy
															# mostly for my amusement; it's the same operation performed twice
															# against the same source, but creates a sanity check in case I screw up
															# or, note - lookupFableAstros have the "right" subset i.e. non-Apollo only
															# so essentially checking are the lengths of the two the same? Or did I screw up?

print("The number of rows for the Claude datast is, ", len(claudeNasaAstros), " and the number of fingerprints are ", len(lookupClaudeAstros))
print("And for Fable's dataset the number of rows is, ", fableNonApolloRows, " and the number of fingerprints are ", len(lookupFableAstros))

setFable = set(lookupFableAstros)
setClaude = set(lookupClaudeAstros)

print("Set Fable - Set Claude =", (setFable-setClaude))
print("Set Claude - Set Fable = ", (setClaude-setFable))

if (set(lookupClaudeAstros) == set(lookupFableAstros)):

	keepingCount = 0 		# Yeah... I could do a len... but why not?

	for (birthDate, groupNum), astro in lookupClaudeAstros.items(): #switching to Claude's set because 3E has the better SG version.
		name = astro[0].replace('"', '\\"')
		# identical as the other files
		# the replace " with \\" means that it won't throw errors as a header in C if someone's nickname is there like "Buzz"
		# note: implemented this rule with Claude's help.

		birthYear = date.fromisoformat(birthDate).year

		if astro[10] != '':
			deathYear = date.fromisoformat(astro[10]).year
		else:
			deathYear = 0

		lunar = 'false' 	# known because this is the NON Apollo dataset
		stroll = 'false'	# same as the above

		if astro[5] == 'N': 	# nothing usually means they never flew, note will change from dataset to dataset
			leo = 'false'
		else:
			leo = 'true'

		# this check SHOULD catch all the training accidents...
		# while some died in car crashes. Most died in a T-38.
		# squashing all cases into training accident. Separate in the future
		# for greater fidelity.

		if deathYear <= 1970 and deathYear != 0:	
			trainAcc = 'true'
		else:
			trainAcc = 'false'

		reachedAge = round(float(astro[11])) # Dumping in number from, 11 Current Age or Age at Death

		if reachedAge >= 80:
			above_80 = 'true'
			# combining with space grandpa determination
			if astro[15] == 'Y':
				spaceGrandpa = 'true'
			else:
				spaceGrandpa = 'false'
		else:
			above_80 = 'false'
			spaceGrandpa = 'false'


		effString = f'	{{"{name.strip()}", {birthYear}, {deathYear}, {lunar}, {stroll}, {leo}, {trainAcc}, {above_80}, {spaceGrandpa}}},\n'

		nonApolloAstroBlob = nonApolloAstroBlob + effString

		keepingCount += 1

	nonApolloAstroBlob = nonApolloAstroBlob + '};\n'
	nonApolloAstroBlob = nonApolloAstroBlob + '\n' + f'#define nasaAstrosCount {keepingCount}'

	with open('./Human Efforts/scripts/Astronaut MC/nasaNonApolloAstroPre1970.h', 'w') as output:
		output.write(nonApolloAstroBlob)




