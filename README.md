# crossword-maker
Generate crossword puzzles from a vocabulary.

## Status
The crossworkmaker works! The makecrossword module imports the vocabulary, generates an empty grid, fills it in, extracts clues and exports the result to an XML file. The core modules are the emptycrosswords module, which generates empty crosswords, and the crosswordFiller, which fills an empty crossword with words from the vocabulary. 

The emptycrosswords module specifies a number of constraints on boolean grids (words have a minimum length of 3, the grid should have good ratio of black and white squares, etc.). It then performs a search through all boolean grids, using simulated annealing. The output is boolean grid that specifies which squares can have letters in them.

The crosswordFiller takes an empty crossword and a vocabulary, and fills in the crossword. It performs an exhaustive, depth-first search through all possible crosswords, filling them in word-by-word, reducing computing time by prioritising positions with few options left.

Writing the program so that the black/white squares are determined a priori has some advantages. Most importantly, it reduces the size of the solution space for the search, which helps with complexity.

There are a few minor errors to work out:
* Output from the emptycrosswords should almost always result in a valid empty crossword for the crosswordFiller. However, empty crosswords often lead to the crosswordFiller aborting the search almost immediately, suggesting there may be some problem with compatiblity. For the moment, it does not take too long to start over a few times.
* The crosswordFiller should not use the same word twice in the same crossword, but this constraint does not seem to work. 

As an alternative to the crosswordFiller and hard-coded templates, I have also started on a crosswordMaker, which is similar to the crosswordFiller but does not use an empty crossword as a basis. The adaptation mostly consists of simplifications to the code, which is nice. However, with even a limited vocabulary, it is almost impossible to run the crosswordMaker on my personal computer, since the combinations of words for an entire row increase exponentially, so I'm abandoning the idea for now.
