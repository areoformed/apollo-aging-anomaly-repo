import csv
import os

#
#  Have had to update this to maintain uniformity across the astronaut
#  pool
# 

astroBlob = """#include <stdbool.h>
#include "nasaAstroStructDefv2.h"

static struct nasaAstronaut apolloAstros[] ={ 

"""

# what I did here is that I've started the array that will be sent to the code
# this is the array of values. I then tack on / append to the END of the array.

astroCount = 0

with open('./Human Efforts/Manually Compiled Data/Apollo Astronaut Data/Lunar Astronauts-Apollo Astronauts.tsv', newline='') as apolloCSV:
	astroData = csv.reader(apolloCSV, delimiter='\t')
	next(astroData)           # trick that Claude taught me. 
	# Logic, csv.reader returns an "iterator"
	#
	# data cheat sheet, with 0 index, 
	# 0 = name, 
	# 5 = lunar eva bool, 6 = did go to the moon bool, <--- LLO v LEO
	# 9 = did they die before 1970?, 10 = did they die in an accident? 
	#
	for row in astroData:		
		name = row[0].replace('"','\\"')
		# the replace " with \\" means that it won't throw errors as a header in C if someone's nickname is there like "Buzz"
		# note: implemented this rule with Claude's help.		

		birthYear = int(row[2].split()[-1])  # hard coded to parse "August 5, 1930" | 
		# -1 loops back around

		deathYearStr = row[7].strip()        # 7 is date of death -- strip removes fields that are empty with a space
		if deathYearStr == '':
			deathYear = 0          # i.e. still alive
		else:
			deathYear = int(row[7].split()[-1]) # same loop back hard coding as line 34

		if row[6] == 'N':          # Did they go to the moon? = No
			lunar = 'false'
			stroll = 'false'
		else:                      	# Yes they went to the moon
			lunar = 'true'         	# LLO flag
			if row[5] == 'N':      	# No surface EVA
				stroll = 'false'
			else:
				stroll = 'true'

								# Cursed if statements aside, 
		leo = 'true'			# they're an Apollo 7 to 17 astronaut 
								# --- they went to space by default

		if row[9] == 'Y':               # Pre-1970 death
			if row[10] == 'Y':          # Accidental?
				trainAcc = 'true'       # sweeping everything including Apollo 1 here
			else:
				trainAcc = 'false'
		else:
			trainAcc = 'false'
		

		if deathYear == 0:
			above_80 = 'true'
		else:
			if ((deathYear - birthYear) >= 80):
				above_80 = 'true'
			else:
				above_80 = 'false'

		if row[11] == 'Y':
			spaceGrandpa = 'true'
		else:
			spaceGrandpa = 'false'


		effString = f'	{{"{name.strip()}", {birthYear}, {deathYear}, {lunar}, {stroll}, {leo}, {trainAcc}, {above_80}, {spaceGrandpa}}},\n'
		
		astroCount += 1
		print(astroCount, ' ', effString)

		astroBlob = astroBlob + effString

# doing it with the five non-lunar Apollo astronauts.

with open('./Human Efforts/Manually Compiled Data/Apollo Astronaut Data/Non-Lunar Astronauts-LEO-Only Apollo.tsv', newline='') as nonLunarApolloCSV:
		otherAstroData = csv.reader(nonLunarApolloCSV, delimiter='\t')
		next(otherAstroData)
		
		for row in otherAstroData:
			# just duplicating the other code...should this be a function?

			name = row[0].replace('"','\\"')			

			birthYear = int(row[2].split()[-1])  	# hard coded to parse "August 5, 1930" | 
			# -1 loops back around

			deathYearStr = row[7].strip()        	# 7 is date of death -- strip removes fields that are empty with a space
			if deathYearStr == '':
				deathYear = 0         			 	# i.e. still alive. Hard coded to be false in C.
			else:
				deathYear = int(row[7].split()[-1]) # same loop back hard coding as line 34

			if row[6] == 'N':          		# Did they go to the moon? = No
				lunar = 'false'
				stroll = 'false'
			else:                      		# Yes they went to the moon
				lunar = 'true'         		# LLO flag
				if row[5] == 'N':      		# No surface EVA
					stroll = 'false'
				else:
					stroll = 'true'

			leo = 'true'					# same schtick as above

			if row[9] == 'Y':               # Pre-1970 death
				if row[10] == 'Y':          # Accidental?
					trainAcc = 'true'       # sweeping everything including Apollo 1 here
				else:
					trainAcc = 'false'
			else:
				trainAcc = 'false'

			if deathYear == 0:
				above_80 = 'true'
			else:
				if ((deathYear - birthYear) >= 80):
					above_80 = 'true'
				else:
					above_80 = 'false'

			if row[11] == 'Y':
				spaceGrandpa = 'true'
			else:
				spaceGrandpa = 'false'


			effString = f'	{{"{name.strip()}", {birthYear}, {deathYear}, {lunar}, {stroll}, {leo}, {trainAcc}, {above_80}, {spaceGrandpa}}},\n'

			astroCount += 1
			print(astroCount, ' ', effString)

			astroBlob = astroBlob + effString		


astroBlob = astroBlob + '};\n'
astroBlob = astroBlob + '\n' + f'#define apolloAstrosCount {astroCount}'

with open('./Human Efforts/scripts/Astronaut MC/apolloData.h', 'w') as output:
	output.write(astroBlob)