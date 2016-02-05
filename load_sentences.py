import operator

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

def load_sentences(language_list, file_prefix, file_postfix):
  lang_sentences = [ ]

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

      lang_sentences.append(sentences)

  return lang_sentences
