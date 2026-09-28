import csv
import os

ssaBlob = """
struct ssaData_1930 {
	int age;
	int numAlive;
};

static struct ssaData_1930 cohortData_1930[] = {
"""

# doing the same tacking on the end thing as the apollo data c-lib generator

with open('./Human Efforts/Manually Compiled Data/Third Party/US Social Security/Actuarial Study 120/CohLifeTables_M_Alt2_TR2024.csv', newline='') as ssa1930_CSV:
		ssaCsvData = csv.reader(ssa1930_CSV, delimiter=',')

		for row in ssaCsvData:
			if not row or row[0] != '1930': # weird row / not row thing
			# why –> row[0] v string. for the first few lines is a string, then numbers.
			# can't do int(row[30]) or it'll crash when a string or null is coerced
			# could try to filter those out but apparently harder?????
			# 
				continue
			else:
				age = int(row[1])
				numAlive = int(row[3])

			effString = f'{{ {age}, {numAlive} }},\n'
			ssaBlob += effString

ssaBlob += '};'

with open ('./Human Efforts/scripts/1930CohortSSAData.h', 'w') as output:
	output.write(ssaBlob)