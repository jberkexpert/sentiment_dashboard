# Demonstrates the sentiment analysis capability of the expert.ai (Cloud based) Natural Language API performed by the 'sentiment' resource
import os
import matplotlib.pyplot as plt
import pandas as pd
import math
from collections import Counter
import csv
import time
from statistics import mean

positive_sentiment_list = []
negative_sentiment_list = []
phrase_list = []
lemma_list = []
syncon_list = []
topic_list = []

#Overall Analysis
def sentiment_phrase_lemma_syncon_topic(output):
    topic_replace = {
        "trade": "shopping",
        "the economy": "pricing",
        "geography": "location",
        "job market": "staff",
        "Christianity": "Christmas",
        "sports": "team",
        "tourism": "travel",
        "roads and traffic": "transportation",
        "data storage": "storage",
        "anatomy": "people",
        "folklore": "holidays",
        "construction industry": "home construction",
        "computer science":"internet",
        "watercraft and nautical navigation": "navigation"
    }
    positive_sentiment_list.append(output.sentiment.positivity)
    negative_sentiment_list.append(output.sentiment.negativity)

    phrase_str = ""
    for phrase in output.main_phrases:
        phrase_str = phrase_str + phrase.value + "\n"
    phrase_list.append(phrase_str)

    lemma_str = ""
    for lemma in output.main_lemmas:
        lemma_str = lemma_str + lemma.value + "\n"
    lemma_list.append(lemma_str)

    syncon_str = ""
    for sy in output.main_syncons:
        syncon_str = syncon_str + str(sy.lemma) + "\n"
    syncon_list.append(syncon_str)

    topic_str = ""
    for topic in output.topics:
        if topic.label in topic_replace:
            topic_str = topic_str + topic_replace[topic.label] + "\n"
        else:
            topic_str = topic_str + topic.label + "\n"
    topic_list.append(topic_str)

    return positive_sentiment_list, negative_sentiment_list, phrase_list, lemma_list, syncon_list, topic_list

#Sentiment Summary
def sentiment_summary(sentiment_list):
    average = round(mean(sentiment_list), 2)
    total = sum(sentiment_list)
    pos_count = len(list(filter(lambda x: (x > 0), sentiment_list)))
    neg_count = len(list(filter(lambda x: (x < 0), sentiment_list)))
    zero_count = len(sentiment_list) - pos_count - neg_count
    analysis_type = ["Total Sentiment", "", "Positive Count", "Negative Count", "Zero Count (Neutral)"]
    numbers = [total, "", pos_count, neg_count, zero_count]
    df = pd.DataFrame({"Average Sentiment": analysis_type, average: numbers})
    return df

#Individual Analysis
def analysis(analysis_list, analysis_type):
    split_list = []
    for item in analysis_list:
        item = item.splitlines()
        for word in item:
            split_list.append(word)
    count = Counter(split_list)
    print(count)

    col = []
    count_col = []
    for item in count:
        col.append(item)
        count_col.append(count[item])
    df = pd.DataFrame({analysis_type: col,'Count': count_col})
    return df.sort_values(by=['Count'], ascending=False)

#Individual Analysis
def analysis2(analysis_list, analysis_type, sentiment_list):
    split_list = []
    positive_list = []
    negative_list = []
    neutral_list = []
    for i in range(0, len(analysis_list)):
        item = analysis_list[i]
        item = item.splitlines()
        for word in item:
            split_list.append(word)
            if sentiment_list[i] > 0:
                positive_list.append(word)
            elif sentiment_list[i] < 0:
                negative_list.append(word)
            elif sentiment_list[i] == 0:
                neutral_list.append(word)
    count = Counter(split_list)
    count_pos = Counter(positive_list)
    count_neg = Counter(negative_list)
    count_neut = Counter(neutral_list)

    col, count_col, col_pos, col_neg, col_neut = [], [], [], [], []

    for item in count:
        col.append(item)
        count_col.append(count[item])
        if count_pos[item]:
            col_pos.append(count_pos[item])
        else:
            col_pos.append(0)
        if count_neg[item]:
            col_neg.append(count_neg[item])
        else:
            col_neg.append(0)
        if count_neut[item]:
            col_neut.append(count_neut[item])
        else:
            col_neut.append(0)
    df = pd.DataFrame({analysis_type: col,'Count': count_col, 'Positive Count': col_pos, "Negative Count": col_neg, "Neutral Count": col_neut})
    return df.sort_values(by=['Count'], ascending=False)

#Emotional and Behavioral Traits
def traits(combined_text, client, language, trait, amount):
    total = 0
    combined_lists = []
    combined_len = math.ceil(len(combined_text) / math.ceil(len(combined_text) / amount))

    for chunk in chunks(combined_text, combined_len):
        combined_lists.append(chunk)
    categories = []
    frequency = []
    score = []
    for item in combined_lists:
        taxonomy = trait
        document = client.classification(body={"document": {"text": item}}, params={'taxonomy': taxonomy,'language': language})

        if len(document.categories) > 0:
            total+=1
        for category in document.categories:
            categories.append(category.label)
            frequency.append(float(category.frequency))
            score.append(category.score)

    category_list = list(set(categories))
    frequency_list = [0] * len(category_list)
    score_list = [0] * len(category_list)
    for i in range(0,len(categories)):
        index = category_list.index(categories[i])
        frequency_list[index]+=(frequency[i] / float(total))
        frequency_list[index] = round(frequency_list[index],2)
        score_list[index]+=(score[i] / total)
        score_list[index] = round(score_list[index])

    df = pd.DataFrame({'Categories': category_list,'Frequency': frequency_list, 'Score': score_list})
    return df.sort_values(by=['Frequency'], ascending=False)

def chunks(s, n):
    """Produce `n`-character chunks from `s`."""
    i = 0
    total = 0
    for start in range(0, len(s), n):
        if start + total + n >= len(s):
            break
        start+=total
        i = 0
        while start + n < len(s) and s[start + n] != " ":
            n+=1
            i+=1
        yield s[start:start+n]
        n-=i
        total+=i
