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

  def GetVal(self):
    return "%d\t%s\t\t\t%s\t%s\t%d\t%s" % (self.id, self.word, self.deptype, self.pos, self.p_dep, ','.join(str(dep) for dep in self.child_dep))

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

  def GetDetails(self):
    value = ""
    for word in self.words:
      value = value + word.GetVal() + "\n"

    return value

def GetMatches(sentence, dep_type, skip_words):
  words = { }

  for word in sentence.words:
    word_val = word.word.lower()
    if word.deptype == dep_type and word_val not in skip_words:
      if word_val in words:
        words[word_val] += 1
      else:
        words[word_val] = 1

  return words

def GetWords(sentences, dep_type, skip_words, word_list):
  for sentence in sentences:
    if sentence.ContainsDeptype(dep_type):
      words = GetMatches(sentence, dep_type, skip_words)
      for word, count in words.iteritems():
        if word in word_list.keys():
          word_list[word] += count
        else:
          word_list[word] = count

def GetDepPosSentences(sentences, dep_type):
  wordlist = [ ]

  for sentence in sentences:
    if sentence.ContainsDeptype(dep_type):
      words = GetMatches(sentence, dep_type)
      for word in words:
        wordlist.append(word)

  return wordlist 
     

if len(sys.argv) < 5:
  print "Arguments must be in the form:"
  print "  python get_dep_pos.py"
  print "    file -- the file to look in for word examples"
  print "    wordlist_prefix -- prefix for skipwords files"
  print "    dependency_list -- a list of closed-class dependencies"
  print "    output_prefix -- prefix to output the words and counts to"

file = sys.argv[1]
wordlist_prefix = sys.argv[2]
dependency_list = sys.argv[3]
output_prefix = sys.argv[4]

dependencies = { }
skip_words = { }

with open(dependency_list) as dependency_file:
  for line in dependency_file:
    dependency_name = line[0:len(line) - 1]
    dependencies[dependency_name] = { }
    skip_words[dependency_name] = [ ]

    with open(wordlist_prefix + dependency_name) as dependency_skiplist:
      for wordline in dependency_skiplist:
        word = wordline[0:len(wordline) - 1]
        skip_words[dependency_name].append(word)

# Load the sentence inputs.
sentences = [ ]

with open(file) as sentence_file:
	curr_sentence = []
	index = 0
	sentence_number = -1
	for line in sentence_file:
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

for dependency in dependencies.keys():
	GetWords(sentences, dependency, skip_words[dependency], dependencies[dependency])    
	output_file = open(output_prefix + dependency, "w")

	for (word, count) in dependencies[dependency].iteritems():
		output_file.write(word + "," + str(count) + "\n")
