import operator
import sys

class Word(object):
	def __init__(self):
		self.child_dep = [ ]
		self.p_dep = -1

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

	def PrintVal(self):
		print"%d\t%s\t\t\t%s\t%s\t%d\t%s" % (self.id, self.word, self.deptype, self.pos, self.p_dep, ','.join(str(dep) for dep in self.child_dep))

class Sentence(object):
	def __init__(self, textvalue):
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
			dep_type = tab_sep[7]
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
				if head_pos in heads:
					heads[head_pos] = heads[head_pos] + 1
				else:
					heads[head_pos] = 1

				if head_pos == "NUM":
					print "--------- New Sentence with Feature --------"
					sentence.PrintDetails()
					print "%s\n\n" % sentence.val
					#print word.word

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
		if word.deptype == dep_type:
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
				if child_dep in deps:
					deps[child_dep] = deps[child_dep] + 1
				else:
					deps[child_dep] = 1

def PrintHeadDepPosTags(sentences, dep_type):
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

	print "---------- Head POS for %s ----------" % dep_type
	for pos, count in sorted_head:
		print "%s: %s" % (pos, str(count))

	print "---------- Dependent POS for %s ----------" % dep_type
	for pos, count in sorted_dep:
		print "%s: %s" % (pos, str(count))

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
	#	print "%s: %s" % (dep, str(count))

	# print "---------- Iobj ----------"
	# for dep, count in sorted_iobj:
	#	print "%s: %s" % (dep, str(count))

filename = sys.argv[1]

# Load the sentence inputs.
sentences = [ ]

with open(filename) as input_file:
	curr_sentence = []
	for line in input_file:
		# Discard lines with comments marked with #. Also disregard any with a hyphen
		# in the first part (this indicates a word which is later described as parts)
		if line[0] != "#" and not("-" in line.split("\t")[0]):
			# Check if you have a new sentence (blank line)
			if line == "\n":
				sentence = Sentence(curr_sentence)
				sentences.append(sentence)
				curr_sentence = []
			else:
				curr_sentence.append(line)

# CheckObjConsistency(sentences)

PrintHeadDepPosTags(sentences, sys.argv[2])