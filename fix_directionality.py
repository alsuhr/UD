import sys

corpus = sys.argv[1]
linenumbers = sys.argv[2]
newfile = sys.argv[3]

numbers = { }
with open(linenumbers) as number_file:
  for line in number_file:
    comps = line.split(",")
    numbers[int(comps[0])] = comps[1:len(comps)]

outfile = open(newfile, "w")

with open(corpus) as corpus_file:
  index = 0
  found_culprit = False
  incorrect_head = -1
  incorrect_head_head = -1
  head_deptype = ""
  correct_head = -1
  dependents = [ ]

  for line in corpus_file:
    if line == "\n":
      found_culprit = False
      incorrect_head = -1
      incorrect_head_head = -1
      head_deptype = ""
      correct_head = -1
      dependents = [ ]     
      outfile.write("\n")
    elif not found_culprit and index in numbers.keys():
      found_culprit = True 
      # Have found a line where the head is after and dependency is mwe.
      # For the leftmost participant:
      #   - Make it a dependent of its current head's head. Change the dependency type to whatever
      #     that dependency type was.
      #   - Leave its children the same.
      # For the rightmost participant:
      #   - Make it a dependent of the leftmost participant with type mwe.
      #   - Make its children dependent of the leftmost participant.
      # For dependents of rightmost participant:
      #   - Make their head the leftmost participant.
      incorrect_head = int(numbers[index][0])
      incorrect_head_head = int(numbers[index][1])
      head_deptype = numbers[index][2]
      correct_head = int(numbers[index][3])
      dependents_str = numbers[index][4:len(numbers[index])]
      for dep_str in dependents_str:
        intval = int(dep_str)
        if intval != correct_head:
          dependents.append(intval)

      comps = line.split("\t")

      # Check the id.
      word_id = int(comps[0])
      if word_id == incorrect_head:
        # Word you're looking at is the incorrect head. Change its head to be the correct_head and its type
        # to 'mwe'.
        comps[6] = str(correct_head)
        comps[7] = "mwe"
      elif word_id == correct_head:
        # Word you're looking at is the correct head. Change its head and deptype.
        comps[6] = str(incorrect_head_head)
        comps[7] = head_deptype 
      elif word_id in dependents:
        # Looking at a child of the incorrect head. Change its head to the correct head.
        comps[6] = str(correct_head)

      printval = "\t".join(comps) 
      outfile.write(printval)
    elif found_culprit:
      comps = line.split("\t")

      # Check the id.
      word_id = -1
      if comps[0].isdigit():
        word_id = int(comps[0])
      if word_id == incorrect_head:
        # Word you're looking at is the incorrect head. Change its head to be the correct_head and its type
        # to 'mwe'.
        comps[6] = str(correct_head)
        comps[7] = "mwe"
      elif word_id == correct_head:
        # Word you're looking at is the correct head. Change its head and deptype.
        comps[6] = str(incorrect_head_head)
        comps[7] = head_deptype 
      elif word_id in dependents:
        # Looking at a child of the incorrect head. Change its head to the correct head.
        print "%d Found dependent %d, changing head to %d" % (index, word_id, correct_head)
        comps[6] = str(correct_head)

      printval = "\t".join(comps) 
      outfile.write(printval)

    else:
      outfile.write(line)

    index = index + 1

outfile.close()
