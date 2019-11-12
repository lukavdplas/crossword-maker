import os
import csv



def importVocab(path):
    filenames = os.listdir(path)

    vocab = dict()

    for filename in filenames:
        file = open(path + '/' + filename, newline='')
        table = csv.reader(file, delimiter='\t')
        for row in table:
            lemma = row[0]
            descriptions = row[1:]
            vocab[lemma] = descriptions

    return vocab
