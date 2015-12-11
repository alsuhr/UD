import sys

outfile = open("tempcorpus.conllu", "w")

with open(sys.argv[1]) as f:
  for line in f:
    comps = line.split("\t")
    if len(comps) == 10 and (comps[3] == "DET" or comps[3] == "INTJ") and comps[7] == "expl":
      comps[3] = "PART"
      outfile.write("\t".join(comps))
    else:
      outfile.write(line) 
