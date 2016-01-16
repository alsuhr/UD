import sys

outfile = open("tempcorpus.conllu", "w")

with open(sys.argv[1]) as f:
  for line in f:
    comps = line.split("\t")
    if len(comps) == 10 and comps[3] == "ADP" and comps[7] == "case" and comps[1] == "par":
      comps[7] = "mark"
      outfile.write("\t".join(comps))
    else:
      outfile.write(line) 
