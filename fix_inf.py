import sys

corpus = sys.argv[1]
linenumbers = sys.argv[2]
newfile = sys.argv[3]

numbers = [ ]
with open(linenumbers) as number_file:
	for line in number_file:
		numbers.append(int(line))

outfile = open(newfile, "w")

with open(corpus) as corpus_file:
	index = 1
	looking_for_
	for line in corpus_file:
		if index in numbers:
			comps = line.split("\t")
			if comps[1] == "de" or comps[1] == "pour" or comps[1] == "INCORRECTINF":
				comps[7] = "mark"
				outval = ""
				for i in range(0, len(comps) - 1):
					outval = outval + comps[i] + "\t"
				outval = outval + comps[len(comps) - 1]
				outfile.write(outval)
			else:
				outfile.write(line)
		else:
			outfile.write(line)


		index = index + 1

outfile.close()