import operator
import sys

class Word(object):
  def __init__(self):
    self.child_dep = [ ]
    self.p_dep = -1
    self.subdeptype = ""

  def SetInfo(self, id, word, deptype, pos):
    self.id = id
    self.word = word
    self.deptype = deptype
    self.pos = pos

  def AddParentDep(self, index):
    self.p_dep = index

  def AddChildDep(self, index):
    self.child_dep.append(index)

  def HasParent(self):
    return self.p_dep >= 0

  def SetSubDeptype(self, subdeptype):
    self.subdeptype = subdeptype

  def PrintVal(self):
    print"%d\t%s\t\t\t%s\t%s\t%d\t%s" % (self.id, self.word, self.deptype, self.pos, self.p_dep, ','.join(str(dep) for dep in self.child_dep))

class Sentence(object):
  def __init__(self, textvalue, line_number):
    self.line_number = line_number
    self.words = [ ]
    root = Word()
    root.SetInfo(0, "", "n/a", "n/a")
    self.words.append(root)

    self.val = ""
    self.deps = ""
    self.pos = ""

    words_waiting = { }

    # Iterate through each unit in the sentence (either a word or a 
    # parts of a word)
    index = 1
    for line in textvalue:
      # Split on tabs
      tab_sep = line.split("\t")

      word_val = tab_sep[1]

      # This strips the second part of the dependency type (if present)
      split_deptype = tab_sep[7].split(":")
      dep_type = split_deptype[0]
      pos = tab_sep[3]

      self.val = self.val + word_val + " "
      self.deps = self.deps + dep_type + " "
      self.pos = self.pos + pos + " "

      # Make it into a word
      if index in words_waiting:
        word = words_waiting[index]
      else:
        word = Word()

      word.SetInfo(index, word_val, dep_type, pos)

      if len(split_deptype) > 1:
        word.SetSubDeptype(split_deptype[1])

      self.words.append(word)
      
      # Get what it's dependent on; add it as a child.
      dep = int(tab_sep[6])
      if dep < len(self.words):
        # Parent is in list, so add it as a child.
        self.words[dep].AddChildDep(index)
        word.AddParentDep(dep)
      else:
        # Parent isn't in the list yet, so preemptively create it. 
        if dep in words_waiting:
          parent = words_waiting[dep]
        else:
          parent = Word()
        parent.AddChildDep(index)
        word.AddParentDep(dep)
        words_waiting[dep] = parent

      index = index + 1

  def ContainsDeptype(self, deptype):
    for v in self.words:
      if v.deptype == deptype:
        return True
    
    return False

  def ContainsWord(self, word):
    for w in self.words:
      if w.word == word:
        return True

    return False

  def PrintDetails(self):
    for word in self.words:
      word.PrintVal()

# This adds the part of speech tags for the heads and dependents for every occurrence
# of dep_type in a sentence. If the POS is already in the dictionary, it increments.
def GetPosTagsHeadDep(sentence, dep_type, heads, deps):
  for word in sentence.words:
    if word.deptype == dep_type:
      # Get the POS tag of the head (if it has one). 
      if word.HasParent():
        head_pos = sentence.words[word.p_dep].pos
        if head_pos != "NOUN" and head_pos != "PROPN" and head_pos != "NUM" and head_pos != "PRON":
          if not head_pos in heads:
            heads[head_pos] = [ ]

          heads[head_pos].append(sentence.line_number + word.id)

      # Iterate through the children. Get the POS and keep track of it.
      for child in word.child_dep:
        child_pos = sentence.words[child].pos
        if child_pos in deps:
          deps[child_pos] = deps[child_pos] + 1
        else:
          deps[child_pos] = 1  

# This adds dep tags for the heads and dependents for every occurrence
# of dep_type in a sentence. If the POS is already in the dictionary, it increments.
def GetDepTagsHeadDep(sentence, dep_type, heads, deps):
  for word in sentence.words:
    if word.deptype == dep_type and word.pos == 'VERB':
      # Get the DEP tag of the head (if it has one). 
      if word.HasParent():
        head_dep = sentence.words[word.p_dep].deptype
        if head_dep in heads:
          heads[head_dep] = heads[head_dep] + 1
        else:
          heads[head_dep] = 1

      # Iterate through the children. Get the POS and keep track of it.
      for child in word.child_dep:
        child_dep = sentence.words[child].deptype

        if (child_dep == 'nsubj'):
          print "--------- New Sentence with Feature --------"
          sentence.PrintDetails()
          print "%s\n\n" % sentence.val

        if child_dep in deps:
          deps[child_dep] = deps[child_dep] + 1
        else:
          deps[child_dep] = 1

