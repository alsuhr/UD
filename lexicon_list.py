import sys

file_list = sys.argv[1]

single_pos = { }
multiple_pos = { }

word_counts = { }

with open(file_list) as files:
  for line in files:
    line = line[0:len(line) - 1]
    with open(line) as input_file:
      for input_line in input_file:
        input_line = input_line[0:len(input_line) - 1]
        comps = input_line.split("\t")
        if len(comps) >= 10:
          word = comps[1].lower()

          if not word in word_counts:
            word_counts[word] = 1
          else:
            word_counts[word] += 1

          pos = comps[3]
          if not word in single_pos.keys():
            single_pos[word] = pos
          elif word in multiple_pos.keys():
            if not pos in multiple_pos[word]:
              multiple_pos[word].append(pos)
          elif word in single_pos.keys():
            if single_pos[word] != pos:
              multiple_pos[word] = [ single_pos[word], pos ]

for word, pos_list in multiple_pos.iteritems():
  val = word + "," + str(word_counts[word]) + ","
  for pos in pos_list:
    val += pos + ","

  print val
