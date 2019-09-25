"""

This file is intended to develop the crosswordMaker. Don't import!

The crosswordMaker is a new version of the crosswordFiller: it doesn't require
an empty crossword to fill in. Instead, it only needs a vocabulary and sets the
black/white fields while working.
This increases the solution space for the search, which comes at the cost of
computation time and space, but makes it more likely that the algorithm will
find something.

The vocabulary is a list of words that can be used in the crossword. For the
final product, of course, the words in the crossword need to be connected to
clues. This can be done post hoc, or the CrosswordMaker could be adapted to
import a dictionary of words and clues, and export clues as part of the output.

As a bit of terminology that is used throughout.

A crossword is the actual puzzle, meaning the grid structure. The solution to a
crossword is the grid completely filled out.

A crossword consists of fields. A field has a single letter. This is usually a
single character in the strict sense, but Dutch crosswords count "IJ" as a
single letter, so I avoid the term character. Fields that have no corresponding
letter are called black fields.

Fields in crosswords have coordinates (X,Y). X coordinates are counted left to
right, starting at 0. Y coordinates are counted top to bottom, starting at 0.

A sequence is a group of fields on a horizontal or vertical line that correspond
to a single word in the solution. Each sequence has a corresponding clue.

A word is an ordered set of letters and an element of the vocabulary. A word can
be filled into a sequence.
"""

import random
import copy
import numpy as np
import nltk

#%%

size = 13

#-------------------------------------------------------------------------------
# vocabulary import
#-------------------------------------------------------------------------------

#use the NLTK words corpus as a filler vocabulary

nltkwords = nltk.corpus.words.words()
unfilteredvocab = [w.lower() for w in nltkwords]

vocab = []
t = 0
for w in unfilteredvocab:
    if not '-' in w:
        vocab.append(w)
        t += 1
        if t > 1000:
            break

#%%

#use the words from the example crossword as a filler vocabulary
# crossword will only have one solution, but this is good for quick testing.

"""
vocab = ['moeras', 'bleken',
         'sara', 'reep',
         'kt', 'miljoen', 'cd',
         'kat', 'atoom', 'tra',
         'arts', 'ons', 'klit',
         'tu', 'do',
         'bereidvaardig',
         'lt', 'sp',
         'test', 'vos', 'step',
         'oer', 'meute', 'kei',
         'nl', 'uurwerk', 'lp',
         'snit', 'neon',
         'cruise', 'onecht',
         'mokka', 'tonic',
         'tarwemeel',
         'es', 'tt', 'sr', 'su',
         'ram', 'stelt', 'uni',
         'aria', 'uit', 'muis',
         'salto', 'verte',
         'jonkvrouw',
         'broos', 'steno',
         'leem', 'das', 'eren',
         'een', 'korps', 'koe',
         'kp', 'tl', 'tk', 'nc',
         'crimineel',
         'nadat', 'pipet'
        ]
"""
#%%

#organise the vocab by length

vocabdict = dict()
for w in vocab:
    l = len(w)
    if l in vocabdict.keys():
        vocabdict[l].add(w)
    else:
        vocabdict[l] = {w}


#-------------------------------------------------------------------------------
# generate lists of possible rows/columns
#-------------------------------------------------------------------------------

def partition(length):
    minwordlength = 3
    mincount = int((l + 1) / (3 + 1))

    partitions = []


    for wordlength in range(minwordlength, length+ 1):
        restlength = length - (wordlength)

        if restlength >= minwordlength + 1:
            rest = partition(restlength - 1)
            for result in rest:
                partitions.append([wordlength] + result)
        else:
            if restlength == 0:
                partitions.append([wordlength])

    return partitions

def wordsetFromPartition(par, vocabdict):
    #recursive function to get the wordset of a row (or part of one)

    if len(par) == 1:
        return vocabdict[par[0]] #words of this length
    else:
        sequenceset = set()
        restset = wordsetFromPartition(par[1:], vocabdict)
        wordset = vocabdict[par[0]]
        for r in restset:
            for w in wordset:
                sequenceset.add(w + '_' + r)
        return sequenceset

vocabset = set()
partitions = partition(size)
for p in partitions:
    for w in wordsetFromPartition(p, vocabdict):
        vocabset.add(w)

#-------------------------------------------------------------------------------
# sequence class
#-------------------------------------------------------------------------------