# This adds the subtypes for each dep_type for every occurrence of dep_type in a sentence.
def GetSubDepTypes(sentence, dep_type, subtypes):
  for word in sentence.words:
    if word.deptype == dep_type:
      # Get the subtype if there is one.
      subtype = word.subdeptype
      if subtype != "":
        if subtype in subtypes:
          subtypes[subtype] = subtypes[subtype] + 1
        else:
          subtypes[subtype] = 1
      else:
        subtypes["none"] = subtypes["none"] + 1

# This adds the values of each word for every occurrence of dep_type in a sentence.
def GetDepWords(sentence, dep_type, words):
  for word in sentence.words:
    if word.deptype == dep_type:
      lower_word = word.word.lower()

      if (lower_word == "glie"):
        print "--------- New Sentence with Feature --------"
        sentence.PrintDetails()
        print "%s\n\n" % sentence.val

      if lower_word in words:
        words[lower_word] = words[lower_word] + 1
      else:
        words[lower_word] = 1

# This adds the pos for every occurrence of dep_type in a sentence.
def GetDepPos(sentence, dep_type, pos_list):
  for word in sentence.words:
    if word.deptype == dep_type:
      pos = word.pos

      if pos == "PART":
        print "---------- New Sentence with Feature ----------"
        sentence.PrintDetails()
        print "%s\n\n" % sentence.val

      if pos in pos_list:
        pos_list[pos] = pos_list[pos] + 1
      else:
        pos_list[pos] = 1

# This adds dep tags for the heads and dependents for every occurrence
# of dep_type in a sentence. If the POS is already in the dictionary, it increments.
def GetDepHeadWords(sentence, dep_type, head_words):
  for word in sentence.words:
    if word.deptype == dep_type:
      # Get the DEP tag of the head (if it has one). 
      if word.HasParent():
        lower_word = sentence.words[word.p_dep].word.lower()

        if (lower_word == "take"):
          print "--------- New Sentence with Feature --------"
          sentence.PrintDetails()
          print "%s\n\n" % sentence.val

        if lower_word in head_words:
          head_words[lower_word] = head_words[lower_word] + 1
        else:
          head_words[lower_word] = 1

# Should be used for dependencies where the head must be to the left (e.g. conj)
def CheckHeadInitialConsistency(sentence, dep_type, leftcount, rightcount, fix_info, save_info):
  for word in sentence.words:
    if word.deptype == dep_type:
      if word.p_dep < word.id:
        leftcount = leftcount + 1
      else:
        rightcount = rightcount + 1

        # Want to print:
        #   - line number of the sentence at the beginning
        #   - id of the incorrect head
        #   - id of what should be the correct head
        #   - id of the incorrect head's head and its dependency type
        #   - ids of dependents of the incorrect head
        info = str(sentence.line_number) + "," + str(word.p_dep) + "," + str(sentence.words[word.p_dep].p_dep) + "," + sentence.words[word.p_dep].deptype + "," + str(word.id) + ","
        info = info + ",".join(map(str, sentence.words[word.p_dep].child_dep))

        if len(sentence.words[word.p_dep].child_dep) == 1:
          if not info in fix_info:
            fix_info.append(info)
        else:
          if not info in save_info:
            save_info.append(info)

  return (leftcount, rightcount)

def PrintHeadDepPosTags(sentences, dep_type, language):
  head_pos = { }
  dep_pos = { }

  for sentence in sentences:
    if sentence.ContainsDeptype(dep_type):
      GetPosTagsHeadDep(sentence, dep_type, head_pos, dep_pos)

  sorted_head = { }
  sorted_dep = { }

  sorted_head = sorted(head_pos.items(), key=operator.itemgetter(0))
  # sorted_head.reverse()
  sorted_dep = sorted(dep_pos.items(), key=operator.itemgetter(0))
  # sorted_dep.reverse()

  writefile = open(language + "_ln.txt", "w")

  for pos, numbers in sorted_head:
    writefile.write("---- " + pos + ": " + str(len(numbers)) + "----\n")
    for number in numbers:
      writefile.write(str(number) + "\n")

  #print "---------- Dependent POS for %s ----------" % dep_type
  #for pos, count in sorted_dep:
  #  print "%s: %s" % (pos, str(count))

