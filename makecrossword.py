#puts some stuff together to make a dutch crossword

print('importing modules...')

import random

from importvocab import importVocab
import emptycrosswords
import crosswordFiller as cf
from exporter import Exporter

#%%

#-------------------------------------------------------------------------------
# vocab import
#-------------------------------------------------------------------------------

print('importing vocab...')

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
# generate crossword
#-------------------------------------------------------------------------------

def generate():
    print('generating empty grid...')
    emptygrid = emptycrosswords.generateEmpty()

    print('filling in crossword...')
    c =  cf.Crossword(emptygrid, vocabdict)
    solved = cf.FillIn(c.hor+c.ver, c)

    return solved

solved = generate()

while not solved:
    solved = generate()

#%%

#-------------------------------------------------------------------------------
# match it with clues
#-------------------------------------------------------------------------------

print('finding clues...')

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

print('exporting...')

Exporter.Export('test.xml', solved,  (hor_clues, ver_clues), author='Luka')
