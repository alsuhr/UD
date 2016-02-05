from load_sentences import *
import sys

filename = sys.argv[1]
prefix = sys.argv[2]
postfix = sys.argv[3]

load_sentences(filename, prefix, postfix)
