import os
import pandas as pd
import numpy as np

# CHANGE THIS FILE PATH TO YOUR FOLDER WITH THE GRAMMAR SPREADSHEETS
loc = (r"C:\..\Grammars")

col_labels = ['phenomenon id', 'description', 'category', 'page number', 'chapter',
    'comment', 'keyword', 'cross-ref/chapter', 'page cross-ref']
    
categories = ['phonetic', 'syllabic', 'grammatical word form', 'lexical word form',
    'word set alternation', 'inflectional affixes', 'derivational affixes', 'gender',
    'syntactic', 'historical', 'orthographic']

def check_column_headers(df):
    # Check column headers for consistency
    cols = df.columns
    for count, col in enumerate(cols):
        if col.lower().rstrip() != col_labels[count]:
            col_label = col_labels[count]
            print(f".....Found inconsistent header for \'{col_label}\' column: {col}")
    
def check_categories(values, cat_dict, desc_values):
    for index, cat in enumerate(values):
        row_num = index + 2
        try:
            lower_cat = cat.lower().rstrip()
        except AttributeError:
            # Case where the category value is not a string
            # and not 0 (the General variation marker)
            if cat != 0:
                # Make sure the rest of the row isn't just empty
                if desc_values[index] is not np.nan:
                    print(f"....Unrecognized category \'{cat}\' found at row {row_num}")
                    cat_dict['uncategorized'] += 1
            else:
                cat_dict["general"] += 1
        else:
            if lower_cat in categories:
                cat_dict[lower_cat] += 1
            else:
                print(f"....Unrecognized category \'{cat}\' found at row {row_num}")
                cat_dict['uncategorized'] += 1

if __name__ == "__main__":
    cat_dict = dict.fromkeys(categories, 0)
    cat_dict["general"] = 0
    cat_dict["uncategorized"] = 0
    
    for filename in os.listdir(loc):
        # DataFrame object
        df = pd.read_excel(os.path.join(loc, filename))
        print(f"Generating report for: {filename}\n")
        print(f"..Checking for inconsistent column headers in {filename}")
        check_column_headers(df)

        print(f"\n..Checking for Category names in {filename}")
        cat_values = df.get('Category')
        desc_values = df.get('Description')
        if cat_values.any() and desc_values.any():
            check_categories(cat_values, cat_dict, desc_values)
        else:
            print("CATEGORY COLUMN DOES NOT EXIST")
    
        print("\n---\n")
    
    print(cat_dict)