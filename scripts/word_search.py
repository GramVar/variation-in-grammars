import argparse
import json
import re
import string
from collections import namedtuple
from pathlib import Path

# TODOs:
# Find context across page boundaries
# Find co-occurences
# Assign scores

CONTEXT_WIDTH = 25

SearchResult = namedtuple("SearchResult", ("page_idx", "word", "word_idx", "context"))
MergedResult = namedtuple("MergedResult", ("page_idx", "words", "word_idxs", "context"))


def parse_keywords(kwfile):
    with open(kwfile, encoding="utf-8") as f:
        return [line.strip() for line in f]


def search_to_merged(result):
    return MergedResult(
        result.page_idx,
        [result.word],
        [result.word_idx],
        result.context,
    )


def split_words(page):
    words = [word.strip(string.punctuation) for word in page.split()]
    return words


def search_for_words(pages, keywords):
    results = []
    for ind, page in enumerate(pages):
        words = split_words(page)
        for word_ind, word in enumerate(words):
            if any(
                re.fullmatch(keyword, word, flags=re.IGNORECASE) for keyword in keywords
            ):
                lookback = max(word_ind - CONTEXT_WIDTH, 0)
                lookahead = word_ind + CONTEXT_WIDTH
                context = words[lookback:lookahead]
                results.append(SearchResult(ind, word, word_ind, list(context)))
    return merge_contexts(results)


def merge_contexts(search_results):
    if search_results == []:
        return []

    merged_results = [search_to_merged(search_results[0])]
    for result in search_results[1:]:
        last_merged = merged_results[-1]
        dist = result.word_idx - last_merged.word_idxs[-1]
        same_page = last_merged.page_idx == result.page_idx
        assert last_merged.page_idx < result.page_idx or (same_page and dist > 0)
        overlap = (2 * CONTEXT_WIDTH + 1) - dist
        if same_page and dist <= 2 * CONTEXT_WIDTH:
            # The search results are within CONTEXT_WIDTH of each other, so we merge
            # Append the keyword that co-occurs
            last_merged.words.append(result.word)
            last_merged.word_idxs.append(result.word_idx)
            last_merged.context.extend(result.context[overlap:])
        else:
            merged_results.append(search_to_merged(result))
    return merged_results


def format_result(result):
    return f'{", ".join(result.words)} (Page {result.page_idx + 1})\n{" ".join(result.context)}'


def format_results(results):
    return "\n\n".join(map(format_result, results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for keywords.")
    parser.add_argument(
        "file",
        type=str,
        help="a JSON file to search",
    )
    parser.add_argument(
        "keywords",
        type=str,
        help="keywords to search for (one regex per line)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="the file to write search results (defaults to <input file>.txt)",
    )
    args = parser.parse_args()

    with open(args.file, "rb") as f:
        pages = json.load(f)
    keywords = parse_keywords(args.keywords)

    results = search_for_words(pages, keywords)

    out = (
        args.output if args.output is not None else Path(args.file).with_suffix(".txt")
    )
    with open(out, "w", encoding="utf-8") as f:
        f.write(format_results(results))
    print(f"{len(results)} search results written to {out}")