class Sequence:
    def __init__(self, cors, direction, crossword):
        self.l = len(cors)
        self.cors = cors
        self.direction = direction
        if self.direction == 'hor':
            self.otherdirection = 'ver'
        else:
            self.otherdirection = 'hor'

        self.wordset = copy.copy(crossword.vocab)
        self.UpdateLetters()
        self.cw = crossword

    def __len__(self):
        return len(self.cors)

    def UpdateLetters(self):
        """Update letter lists based on wordset."""
        newlist = []
        for i in range(len(self)):
            newset = set(w[i] for w in self.wordset)
            newlist.append(newset)

        self.letteroptions = newlist

    def Letters(self, x, y):
        """Get the letter list of a field based on its coordinates."""
        for i in range(len(self.cors)):
            xcor, ycor = self.cors[i]
            if (xcor, ycor) == (x,y):
                return self.letteroptions[i]
        return None

    def ExcludeLetter(self, i, letter):
        """Exclude a letter from a position and update the wordset."""
        newset = set()
        for w in self.wordset:
            if w[i] != letter:
                newset.add(w)
        self.wordset = newset
        self.UpdateLetters()

    def Choose(self, word):
        """Turn wordset into a single word. Return list of sequences that may be affected."""
        self.wordset = {word}

        #get indices of changed fields
        fieldindices = []
        for i in range(len(self)):
            if len(self.letteroptions[i]) > 1:
                self.letteroptions[i] = set(word[i])
                fieldindices.append(i)

        #get sequences intersecting with changed fields
        neighbours = []
        for i in fieldindices:
            otherseq = self.cw.Intersect(self, i)
            if otherseq:
                neighbours.append(otherseq)

        return neighbours

    def ExcludeWord(self, word):
        """Remove word from wordset and update letter options."""
        self.wordset.remove(word)
        oldletteroptions = copy.deepcopy(self.letteroptions)
        self.UpdateLetters()
        #this can be more efficient. You only need to see if one letter per position is still an option.

        #get list of sequences that may be affected
        cors_to_update = list()
        for i in range(len(self)):
            if self.letteroptions[i] != oldletteroptions[i]:
                cors_to_update.append(self.cors[i])

        neighbours = list()
        for x,y in cors_to_update:
            neighbours.append(self.cw.Seq(x,y, self.otherdirection))

        return neighbours

    def Copy(self, crossword):
        """Return a deep copy"""
        newseq = Sequence(self.cors, self.direction, crossword)

        newseq.wordset = copy.deepcopy(set([w for w in self.wordset]))

        newseq.UpdateLetters()
        return newseq

#-------------------------------------------------------------------------------
# crossword class
#-------------------------------------------------------------------------------

class Crossword:
    def __init__(self, size, vocab=None):
        """Initialise from empty grid or from other crossword"""
        if type(size) == Crossword:
            self.InitFromCrossword(grid)

        else:
            self.Width = size
            self.Height = size

            #create the list of possible rows/columns
            self.vocab = vocab


            #array that maps a coordinate in the crossword to which sequences overlap with it
            self.ref = np.array([[(None,None) for x in range(self.Height)] for y in range(self.Width)], tuple)

            #add horizontal sequences
            self.hor = []
            for y in range(self.Height):
                #get coordinates
                cors = []
                for x in range(0, self.Width):
                    cors.append((x, y))
                #initiate sequence
                self.hor.append(Sequence(cors, 'hor', self))

            #add vertical sequences
            self.ver = []
            for x in range(self.Width):
                #get coordinates
                cors = []
                for y in range(0, self.Height):
                    cors.append((x, y))
                #initiate sequence
                self.hor.append(Sequence(cors, 'ver', self))

    def InitFromCrossword(self, cw):
        """make a deep copy from another crossword"""
        self.Width = cw.Width
        self.Height = cw.Height

        #array that maps a coordinate in the crossword to which sequences overlap with it
        self.ref = np.array([[(None,None) for x in range(self.Height)] for y in range(self.Width)], tuple)


        #add horizontal sequences
        self.hor = [seq.Copy(self) for seq in cw.hor]
        #add sequences to map
        for i in range(len(self.hor)):
            s = self.hor[i]
            for x, y in s.cors:
                self.ref[x,y][0] = i

        #add vertical sequences
        self.ver = [seq.Copy(self) for seq in cw.ver]
        #add sequences to map
        for i in range(len(self.ver)):
            s = self.ver[i]
            for x, y in s.cors:
                self.ref[x,y][1] = i

    def Seq(self, x, y, direction):
        """Get the sequence that intersects with given coordinates on given direction"""
        if direction == 'hor':
            if self.ref[x, y][0] != None:
                return self.hor[self.ref[x, y][0]]
            return None
        else:
            if self.ref[x, y][1] != None:
                return self.ver[self.ref[x, y][1]]
            return None

    def Intersect(self, seq, i):
        """Get the sequence that intersects with input sequence's ith field."""
        direction = seq.otherdirection
        x,y = seq.cors[i]
        return self.Seq(x, y, direction)

    def UpdateSeq(self, seq):
        """Update the wordset of a single sequence"""
        if seq:
            #loop through sequence's fields
            oldletters = [options for options in seq.letteroptions]

            for i in range(len(seq.cors)):
                xcor, ycor = seq.cors[i]
                #get intersecting sequence
                otherseq = self.Intersect(seq, i)

                if otherseq:
                    #print('Checking position', i)
                    to_delete = seq.Letters(xcor, ycor) - otherseq.Letters(xcor, ycor)
                    #print('Excluding', to_delete)
                    if len(to_delete) > 0:
                        for letter in to_delete:
                            seq.ExcludeLetter(i, letter)

            #check if any intersecting sequences would be affected by this
            affected = list()

            for i in range(len(seq)):
                if seq.letteroptions[i] != oldletters[i]:
                    otherseq = self.Intersect(seq, i)
                    if otherseq:
                        affected.append(otherseq)

            #return list of newly affected sequences
            return affected
        else:
            return None

    def NextSeq(self):
        """return coordinates of the next sequence to be filled in. Currently calculated as
        the sequence with the smallest remaining wordset."""
        allsequences = self.hor + self.ver
        candidates = set()
        for seq in allsequences:
            if len(seq.wordset) > 1:
                candidates.add(seq)

        sequence = min(candidates, key= lambda seq: len(seq.wordset))
        x, y = sequence.cors[0]
        direction = sequence.direction
        return (x, y, direction)

    def __str__(self):
        """Print function."""
        strgrid = np.array([[' ' for x in range(self.Height)] for y in range(self.Width)], str)
        for seq in self.hor+self.ver:
            for i in range(len(seq.cors)):
                x, y = seq.cors[i]
                if strgrid[x, y] == ' ':
                    strgrid[x,y] = list(seq.wordset)[0][i]

        strgrid = strgrid.T

        bigstring = ''
        for row in strgrid:
            for field in row:
                bigstring = bigstring + field + ' '
            bigstring = bigstring + '\n'

        return bigstring

