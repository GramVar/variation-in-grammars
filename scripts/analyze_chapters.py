import os
import pprint
import pandas as pd
import numpy as np
import re
from collections import namedtuple

# CHANGE THIS FILE PATH TO YOUR FOLDER WITH THE GRAMMAR SPREADSHEETS
loc = (r"C:\Users\rever\OneDrive\Desktop\grammar_project\Spreadsheets")

col_labels = ['phenomenon id', 'description', 'category', 'page number', 'chapter',
    'comment', 'explanation for variation', 'keyword', 'cross-ref/chapter', 'page cross-ref']
    
ColumnLabels = namedtuple('ColumnLabels', (
    'phenomenon_id', 'description', 'category', 'page_number', 'chapter',
    'comment', 'explanation', 'keyword', 'cross_ref_chapter', 'page_cross_ref'))

categories = ['phonetic', 'syllabic', 'grammatical word form', 'lexical word form',
    'word set alternation', 'inflectional affixes', 'derivational affixes', 'gender',
    'syntactic', 'historical', 'orthographic']

chapters = ['introduction', 'phonology', 'word classes', 'morphology', 'np structure',
    'vp structure', 'clause structure', 'complex clauses', 'lexicon appendix',
    'text appendix', 'variation', 'n/a']

explanations = ['dialectal', 'contact/borrowing/loan', 'age', 'register', 'gender',
    'class/profession', 'unclear', 'no explanation', 'social or socio-economic', 'out-group',
    'natural', 'historic', 'speech rate', 'speaker variation', 'free variation', 'competence',
    'levels of lexicalization', 'contact']

def check_column_headers(df):
    # Check column headers for consistency
    cols = df.columns
    for count, col in enumerate(cols):
        if col.lower().rstrip() != col_labels[count]:
            col_label = col_labels[count]
            print(f".....Found inconsistent header for \'{col_label}\' column: {col}")

def setup_cat_dict():
    # Initialize the category dictionaries
    file_cat_dict = {cat: {'count': 0} for cat in categories}
    file_cat_dict['uncategorized'] = {'count': 0}
    file_cat_dict['general'] = {'count': 0}
    for category in file_cat_dict:
        file_cat_dict[category]['chapters'] = dict.fromkeys(chapters, 0)
        file_cat_dict[category]['explanations for variation'] = dict.fromkeys(explanations, 0)
    return file_cat_dict

def analyze_categories(values, chap_values, exp_values, cat_dict):
    file_cat_dict = setup_cat_dict()
    for index, category in enumerate(values):
        if category == 0:
            lower_cat = 'general'
        else:
            cats = re.split(',\s*', category)
            for cat in cats:
                row_num = index + 2
                chapter = chap_values[index]
                explanation = exp_values[index]
                lower_chap = chapter.lower()
                if not isinstance(explanation, str) and np.isnan(explanation):
                    explanation = lower_exp = 'no explanation'
                else:
                    lower_exp = explanation.lower()
                if cat == 0:
                    lower_cat = 'general'
                else:
                    lower_cat = cat.lower().rstrip()
                    if lower_cat not in categories:
                        lower_cat = 'uncategorized'
                if lower_chap not in chapters:
                    lower_chap = 'n/a'

                cat_dict['totals'][lower_cat]['count'] += 1
                cat_dict['totals'][lower_cat]['chapters'][lower_chap] += 1

                exps = re.split(',\s*', lower_exp)
                if lower_exp != 'no explanation':
                    exps = re.split(',\s*', lower_exp)
                    for exp in exps:
                        exp = exp.strip()
                        cat_dict['totals'][lower_cat]['explanations for variation'][exp] += 1
                        file_cat_dict[lower_cat]['explanations for variation'][exp] += 1

                       file_cat_dict[lower_cat]['count'] += 1
                file_cat_dict[lower_cat]['chapters'][lower_chap] += 1

    return dict(sorted(file_cat_dict.items(), key=lambda item: item[1]['count'], reverse=True))

def get_keywords(values, keyword_dict):
    file_keyword_dict = {}
    totals_dict = keyword_dict['totals']
    for index, keywords in enumerate(values):
        if keywords is not np.nan:
            words = re.split(',\s*', keywords)
            for word in words:
                word = word.lower()
                if word in file_keyword_dict:
                    file_keyword_dict[word] += 1
                else:
                    file_keyword_dict[word] = 1
                if word in totals_dict:
                    totals_dict[word] += 1
                else:
                    totals_dict[word] = 1
    return dict(sorted(file_keyword_dict.items(), key=lambda item: item[1], reverse=True))
            

if __name__ == "__main__":
    # Setting up dictionary to print
    cat_dict = {
        'totals': setup_cat_dict(),
        'spreadsheets': {}
    }

    keyword_dict = {
        'totals': {},
        'spreadsheets': {}
    }

    for filename in os.listdir(loc):
        # DataFrame object
        df = pd.read_excel(os.path.join(loc, filename))
        df.columns = [x.lower().rstrip() for x in df.columns]

        print(f"\n..Checking for Category names in {filename}")
        cat_values = df.get('category')
        desc_values = df.get('description')
        chap_values = df.get('chapter')
        exp_values = df.get('explanation for variation')
        if cat_values.any() and desc_values.any():
            cat_dict['spreadsheets'][filename] = analyze_categories(cat_values, chap_values, exp_values, cat_dict)
        else:
            print("CATEGORY COLUMN DOES NOT EXIST")

        print(f"\n..Checking for keywords in {filename}")
        keyword_values = df.get('keyword')
        if keyword_values.any():
            keyword_dict['spreadsheets'][filename] = get_keywords(keyword_values, keyword_dict)
        else:
            print("KEYWORD COLUMN DOES NOT EXIST")

        print("\n---\n")
        
        
    keyword_dict['totals'] = dict(sorted(keyword_dict['totals'].items(), key=lambda item: item[1], reverse=True))
    cat_dict['totals'] = dict(sorted(cat_dict['totals'].items(), key=lambda item: item[1]['count'], reverse=True))
    final_dict = {
        'categories': cat_dict,
        'keywords': keyword_dict
    }
    print(final_dict)