def CountRelPosTags(sentences, dep_type, language, pos_count):
  pos_list = { }

  for sentence in sentences:
    if sentence.ContainsDeptype(dep_type):
      GetDepPos(sentence, dep_type, pos_list)

  for pos, count in pos_list.iteritems():
    pos_count[pos][language] = count

def GetSubtypes(sentences):
  result = { }

  for sentence in sentences:
    for word in sentence.words:
      subtype = word.subdeptype
      if subtype != "":
        wholetype = word.deptype + ":" + subtype
        if not wholetype in result:
          result[wholetype] = 1
        else:
          result[wholetype] = result[wholetype] + 1   

  return result

def PrintSubDepTypes(sentences, dep_type):
  subtypes = { }
  subtypes["none"] = 0

  for sentence in sentences:
    if sentence.ContainsDeptype(dep_type):
      GetSubDepTypes(sentence, dep_type, subtypes)

  sorted_deps = { }
  sorted_deps = sorted(subtypes.items(), key=operator.itemgetter(0))

  print "---------- Subtypes for Dep %s -----------" % dep_type
  for subtype, count in sorted_deps:
    print "%s: %s" % (subtype, str(count))

def PrintDepWords(sentences, dep_type):
  words = { }

  for sentence in sentences:
    if sentence.ContainsDeptype(dep_type):
      GetDepHeadWords(sentence, dep_type, words)

  sorted_words = { }
  sorted_words = sorted(words.items(), key=operator.itemgetter(1))

  print "---------- Words for Dep %s -----------" % dep_type
  for word, count in sorted_words:
    print "%s: %s" % (word, str(count))

def PrintDepPos(sentences, dep_type):
  pos_list = { }

  for sentence in sentences:
    if sentence.ContainsDeptype(dep_type):
      GetDepPos(sentence, dep_type, pos_list)

  sorted_pos = { }
  sorted_pos = sorted(pos_list.items(), key=operator.itemgetter(0))

  print "---------- POS for Dep %s -----------" % dep_type
  for pos, count in sorted_pos:
    print "%s: %s" % (pos, str(count))

def CheckPattern(sentences, word):
  # Checks for a pattern where the word is a case dependent,
  # and has case dependent.
  linenumbers = [ ]

  for sentence in sentences:
    if sentence.ContainsWord(word):
      # Find the word
      for w in sentence.words:
        if w.word == word and w.deptype == "case":
          for dep in w.child_dep:
            if sentence.words[dep].deptype == "case":
              linenumber = sentence.line_number
              if not linenumber in linenumbers:
                linenumbers.append(linenumber)
                print str(sentence.line_number + w.id)

def CheckInfPattern(sentences):
  for sentence in sentences:
    if sentence.ContainsWord("de") or sentence.ContainsWord("pour") or sentence.ContainsWord("INCORRECTINF"):
      for w in sentence.words:
        if w.deptype == "case" and (w.word == "de" or w.word == "pour" or w.word == "INCORRECTINF"):
           # Check for VERB dependents
           for dep in w.child_dep:
             if dep > w.id and sentence.words[dep].pos == "VERB":
               print str(sentence.line_number + w.id) + " " + w.word + " dep"

          # Check for VERB head
          #if sentence.words[w.p_dep].pos == "VERB" and not w.deptype == "mark":
          #  print str(sentence.line_number + w.id + 3)

def CheckObjConsistency(sentences):
  heads = { }
  dobj_deps = { }
  iobj_deps = { }

  for sentence in sentences:
    if sentence.ContainsDeptype("dobj") or sentence.ContainsDeptype("iobj"):
      GetPosTagsHeadDep(sentence, "dobj", heads, dobj_deps)
      GetPosTagsHeadDep(sentence, "iobj", heads, iobj_deps)

  if "ADP" in dobj_deps:
    print "Dobj has %d ADP dependents" % dobj_deps["ADP"]

  if "ADP" in iobj_deps:
    print "Iobj has %d ADP dependents" % iobj_deps["ADP"]

  sorted_dobj = sorted(dobj_deps.items(), key=operator.itemgetter(0))
  sorted_iobj = sorted(iobj_deps.items(), key=operator.itemgetter(0))

  # print "---------- Dobj ----------"
  # for dep, count in sorted_dobj:
  #  print "%s: %s" % (dep, str(count))

  # print "---------- Iobj ----------"
  # for dep, count in sorted_iobj:
  #  print "%s: %s" % (dep, str(count))

