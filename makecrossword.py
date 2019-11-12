#puts some stuff together to make a dutch crossword


import numpy as np
import random
from importvocab import importVocab
import emptycrosswords
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

emptygrid = emptycrosswords.generateEmpty()

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

def sortedverticals(cw):
    """Returns a list of all vertical sequences, but sorted by row instead of by
    column."""
    words = []
    for y in range(cw.Height):
        for x in range(cw.Width):
            seq = cw.Seq(x,y,'ver')
            if seq:
                starting_x, starting_y = seq.cors[0]
                if starting_y == y:
                    words.append(seq)
    return words

hor_clues = cluelist(solved.hor)
sorted_ver = sortedverticals(solved)
ver_clues = cluelist(sorted_ver)

#%%

#-------------------------------------------------------------------------------
# export
#-------------------------------------------------------------------------------

from exporter import Exporter

Exporter.Export('test.xml', solved,  (hor_clues, ver_clues), author='Luka')
