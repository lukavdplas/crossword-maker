#puts some stuff together to make a dutch crossword


import numpy as np
import random
from importvocab import importVocab
import crosswordFiller as cf

#%%

#-------------------------------------------------------------------------------
# vocab import
#-------------------------------------------------------------------------------

#import vocab
vocabpath = './vocab'
vocabwithclues = importVocab(vocabpath)
vocablist = list(vocabwithclues.keys())    #we don't care about the clues for now

#organise the vocab by length
#vocab dict contains a set of words for every length w
vocabdict = dict()
for w in vocablist:
    l = len(w)
    if l in vocabdict.keys():
        vocabdict[l].add(w)
    else:
        vocabdict[l] = {w}

#%%

#-------------------------------------------------------------------------------
# empty crosword import
#-------------------------------------------------------------------------------

# for now, i use a small set of hardcoded templates.

cws = [ [ [True, True, True, True, True, True, True, False, True, True, True, True, True],
          [False, False, False, True, False, False, False, False, True, True, True, False, True],
          [True, False, True, True, True, False, True, False, True, True, True, True, True],
          [True, False, False, True, True, True, True, False, True, False, True, False, True],
          [True, True, True, False, True, False, True, True, True, True, False, False, True],
          [True, False, True, False, False, False, True, False, False, True, True, True, True],
          [True, False, True, True, True, True, True, True, True, True, True, False, True],
          [True, True, True, True, False, False, True, False, False, False, True, False, True],
          [True, False, False, True, True, True, True, False, True, False, True, True, True],
          [True, False, True, False, False, False, True, True, True, True, False, False, True],
          [True, True, True, True, True, False, True, False, True, True, True, False, True],
          [True, False, True, True, True, False, False, False, False, True, False, False, True],
          [True, True, True, True, True, False, True, True, True, True, True, True, True] ] ]

emptygrid = np.array(random.choice(cws))

#%%

#-------------------------------------------------------------------------------
# filling in the crossword
#-------------------------------------------------------------------------------

c =  cf.Crossword(emptygrid, vocabdict)
solved = cf.FillIn(c.hor+c.ver, c)
if solved:
    print(solved)
else:
    print('oh no ):')

#%%

#-------------------------------------------------------------------------------
# match it with clues
#-------------------------------------------------------------------------------

def cluelist(sequencelist):
    """Returns a list of clues, in the order matching the original list."""
    words = [list(seq.wordset)[0] for seq in sequencelist]
    return [random.choice(vocabwithclues[word]) for word in words]

hor_clues = cluelist(solved.hor)
ver_clues = cluelist(solved.ver)

#%%

#-------------------------------------------------------------------------------
# export
#-------------------------------------------------------------------------------

from exporter import Exporter

Exporter.Export('test.xml', solved)
