import os
import re
import pandas as pd
import numpy as np

# CHANGE THIS FILE PATH TO YOUR FOLDER WITH THE GRAMMAR SPREADSHEETS
loc = (r"../Spreadsheets")

col_labels = ['phenomenon id', 'description', 'category', 'page number', 'chapter',
    'comment', 'explanation for variation', 'keyword', 'cross-ref/chapter', 'page cross-ref']
    
categories = ['phonetic', 'syllabic', 'grammatical word form', 'lexical word form',
    'word set alternation', 'inflectional affixes', 'derivational affixes', 'gender',
    'syntactic', 'historical', 'orthographic', 'functional interpretation']

chapters = ['introduction', 'phonology', 'word classes', 'morphology', 'np structure',
    'vp structure', 'clause structure', 'complex clauses', 'lexicon appendix',
    'text appendix', 'variation', 'discourse/pragmatics', 'semantics']

explanations = ['dialectal', 'contact/borrowing/loan', 'age', 'register', 'gender',
    'class/profession', 'unclear', 'no explanation', 'social or socio-economic', 'out-group',
    'natural', 'historic', 'speech rate', 'speaker variation', 'free variation',
    'competence', 'articulatory']

def check_column_headers(df):
    # Check column headers for consistency
    cols = df.columns
    for count, col in enumerate(cols):
        if col.lower().rstrip() != col_labels[count]:
            col_label = col_labels[count]
            print(f".....Found inconsistent header for \'{col_label}\' column: {col}")
    
def check_values(values, categories, col_name):
    try:
        for index, value in enumerate(values):
            row_num = index + 2
            if isinstance(value, str):
                vals = re.split(',\s*', value)
                for val in vals:
                    lower_val = val.lower().rstrip()
                    if lower_val not in categories:
                        print(f"....Unrecognized {col_name} \'{val}\' found at row {row_num}")
            elif value != 0:
                print(f"....Unrecognized {col_name} \'{value}\' found at row {row_num}")
    except TypeError:
        print(f"Found no values for {col_name}")


if __name__ == "__main__":
    
    for filename in os.listdir(loc):
        # DataFrame object
        df = pd.read_excel(os.path.join(loc, filename))
        df.columns = [x.lower().strip() for x in df.columns]
        print(f"Generating report for: {filename}\n")
        print(f"..Checking for inconsistent column headers in {filename}")
        check_column_headers(df)

        print(f"\n..Checking for Category names in {filename}")
        cat_values = df.get('category')
        check_values(cat_values, categories, 'Category')
        print(f"\n..Checking for Chapter names in {filename}")
        chap_values = df.get('chapter')
        check_values(chap_values, chapters, 'Chapter')
        print(f"\n..Checking for Explanations for Variation in {filename}")
        exp_values = df.get('explanation for variation')
        check_values(exp_values, explanations, 'Explanation for Variation')
    
        print("\n---\n")