lang_file = sys.argv[1]
lang_prefix = sys.argv[2]
pos_list = sys.argv[3]

pos_count = { }

with open(pos_list) as pos:
  for line in pos:
    pos_count[line[0:len(line) - 1]] = { }

languages = [ ]

left_counts = { }
right_counts = { }

with open(lang_file) as lang_list:
  for lang_line in lang_list:
    comps = lang_line.split(",")
    # Load the sentence inputs.
    sentences = [ ]

    for pos, counts in pos_count.iteritems():
      counts[comps[0]] = 0

    with open(lang_prefix + comps[0] + "/" + comps[1][0:len(comps[1]) - 1] + "-ud-train.conllu") as input_file:
      curr_sentence = []
      index = 0
      sentence_number = -1
      for line in input_file:
        # Discard lines with comments marked with #. Also disregard any with a hyphen
        # in the first part (this indicates a word which is later described as parts)
        if line[0] != "#" and not("-" in line.split("\t")[0]):
          # Check if you have a new sentence (blank line)
          if line == "\n":
            sentence = Sentence(curr_sentence, sentence_number)
            sentences.append(sentence)
            curr_sentence = []
          else:
            if len(curr_sentence) == 0:
              sentence_number = index

            curr_sentence.append(line)
        index = index + 1

    # CheckObjConsistency(sentences)
    print "---------------------------- LANGUAGE : %s ----------------------------" % comps[0]
    # PrintHeadDepPosTags(sentences, sys.argv[3], comps[0])
    #CountRelPosTags(sentences, sys.argv[4], comps[0], pos_count) 
    subtypes = GetSubtypes(sentences) 

    outfile = open(comps[0] + "_subtypes.txt", "w")
    for subtype, count in subtypes.iteritems():
      outfile.write(subtype + ": " + str(count) + "\n")

    #outfile.close()

    languages.append(comps[0])

    #num_left = 0
    #num_right = 0
    #print_info = [ ]
    #save_info = [ ]
    #for sentence in sentences:
    #  (num_left, num_right) = CheckHeadInitialConsistency(sentence, sys.argv[4], num_left, num_right, print_info, save_info)
    #writefile = open(comps[0] + "_ln.txt", "w")
    #for info in print_info:
    #  writefile.write(info + "\n")

    #savefile = open(comps[0] + "_ln_with_dep.txt", "w")
    #for info in save_info:
    #  savefile.write(info + "\n")
    

    #left_counts[comps[0]] = num_left
    #right_counts[comps[0]] = num_right

#outfile = open("counts.csv", "w")

#outfile.write("direction,")
#outfile.write(",".join(languages) + "\n")
#outfile.write("left,")

#for lang, count in left_counts.iteritems():
#  print lang
#  outfile.write(str(count) + ",")
#outfile.write("\n")
#outfile.write("right,")

#for lang, count in right_counts.iteritems():
#  outfile.write(str(count) + ",")
#outfile.write("\n")
#for pos, counts in pos_count.iteritems():
#  outfile.write(pos + ",")
#  for lang, count in counts.iteritems():
#    print lang
#    outfile.write(str(count) + ",")
#  outfile.write("\n")

# PrintDepWords(sentences, sys.argv[2])
# PrintSubDepTypes(sentences, sys.argv[2])
# PrintDepPos(sentences, sys.argv[2])

#num_left = 0
#num_right = 0
#line_numbers = [ ]
#for sentence in sentences:
#  (num_left, num_right) = CheckHeadInitialConsistency(sentence, sys.argv[2], num_left, num_right, line_numbers)

#print "Found %d instances of left heads and %d of right heads." % (num_left, num_right)

#outfile = open(sys.argv[3], "w")
#for number in line_numbers:
#  outfile.write(str(number) + "\n")
#outfile.close()

#CheckPattern(sentences, "par")
#CheckInfPattern(sentences)
