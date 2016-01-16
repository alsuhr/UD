import sys

file_name = sys.argv[1]

index = 0

pos_not_dep = { }
dep_not_pos = { }

with open(file_name) as file:
  for line in file:
    comps = line.split("\t")
    if len(comps) >= 10:
      if comps[3] == "AUX" and (comps[7] != "aux" and comps[7] != "auxpass"):
        pos_not_dep[index] = line[0:len(line) - 1]
      elif comps[3] != "AUX" and (comps[7] == "aux" or comps[7] == "auxpass"):
        dep_not_pos[index] = line[0:len(line) - 1]

    index = index + 1

print "****** AUX not aux (%d) ******" % len(pos_not_dep)
for (linenum, line) in pos_not_dep.iteritems():
  print "%d: %s" % (linenum, line)

print "****** aux not AUX (%d) ******" % len(dep_not_pos)
for (linenum, line) in dep_not_pos.iteritems():
  print "%d: %s" % (linenum, line)

