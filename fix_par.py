import sys

corpus = sys.argv[1]
linenumbers = sys.argv[2]
newfile = sys.argv[3]

numbers = [ ]
with open(linenumbers) as number_file:
  for line in number_file:
    numbers.append(int(line))

outfile = open(newfile, "w")

with open(corpus) as corpus_file:
  index = 0
  found_culprit = False
  after_par = False
  par_comps = [ ]
  after_par_comps = [ ]
  par_num = -1
  for line in corpus_file:
    if index in numbers:
      # Has found the beginning of a new culprit sentence;
      # should not be a useful line so just print it.
      outfile.write(line)
      found_culprit = True
    else:
      if line == "\n":
        # Found empty line so you're at the end of a
        # sentence, so print it and set found_culprit
        # to false. Also set after_par to false.
        found_culprit = False
        outfile.write(line)
      elif not found_culprit:
        # Hasn't found a new sentence, and not currently
        # looking at a bad sentence, so just print the line
        # and move on
        outfile.write(line)
      else:
        # Split on tabs.
        tabs = line.split("\t")

        if not after_par:
          if tabs[1] == "par":
            # Found 'par'. So set par bool to true.
            after_par = True
            par_comps = tabs
            after_par_comps.append(par_comps)
            par_num = tabs[0]
          else:
            # Just print the line.
            outfile.write(line)
        else:
          # Reading a line after the wrong par.
          if tabs[6] == par_num:
            # Found the dependent. Set the head num from
            # 'par'.
            tabs[6] = after_par_comps[0][6]
            tabs[7] = "nmod"
            after_par_comps[0][6] = tabs[0]
            after_par_comps.append(tabs)

            # Now print the comps.
            for comps in after_par_comps:
              printval = ""
              for i in range(0, len(comps) - 1):
                printval = printval + comps[i] + "\t"
              printval = printval + comps[len(comps) - 1]

              outfile.write(printval)

            after_par = False
            par_comps = [ ]
            after_par_comps = [ ]
            par_num = -1
            found_culprit = False
          else:
            # Didn't find the dependent. Just append the
            # comps to the after_par_comps.
            after_par_comps.append(tabs)

    index = index + 1

outfile.close()
