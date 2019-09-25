#puts some stuff together to make a dutch crossword


import numpy as np
from importvocab import importVocab
import crosswordFiller as cf


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

#-------------------------------------------------------------------------------
# empty crosword import
#-------------------------------------------------------------------------------

# as a filler, we will use our example crossword and take the setting from it.

grid = ['moeras_bleken',
        'o_sara_reep_a',
        'kt_miljoen_cd',
        'kat_atoom_tra',
        'arts_ons_klit',
        '_w_tu_k_do_m_',
        'bereidvaardig',
        '_m_lt_r_sp_n_',
        'test_vos_step',
        'oer_meute_kei',
        'nl_uurwerk_lp',
        'i_snit_neon_e',
        'cruise_onecht']

emptygrid = np.full((len(grid), len(grid[0])), True, dtype=bool)

for i in range(len(grid)):
    for j in range(len(grid[i])):
        if grid[i][j] == '_':
            emptygrid[j,i] = False

#-------------------------------------------------------------------------------
# filling in the crossword
#-------------------------------------------------------------------------------

c =  cf.Crossword(emptygrid, vocabdict)
solved = cf.FillIn(c.hor+c.ver, c)
if solved:
    print(solved)
else:
    print('oh no ):')
