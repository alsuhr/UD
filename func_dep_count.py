import sys

filename = sys.argv[1]
wordlist = sys.argv[2]

words = { }

with open(wordlist) as word_file:
  for line in word_file:
    words[line[0:len(line) - 1]] = { }

with open(filename) as sentences:
  for line in sentences:
    line = line[0:len(line) - 1]
    comps = line.split("\t")
    if len(comps) >= 10:
      word = comps[1]
      if word in words.keys():
        deptype = comps[7]
        if deptype in words[word].keys():
          words[word][deptype] += 1
        else:
          words[word][deptype] = 1

for word, counts in words.iteritems():
  print "***** word: %s *****" % word
  for deptype, count in counts.iteritems():
    print "%s,%d" % (deptype, count)

  print ""
