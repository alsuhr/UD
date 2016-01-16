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

def GetMatches(sentence, dep_type, pos, search_rel):
  line_numbers = [ ]

  for word in sentence.words:
    nummod_parent = False
    if word.HasParent() and sentence.words[word.p_dep].deptype == "nummod":
      nummod_parent = True

    if word.deptype == dep_type: # and nummod_parent:
      if search_rel == "d":
        for child in word.child_dep:
          if sentence.words[child].deptype == pos:
            line_numbers.append(sentence.line_number + word.id)
      else:
        print "Warning: search_rel should be w, h, or d"

  return line_numbers

def GetDepPosSentences(sentences, dep_type, pos, search_rel):
  match_sentences = [ ]
  line_numbers = [ ]

  for sentence in sentences:
    if sentence.ContainsDeptype(dep_type):
      ex_ln = GetMatches(sentence, dep_type, pos, search_rel)
      if len(ex_ln) > 0:
        match_sentences.append(sentence)
        for ln in ex_ln:
          line_numbers.append(ln)

  return (match_sentences, line_numbers)
     

if len(sys.argv) < 8:
  print "Arguments must be in the form:"
  print "  python get_dep_pos.py"
  print "    language_list: a list of languages, one per line, in the form \'language,shorthand\' e.g. \'English,en\'"
  print "    file_prefix: the prefix on the .conllu files, e.g. \'UD_\'"
  print "    file_postfix: the postfix on the .conllu files, e.g. \'-ud-train.conllu\'"
  print "      (this script will look for files in the form file_prefixlanguage/shorthandpostfix)"
  print "    dep_type: the dependency relation type to search for"
  print "    pos: the part of speech to limit the output to"
  print "    search_rel: which kind of relation to search for..."
  print "      w: look at the POS of words which have dep_type"
  print "      h: look at the POS of heads of the word which have dep_type"
  print "      d: look at the POS of the dependents of the word which have dep_type"
  print "    output_options: whether or not to print examples, line numbers, or both..."
  print "      e: just example sentences; one file will be created for each language in the form language_dep_type_pos_ex.txt"
  print "      l: just line numbers; one file will be created for each language in the form language_dep_type_pos_ln.txt"
  print "      el/le: both example sentences and line numbers"

language_list = sys.argv[1]
file_prefix = sys.argv[2]
file_postfix = sys.argv[3]
dep_type = sys.argv[4]
pos = sys.argv[5]
search_rel = sys.argv[6]
output_options = sys.argv[7]

with open(language_list) as language_file:
  for language in language_file:
    comps = language.split(",")
    long_name = comps[0]
    short_name = comps[1][0:len(comps[1]) - 1]

    # Load the sentence inputs.
    sentences = [ ]

    with open(file_prefix + long_name + "/" + short_name + file_postfix) as sentence_file:
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

    (examples, line_numbers) = GetDepPosSentences(sentences, dep_type, pos, search_rel) 

    if len(examples) > 0:
      print "Found %d examples for language %s with deptype %s and POS %s" % (len(line_numbers), long_name, dep_type, pos)
      output_prefix = long_name + "_" + dep_type + "_" + pos

      # Print example sentences.
      if output_options.find("e") >= 0:
        example_file = open(output_prefix + "_ex.txt", "w")
        for example in examples:
          example_file.write(example.GetDetails())
          example_file.write(example.val + "\n\n")
      
      # Print line numbers.
      if output_options.find("l") >= 0:
        line_file = open(output_prefix + "_ln.txt", "w")
        for line_number in line_numbers:
          line_file.write(str(line_number) + "\n")     
    else:
      print "No such examples for language %s with deptype %s and POS %s!" % (long_name, dep_type, pos)