#%%

#-------------------------------------------------------------------------------
# filling in the crossword
#-------------------------------------------------------------------------------

def update(queue, crossword):
    """update the crossword, given a queue"""
    if len(queue) > 0:
        #pop first sequence
        seq = queue[0]
        if seq:
            x, y = seq.cors[0]
            direction = seq.direction

            #update sequence's wordlist
            neighbours = crossword.UpdateSeq(seq)

            #check if this led to a contradiction
            wordsleft = len(seq.wordset)
            if wordsleft > 0:
                if neighbours:
                    newqueue = queue[1:] + neighbours
                else:
                    newqueue = queue[1:]
                return update(newqueue, crossword)
            else:
                return False
        else:
            return update(queue[1:], crossword)
    else:
        #if the queue is empty, then we're done
        return True

iterations = 0
progress = list()

def FillIn(sequencelist, crossword):
    """Recursive function that fills in words in sequences"""
    #update logs
    global iterations
    global progress
    iterations += 1
    #get the number of words yet to be excluded
    left = 0
    for seq in crossword.hor + crossword.ver:
        left += len(seq.wordset) - 1
    progress.append(left)

    updated = update(sequencelist, crossword)

    if updated:
        #check if the crossword is now completely filled in
        complete = True
        for seq in crossword.hor + crossword.ver:
            if len(seq.wordset) > 1:
                complete = False

        if complete:
            #if the crossword is now complete
            return crossword

        else:
            #if the crossword is not yet complete
            #select the next sequence to change
            new_x, new_y, new_dir = crossword.NextSeq()
            sequence = crossword.Seq(new_x, new_y, new_dir)

            wordsetsize = len(crossword.Seq(new_x, new_y, new_dir))

            #select the next word to try
            wordchoice = random.choice(list(sequence.wordset))

            #create copy of the crossword
            newcw = copy.deepcopy(Crossword(crossword))
            newseq = newcw.Seq(new_x, new_y, new_dir)
            neighbours = newseq.Choose(wordchoice)

            #remove the word for other sequences to prevent duplicates
            for s in newcw.hor+newcw.ver:
                if len(s) == len(newseq) and s != newseq:
                    if wordchoice in s.wordset:
                        s.ExcludeWord(wordchoice)
                        for i in range(len(s)):
                            neighbours.append(newcw.Intersect(s, i))

            #check the resulting crossword
            filled_in = FillIn(neighbours, newcw)

            if filled_in:
                #if you were able to complete the crossword
                return filled_in
            else:
                #if you weren't, exclude this choice
                neighbours = sequence.ExcludeWord(wordchoice)

                #solve the crossword with this choice excluded
                return FillIn(neighbours, crossword)

    else:
        #if the update revealed a contradiction
        return None


#%%

#-------------------------------------------------------------------------------
# test crossword
#-------------------------------------------------------------------------------


c =  Crossword(13, vocabset)

solved = FillIn(c.hor+c.ver, c)
if solved:
    print(solved)

#%%

#progress graph

#import matplotlib.pyplot as plt

#plt.plot(list(range(len(progress))), progress, '-')
#plt.xlabel('iterations')
#plt.ylabel('total wordset size')

#%%

#-------------------------------------------------------------------------------
# test crossword
#-------------------------------------------------------------------------------
"""
from exporter import Exporter

Exporter.Export('test.xml', solved)
"""
