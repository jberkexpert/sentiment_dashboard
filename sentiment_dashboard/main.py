# Demonstrates the sentiment analysis capability of the expert.ai (Cloud based) Natural Language API performed by the 'sentiment' resource
import os
import creds_file
import matplotlib.pyplot as plt
from expertai.nlapi.cloud.client import ExpertAiClient
import pandas as pd
import math
from collections import Counter
import csv
import time
import logging
import sys
from statistics import mean
from textblob import TextBlob
import traceback
from pathlib import Path
from nltk.sentiment import SentimentIntensityAnalyzer
from functions import sentiment_phrase_lemma_syncon_topic, analysis, analysis2, traits, chunks, sentiment_summary
os.environ["EAI_USERNAME"] = creds_file.un
os.environ["EAI_PASSWORD"] = creds_file.pw


class SentimentAnalyzer:
    def analyze_csv(self, input_file, output_file):
        path = Path(output_file)
        if path.is_file():
            return True
        try:
            print(input_file)
            client = ExpertAiClient()

            language= 'en'
            sia = SentimentIntensityAnalyzer()

            # output_file = "{}_Output.xlsx".format(input_file.strip(".csv"))
            combined_text = ""
            df_dict, df_dict2 = {}, {}
            df0, df1_0, df2, df3, df4, df5, df6 = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            positive_sentiment_list, negative_sentiment_list, phrase_list, lemma_list, syncon_list, topic_list = [], [], [], [], [], []
            sentiment_list, nltk_list, pos_nltk_list, neu_nltk_list, neg_nltk_list, textblob_list, combined_sentiment_list = [], [], [], [], [], [], []
            i = 0
            try:
                with open(input_file, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        print(row)
                        try:
                            for item in row:
                                if item not in df_dict:
                                    df_dict[item] = [row[item]]
                                else:
                                    df_dict[item].append(row[item])
                            name = list(row.items())[0][0]
                            text = row[name]
                            if len(text) > 10000:
                                text = text[0:9998]
                            combined_text = "{}\n{}".format(combined_text,text)
                            output = client.full_analysis(body={"document": {"text": text}}, params={'language': language})

                            combined = []

                            #Expert Sentiment
                            overall_expert = output.sentiment.overall
                            sentiment_list.append(overall_expert)
                            combined.append(overall_expert)
                            df1 = sentiment_summary(sentiment_list)

                            #NLTK
                            overall_nltk = sia.polarity_scores(text)['compound'] * 100
                            nltk_list.append(overall_nltk)
                            combined.append(overall_nltk)
                            pos_nltk_list.append(sia.polarity_scores(text)['pos'] * 100)
                            neu_nltk_list.append(sia.polarity_scores(text)['neu'] * 100)
                            neg_nltk_list.append(sia.polarity_scores(text)['neg'] * 100)

                            #TextBlob
                            textblob = TextBlob(text)
                            overall_textblob = textblob.sentiment.polarity * 100
                            textblob_list.append(overall_textblob)
                            combined.append(overall_textblob)

                            #Overall Sentiment
                            combined_sentiment_list.append(mean(combined))
                            df1_1 = sentiment_summary(combined_sentiment_list)

                            positive_sentiment_list, negative_sentiment_list, phrase_list, lemma_list, syncon_list, topic_list = sentiment_phrase_lemma_syncon_topic(output)
                            print("Printing positive sentiment:", positive_sentiment_list)
                            print(i)
                            i+=1
                        except Exception as e:
                            # logging.basicConfig(filename="log.txt", level=logging.DEBUG)
                            # logging.info(e)
                            print("Error 1:", e)
                            # sys.exit(1)
            except Exception as e:
                # logging.basicConfig(filename="log.txt", level=logging.DEBUG)
                # logging.info(e)
                print("Error 2:", e)
                # sys.exit(1)


            df_dict["Overall Sentiment"] = combined_sentiment_list
            df_dict["Expert Sentiment"] = sentiment_list
            df_dict["Positive Sentiment"] = positive_sentiment_list
            df_dict["Negative Sentiment"] = negative_sentiment_list
            df_dict["Phrases"] = phrase_list
            df_dict["Lemmas"] = lemma_list
            df_dict["Syncons"] = syncon_list
            df_dict["Topics"] = topic_list

            df_dict2["Expert Sentiment"] = sentiment_list
            df_dict2["NLTK Sentiment"] = nltk_list
            df_dict2["TextBlob Sentiment"] = textblob_list
            df_dict2["Combined Sentiment"] = combined_sentiment_list
            df_dict2["Expert Positive Sentiment"] = positive_sentiment_list
            df_dict2["Expert Negative Sentiment"] = negative_sentiment_list
            df_dict2["NLTK Positive Sentiment"] = pos_nltk_list
            df_dict2["NLTK Neutral Sentiment"] = neu_nltk_list
            df_dict2["NLTK Negative Sentiment"] = neg_nltk_list

            print(df_dict)
            df0 = pd.DataFrame(df_dict)
            df1_0 = pd.DataFrame(df_dict2)
            df2 = analysis2(topic_list, "Topic", sentiment_list)
            df3 = analysis2(lemma_list, "Lemma", sentiment_list)
            df4 = analysis2(phrase_list, "Phrase", sentiment_list)
            df5 = traits(combined_text, client, language, "emotional-traits", 9950)
            df6 = traits(combined_text, client, language, "behavioral-traits", 9950)

            # Create a Pandas Excel writer using XlsxWriter as the engine.
            writer = pd.ExcelWriter(output_file, engine='xlsxwriter',engine_kwargs={'options': {'strings_to_numbers': True}})

            # Write each dataframe to a different worksheet.
            df0.to_excel(writer, index=False, sheet_name='Overall Analysis')
            df1.to_excel(writer, index=False, sheet_name='Expert Sentiment Analysis')
            df1_0.to_excel(writer, index=False, sheet_name='Sentiment Comparison')
            df1_1.to_excel(writer, index=False, sheet_name='Sentiment Analysis')
            df2.to_excel(writer, index=False, sheet_name='Topics')
            df3.to_excel(writer, index=False, sheet_name='Lemmas')
            df4.to_excel(writer, index=False, sheet_name='Phrases')
            df5.to_excel(writer, index=False, sheet_name='Emotional Traits')
            df6.to_excel(writer, index=False, sheet_name='Behavioral Traits')

            # Close the Pandas Excel writer and output the Excel file.
            writer.close()
            return True
        except Exception as e:
            print("An error occurred: ", e)
            traceback.print_exc()
            return False
