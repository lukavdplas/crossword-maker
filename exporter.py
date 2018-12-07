import xml.etree.ElementTree as ET
import numpy as np

class Exporter:
    def Export(path, crossword, clues=None, author='Luka van der Plas'):
        if path.endswith('.xml') or path.endswith('.pzl'):
            Exporter.ExportAsXML(path, crossword, clues, author)

    def ExportAsXML(path, cw, clues, author):
        root = ET.Element('puzzle')
        #add author
        author_n = ET.SubElement(root, 'author')
        author_n.text = author

        #add size
        width = cw.Width
        height = cw.Height
        size_n = ET.SubElement(root, 'size')
        size_n.text = str(width)+'x'+str(height)

        #set up grid
        grid = np.full([width, height], '_', dtype=str)
        for seq in cw.hor+cw.ver:
            for i in range(len(seq.cors)):
                x, y = seq.cors[i]
                grid[x,y] = list(seq.wordset)[0][i]
        grid = grid.T

        #add grid node
        grid_n = ET.SubElement(root, 'grid')
        for row in grid:
            row_n = ET.SubElement(grid_n, 'row')
            row_n.text = ''.join(row)

        #add clues

        #export
        tree = ET.ElementTree(element=root)
        tree.write(path, encoding='utf-8')
