# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import subprocess, re
import pandas as pd

# use linux command line tool pdftotext to convert a pdf to a visually laid out
# text file
def convertPDFToText(currentPDF):
    
    # read binary mode for PDF reading
    pdfData = open(currentPDF,'rb').read()

    # call pdftotext
    pdftotext_cmd = "/usr/local/bin/pdftotext"
    pdftotext_opt = "-layout"
    try:
        if (len(pdfData) > 0) :
            out, err = subprocess.Popen([pdftotext_cmd, pdftotext_opt, currentPDF, 
                                     currentPDF.replace('.pdf','.txt') ])\
                                     .communicate()
    except:
        print('Could not complete conversion.')
        return -1
    return 0
    
def extractPatterns(fname):
    with open(fname, encoding = 'ISO-8859-1', mode = "r") as text_file:
        text = text_file.read()
        
    # parse text for spaces:
    line_parser = pd.DataFrame({'line':text.split('\n')})
    line_parser['spaces'] = ''
    for index in line_parser.index:
        line = line_parser.loc[index,'line']
        while len(line)>0:
            len_init = len(line)
            line = line.lstrip(' ')
            len_final = len(line)
            len_change = len_init - len_final
            line_parser.loc[index,'spaces'] += str(len_change) + ','          
            skip_chars = line.find(' ')
            if skip_chars == -1:
                line_parser.loc[index,'spaces'] += str(len(line)) + ','
                line = ''
            else:
                line_parser.loc[index,'spaces'] += str(skip_chars) + ','
                line = line[skip_chars:]
    return line_parser

def detectLineType(lines):
    lines['line_type'] = ''
    for index in lines.index:
        if lines.loc[index,'spaces'] == '':
            lines.loc[index,'line_type'] = 'empty line'
        else:
           space_dist = list(map(int, list(filter(None,lines.loc[index,'spaces'].split(',') ))))
           space_evens = space_dist[2::2]
           if all(e == 1 for e in space_evens):
               lines.loc[index,'line_type'] = 'text line'
           else:
               lines.loc[index,'line_type'] = 'tabular line'
    return lines
 
def multipleSpaceSplit(lines):
    lines['space_split_len'] = ''
    for index in lines.index:
        n = len(re.split(r'\s{2,}', lines.loc[index,'line']))
        lines.loc[index,'space_split_len'] = n
    return lines

def generateDocDataFrame(fname):
    df = extractPatterns(fname)
    detectLineType(df)
    multipleSpaceSplit(df)
    return df

def findTables(df):
    table_index = []
    current_table_start = -1
    current_table_cols = 0
    for index in df.index:
        # find the beginning of a table
        if (df.loc[index,'line_type'] == 'tabular line') and\
            (current_table_start == -1):
                current_table_start = index
                current_table_cols = df.loc[index,'space_split_len']
        # find end of table
        if (df.loc[index,'space_split_len'] == 1) and\
            (df.loc[index,'line_type'] == 'text line') and\
            (current_table_start != -1):
                table_index.extend([current_table_start,index])
                current_table_start = -1
                current_table_cols = 0
        # find end of one table, start of another
        if (df.loc[index,'space_split_len'] != current_table_cols) and\
            (df.loc[index,'line_type'] == 'tabular line'):
                table_index.extend([current_table_start,index])
                current_table_start = index
                current_table_cols = df.loc[index,'space_split_len']
    return table_index

def extractTable(df, start, end):
    table = pd.DataFrame(columns=re.split(r'\s{2,}',df.loc[start,'line']))
    for index in range(start+1,end):
        if df.loc[index,'line_type'] == 'tabular line':
            table.loc[len(table)] = re.split(r'\s{2,}',df.loc[index,'line'])
    return table            
            
            
            
            
            
            