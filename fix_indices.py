import sys

corpus = sys.argv[1]
newfile = sys.argv[2]
prefix = sys.argv[3]

outfile = open(newfile, "w")

with open(corpus) as corpus_file:
	index = 1
	for line in corpus_file:
		comps = line.split(" ")
		if comps[0] == "#" and comps[1] == "sentid:":
			writestr = "# sentid: " + prefix + "_" + '{0:05}'.format(index) + "\n"
			outfile.write(writestr)
			index = index + 1
		else:
			outfile.write(line)

outfile.close()