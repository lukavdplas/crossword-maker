# crossword-maker
Generate crossword puzzles from a vocabulary.

## Status
The crosswordFiller is a working program that takes an empty crossword and a vocabulary. An empty crossword has the positions of the "black squares" already specified, and a vocabulary is just a list of words. The crosswordFiller fills the crossword wih words. It performs an exhaustive, depth-first search through all possible crosswords, filling them in word-by-word, reducing computing time by prioritising positions with few options left.
Writing the program so that the black squares are determined a priori has some advantages. Most importantly, it reduces the size of the solution space for the search, which helps with complexity.

I worked a bit on the emptycrosswords module, which is supposed to run together with the crosswordFiller, generating empty crosswords to fill in. I ran into the problem that the division of white and black squares in empty crosswords is not as easy to describe as it seems.

As an alternative to procedurally generating empty crosswords, I started on a prototype version of a complete crossword generator (makecrossword), that uses a limited number of hard-coded empty crosswords as a basis. 

I have also started on a crosswordMaker, which is similar to the crosswordFiller but does not use an empty crossword as a basis. The adaptation mostly consists of simplifications to the code, which is nice. However, with even a limited vocabulary, it is almost impossible to run the crosswordMaker on my personal computer, so I'm abandoning the idea for now.
