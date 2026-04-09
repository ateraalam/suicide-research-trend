# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 20:18:50 2025

@author: cdbha
"""
import pandas as pd
import nltk
from nltk.corpus import wordnet as wn
import os

# Function to preprocess text and search for terms
def analyze_methodology(frame):
    # Define lists of terms associated with quantitative and qualitative research
    quantitative_terms = [
        "statistical analysis", "regression analysis", "correlation", "hypothesis testing",
        "survey", "questionnaire", "experiment", "control group", "randomized controlled trial",
        "data points", "sample size", "standard deviation", "variance", "p-value",
        "quantitative data", "numerical data", "metrics", "measurement", "likert scale",
        "descriptive statistics", "inferential statistics", "t-test", "anova", "chi-square test",
        "factor analysis", "multivariate analysis", "cross-sectional study", "longitudinal study",
        "big data", "data mining", "epidemiological study", "risk factors", "suicide rates",
        "self-harm rates", "psychometric scales", "predictive modeling", "effect size",
        "standardized instruments", "meta-analysis", "systematic review"
    ]

    qualitative_terms = [
        "interviews", "focus groups", "case study", "ethnography", "phenomenology",
        "grounded theory", "narrative analysis", "content analysis", "thematic analysis",
        "discourse analysis", "observation", "field notes", "participant observation",
        "open-ended questions", "qualitative data", "textual analysis", "interpretive research",
        "contextual analysis", "inductive reasoning", "coding", "triangulation",
        "thick description", "emic perspective", "etic perspective", "narrative analysis",
        "thematic analysis", "grounded theory", "phenomenology", "interpretive phenomenological analysis",
        "contextual factors", "stigma", "coping mechanisms", "help-seeking behavior"
    ]

    # Update list with synonyms:

    for item in quantitative_terms:
        try:
            syns = wn.synset(f'{item}.n.01').lemma_names()
            for i in syns:
                if i not in quantitative_terms:
                    quantitative_terms.append(i)
        except Exception:
            pass

    for item in qualitative_terms:
        try:
            syns = wn.synset(f'{item}.n.01').lemma_names()
            for i in syns:
                if i not in qualitative_terms:
                    qualitative_terms.append(i)
        except Exception:
            pass

    text = str(frame.abstract)  # Convert to lowercase for case-insensitive matching
    # Initialize counters for quantitative and qualitative terms
    quant_count = 0
    qual_count = 0

    # Check for quantitative terms
    for term in quantitative_terms:
        if term in text:
            quant_count += 1

    # Check for qualitative terms
    for term in qualitative_terms:
        if term in text:
            qual_count += 1

    # Determine the methodology based on term counts
    if quant_count > qual_count:
        return "Quantitative"
    elif qual_count > quant_count:
        return "Qualitative"
    else:
        return "Mixed Methods or Unclear"


def main(dir_path):
    df = pd.read_csv(dir_path + r'\v2.scrubbed_data.csv')

    meth = df.apply(analyze_methodology, axis=1)
    df['research_methodology'] = meth

    df.to_csv(dir_path + r'\bibwithmeth.csv')


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__)) + r'\safetylit_records'

    main(dir_path)
