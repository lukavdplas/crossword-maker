"""

This file contains the crosswordFiller for use.

The CrosswordFiller needs two things as input: an empty crossword (which
specifies the locations of black fields) and a vocabulary.

The vocabulary is a list of words that can be used in the crossword. For the
final product, of course, the words in the crossword need to be connected to
clues. This can be done post hoc, or the CrosswordFiller could be adapted to
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

        self.wordset = crossword.vocabdict[self.l]
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
        """Turn wordset into a single word. Return list of coordinates for which the letterset has changed."""
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
    def __init__(self, grid, vocabdict=None):
        """Initialise from empty grid or from other crossword"""
        if type(grid) == Crossword:
            self.InitFromCrossword(grid)

        else:
            self.vocabdict = vocabdict
            self.Empty = grid
            shape = grid.shape
            self.Width = shape[0]
            self.Height = shape[1]

            #array that maps a coordinate in the crossword to which sequences overlap with it
            self.ref = np.array([[(None,None) for x in range(self.Height)] for y in range(self.Width)], tuple)

            #add horizontal sequences
            self.hor = []
            for y in range(self.Height):
                left = False
                for x in range(self.Width - 1):
                    current = self.Empty[x,y]
                    right = self.Empty[x+1, y]
                    if (left, current, right) == (False, True, True):
                        #if this is the start of a new sequence
                        #check length of sequence
                        l = 0
                        for value in self.Empty[x:, y]:
                            if value:
                                l += 1
                            else:
                                break

                        cors = []
                        for xcor in range(x, x+l):
                            cors.append((xcor, y))
                            self.ref[xcor, y][0] = len(self.hor)

                        self.hor.append(Sequence(cors, 'hor', self))

                    left = current

            #add vertical sequences
            self.ver = []
            for x in range(self.Width):
                above = False
                for y in range(self.Height - 1):
                    current = self.Empty[x,y]
                    below = self.Empty[x, y+1]
                    if (above, current, below) == (False, True, True):
                        #if this is the start of a new sequence
                        #check length of sequence
                        l = 0
                        for value in self.Empty[x, y:]:
                            if value:
                                l += 1
                            else:
                                break

                        cors = []
                        for ycor in range(y, y+l):
                            cors.append((x, ycor))
                            self.ref[x, ycor][1] = len(self.ver)

                        self.ver.append(Sequence(cors, 'ver', self))

                    above = current

    def InitFromCrossword(self, cw):
        """make a deep copy from another crossword"""
        self.Empty = copy.deepcopy(cw.Empty)
        self.Width = cw.Width
        self.Height = cw.Height
        self.vocabdict = cw.vocabdict

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


def FillIn(sequencelist, crossword):
    """Recursive function that fills in words in sequences"""

    #try to update
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
