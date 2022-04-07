import json
import sys
from collections import defaultdict as ddict
from typing import Any, DefaultDict, Dict, Set, Tuple

import matplotlib.pyplot as plt  # type: ignore

DATA1 = Tuple[Tuple[str, ...], Tuple[int, ...]]
DATA2 = Tuple[Tuple[str, ...], Tuple[float, ...], Tuple[float, ...]]

FIG_TITLE1 = "Fig 1: Types of Variation (All Grammars)"
FIG_TITLE2 = "Fig 2: Phonetic/Phonological vs. Syntactic : Explanations"

PHON_CATS = {
    "phonetic",
}
SYN_CATS = {
    "syntactic",
}


def caps(txt: str, all_caps: bool) -> str:
    return txt.upper() if all_caps else txt


def counts_by_expl(
    data: Dict[str, Any],
    cat_set: Set[str],
) -> Tuple[Tuple[str, ...], Tuple[float, ...]]:
    expl_cnts: DefaultDict[str, int] = ddict(int)
    for cat, cnts in data.items():
        if cat in cat_set:
            for expl, cnt in cnts["explanations for variation"].items():
                expl_cnts[expl] += cnt
    lbls, cnts = zip(*sorted(expl_cnts.items()))
    cnts = [100 * (cnt / sum(cnts)) for cnt in cnts]
    return lbls, cnts


def data1(data: Dict[str, Any]) -> DATA1:
    # Assumes counts are already sorted
    cat_cnts = [
        (cat, cnts["count"]) for cat, cnts in data.items() if cat != "uncategorized"
    ]
    lbls, cnts = zip(*cat_cnts)
    return lbls, cnts


def data2(data: Dict[str, Any]) -> DATA2:
    lbls, phon_cnts = counts_by_expl(data, PHON_CATS)
    _syn_lbls, syn_cnts = counts_by_expl(data, SYN_CATS)
    assert lbls == _syn_lbls
    return lbls, phon_cnts, syn_cnts


def plot1(data: DATA1, outfile: str, all_caps=True) -> None:
    lbls, cnts = data

    # Initialize graph
    fig, ax = plt.subplots()

    # Graph title
    ax.set_title(caps(FIG_TITLE1, all_caps))

    # Turn off border and y axis
    ax.set_frame_on(False)
    ax.yaxis.set_visible(False)

    # Bar chart
    bar = ax.bar(lbls, cnts, width=0.5, color="blue")

    # Display count on each bar
    ax.bar_label(bar, padding=5, rotation=90)

    # Set x axis labels
    ax.set_xticklabels([caps(lbl, all_caps) for lbl in lbls])

    # Angle labels
    fig.autofmt_xdate(rotation=45)

    # Save to file
    fig.savefig(outfile, bbox_inches="tight")


def plot2(data: DATA2, outfile: str, all_caps=True) -> None:
    lbls, phon_cnts, syn_cnts = data

    bar_width = 0.6
    gap = 0.4
    phon_lbls = [x * (1 + gap) for x in range(len(lbls))]
    syn_lbls = [(x * (1 + gap)) + bar_width for x in range(len(lbls))]

    fig, ax = plt.subplots()
    ax.set_title(caps(FIG_TITLE2, all_caps))
    ax.set_frame_on(False)
    ax.yaxis.set_visible(False)

    phon_bar = ax.bar(
        phon_lbls,
        phon_cnts,
        width=bar_width,
        color="blue",
        label="Phonology Category",
    )
    syn_bar = ax.bar(
        syn_lbls,
        syn_cnts,
        width=bar_width,
        color="orange",
        label="Syntactic Category",
    )
    ax.bar_label(phon_bar, fmt="%.2f", padding=5, rotation=90)
    ax.bar_label(syn_bar, fmt="%.2f", padding=5, rotation=90)
    ax.set_xticks([(x * (1 + gap)) + bar_width / 2 for x in range(len(lbls))])
    ax.set_xticklabels([caps(lbl, all_caps) for lbl in lbls])
    fig.autofmt_xdate(rotation=45)

    ax.legend()

    fig.savefig(outfile, bbox_inches="tight")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(f"Usage: {sys.argv[0]} DATA.JSON")
    with open(sys.argv[1], encoding="utf8") as f:
        data = json.load(f)

    # Formatting defaults
    plt.rcdefaults()
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["xtick.labelcolor"] = "#555555"
    plt.rcParams["text.color"] = "#555555"
    plt.rcParams["axes.titlecolor"] = "#000000"

    # Compute data
    data = data["categories"]["totals"]
    d1 = data1(data)
    d2 = data2(data)

    # Plot data
    plot1(d1, "fig1.png")
    plot2(d2, "fig2.png")

    # Write CSV
    with open("fig1.csv", "w", encoding="utf8") as f:
        f.write(
            "Variation,Count\n"
            + "\n".join(f"{lbl},{cnt}" for lbl, cnt in zip(*d1))
            + "\n"
        )
    with open("fig2.csv", "w", encoding="utf8") as f:
        f.write(
            "Explanation,Phonology (%),Syntax (%)\n"
            + "\n".join(f"{lbl},{pcnt},{scnt}" for lbl, pcnt, scnt in zip(*d2))
            + "\n"
        )
