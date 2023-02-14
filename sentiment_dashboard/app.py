import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from main import SentimentAnalyzer
import traceback
import os

st.set_page_config(layout="wide")

# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

csv_file = None
with st.expander("Upload a new file", expanded=True):
    st.warning("Please upload a CSV file with the first column containing the text to be analyzed.")
    csv_file = st.file_uploader("", type=["csv"])

if csv_file:
    # Perform operations on the file
    st.success("File uploaded")
    input_file = csv_file.name
    excel_file = "{}_Output.xlsx".format(input_file.strip(".csv"))
    show_uploader = False
    analyzer = SentimentAnalyzer()


    try:
        if analyzer.analyze_csv(input_file, excel_file):
            if excel_file is not None:
                # Inject CSS with Markdown
                st.markdown(hide_table_row_index, unsafe_allow_html=True)

                tab1, tab2, tab3, tab4, tab5 = st.tabs(["Sentiment", "Traits", "Topics", "Phrases", "Keywords"])

                ### --- LOAD DATAFRAME
                # excel_file = 'Amazon Product Reviews Medium_Output.xlsx'
                # excel_file = 'Learners Comments Guiding Principles_COMPLETE_Output.xlsx'
                # excel_file = 'AtHome_Output_Aug1.xlsx'
                # excel_file = 'twitter_@AtHomeStore_Output.xlsx'
                # excel_file = 'Comcast Verbatim_Output.xlsx'



                num_letter_dict = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i', 9: 'j', 10: 'k', 11: 'l', 12: 'm', 13: 'n', 14: 'o', 15: 'p', 16: 'q', 17: 'r', 18: 's', 19: 't', 20: 'u', 21: 'v', 22: 'w', 23: 'x', 24: 'y', 25: 'z'}
                with tab1:
                    st.title('Sentiment Analysis')
                    sheet_name = 'Sentiment Analysis'
                    avg_sentiment = pd.read_excel(excel_file, sheet_name, index_col=None, usecols = "B", header = 0, nrows=0)
                    avg_sentiment = avg_sentiment.columns.values[0]

                    pos_count = pd.read_excel(excel_file, sheet_name, index_col=None, usecols = "B", header = 3, nrows=0)
                    pos_count = pos_count.columns.values[0]

                    neg_count = pd.read_excel(excel_file, sheet_name, index_col=None, usecols = "B", header = 4, nrows=0)
                    neg_count = neg_count.columns.values[0]

                    neut_count = pd.read_excel(excel_file, sheet_name, index_col=None, usecols = "B", header = 5, nrows=0)
                    neut_count = neut_count.columns.values[0]

                    sentiment_count = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A:B',
                                       header=3)

                    sentiment_meter = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = avg_sentiment,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Average Sentiment"}))
                    sentiment_meter.update_traces(gauge_axis_range=[-100,100], selector=dict(type='indicator'))
                    col1a, col2a, col3a = st.columns([1,3,2])
                    col2a.plotly_chart(sentiment_meter)
                    col3a.header("Sentiment Counts")
                    col3a.metric("Positive", pos_count)
                    col3a.metric("Negative", neg_count)
                    col3a.metric("Neutral", neut_count)

                    sheet_name = 'Overall Analysis'
                    columns = pd.read_excel(excel_file,sheet_name=sheet_name).columns.tolist()
                    start = num_letter_dict[columns.index("Overall Sentiment")]
                    end = num_letter_dict[columns.index("Expert Sentiment")]
                    overall_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A,{}'.format(start),
                                       header=0)
                    sentiment = overall_df['Overall Sentiment'].unique().tolist()
                    sentiment_selection = st.slider('Sentiment Range:',
                                        min_value= min(sentiment),
                                        max_value= max(sentiment),
                                        value=(min(sentiment),max(sentiment)))

                    mask = (overall_df['Overall Sentiment'].between(*sentiment_selection))
                    number_of_result = overall_df[mask].shape[0]
                    st.markdown(f'*Available Results: {number_of_result}*')
                    # df_grouped = overall_df.rename(columns={'Overall Sentiment': 'Sentiment'})
                    # df_grouped = df_grouped.reset_index()

                    st.table(overall_df[mask])

                with tab2:
                    st.title('Traits')
                    col1, col2 = st.columns(2)

                    sheet_name = 'Emotional Traits'
                    emotional_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A:C',
                                       header=0)

                    # # --- PLOT PIE CHART
                    et_pie = px.pie(emotional_df.head(10),
                                    title='Emotional Traits Breakdown',
                                    values='Frequency',
                                    names='Categories')

                    col1.plotly_chart(et_pie)
                    col1.table(emotional_df)

                    sheet_name = 'Behavioral Traits'
                    behavioral_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A:C',
                                       header=0)

                    # # --- PLOT PIE CHART
                    bt_pie = px.pie(behavioral_df.head(10),
                                    title='Behavorial Traits Breakdown',
                                    values='Frequency',
                                    names='Categories')

                    col2.plotly_chart(bt_pie)
                    col2.table(behavioral_df)

                with tab3:
                    sheet_name = 'Topics'
                    st.title('Topics')
                    topic_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A:B',
                                       header=0)

                    pos_topic_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A,C',
                                       header=0)

                    neg_topic_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A,D',
                                       header=0)

                    # # --- PLOT PIE CHART
                    topic_pie = px.pie(topic_df.head(10),
                                    title='Topic Breakdown',
                                    values='Count',
                                    names='Topic')

                    pos_topic_df = pos_topic_df.sort_values(by=['Positive Count'], ascending=False)
                    positive_topic_pie = px.pie(pos_topic_df.head(10),
                                    title='Positive Topic Breakdown',
                                    values='Positive Count',
                                    names='Topic')

                    neg_topic_df = neg_topic_df.sort_values(by=['Negative Count'], ascending=False)
                    negative_topic_pie = px.pie(neg_topic_df.head(10),
                                        title='Negative Topic Breakdown',
                                        values='Negative Count',
                                        names='Topic')


                    # st.plotly_chart(topic_pie)

                    col1a, col2a, col3a = st.columns(3)
                    topic_pie.update_layout(width=500)
                    positive_topic_pie.update_layout(width=500)
                    negative_topic_pie.update_layout(width=500)
                    col1a.plotly_chart(topic_pie)
                    col1a.table(topic_df)
                    col2a.plotly_chart(positive_topic_pie)
                    col2a.table(pos_topic_df)
                    col3a.plotly_chart(negative_topic_pie)
                    col3a.table(neg_topic_df)

                with tab4:
                    sheet_name = 'Phrases'
                    st.title('Phrases')
                    phrase_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A:B',
                                       header=0)

                    pos_phrase_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A,C',
                                       header=0)

                    neg_phrase_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A,D',
                                       header=0)

                    # # --- PLOT PIE CHART
                    phrase_pie = px.pie(phrase_df.head(10),
                                    title='Phrase Breakdown',
                                    values='Count',
                                    names='Phrase')

                    pos_phrase_df = pos_phrase_df.sort_values(by=['Positive Count'], ascending=False)
                    positive_phrase_pie = px.pie(pos_phrase_df.head(10),
                                    title='Positive Phrase Breakdown',
                                    values='Positive Count',
                                    names='Phrase')

                    neg_phrase_df = neg_phrase_df.sort_values(by=['Negative Count'], ascending=False)
                    negative_phrase_pie = px.pie(neg_phrase_df.head(10),
                                        title='Negative Phrase Breakdown',
                                        values='Negative Count',
                                        names='Phrase')


                    # st.plotly_chart(phrase_pie)

                    col1a, col2a, col3a = st.columns(3)
                    phrase_pie.update_layout(width=500)
                    positive_phrase_pie.update_layout(width=500)
                    negative_phrase_pie.update_layout(width=500)
                    col1a.plotly_chart(phrase_pie)
                    col1a.table(phrase_df)
                    col2a.plotly_chart(positive_phrase_pie)
                    col2a.table(pos_phrase_df)
                    col3a.plotly_chart(negative_phrase_pie)
                    col3a.table(neg_phrase_df)

                with tab5:
                    sheet_name = 'Lemmas'
                    st.title('Lemmas')
                    lemma_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A:B',
                                       header=0)

                    pos_lemma_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A,C',
                                       header=0)

                    neg_lemma_df = pd.read_excel(excel_file,
                                       sheet_name=sheet_name,
                                       usecols='A,D',
                                       header=0)

                    # # --- PLOT PIE CHART
                    lemma_pie = px.pie(lemma_df.head(10),
                                    title='Lemma Breakdown',
                                    values='Count',
                                    names='Lemma')

                    pos_lemma_df = pos_lemma_df.sort_values(by=['Positive Count'], ascending=False)
                    positive_lemma_pie = px.pie(pos_lemma_df.head(10),
                                    title='Positive Lemma Breakdown',
                                    values='Positive Count',
                                    names='Lemma')

                    neg_lemma_df = neg_lemma_df.sort_values(by=['Negative Count'], ascending=False)
                    negative_lemma_pie = px.pie(neg_lemma_df.head(10),
                                        title='Negative Lemma Breakdown',
                                        values='Negative Count',
                                        names='Lemma')


                    # st.plotly_chart(lemma_pie)

                    col1a, col2a, col3a = st.columns(3)
                    lemma_pie.update_layout(width=450)
                    positive_lemma_pie.update_layout(width=450)
                    negative_lemma_pie.update_layout(width=450)
                    col1a.plotly_chart(lemma_pie)
                    col1a.table(lemma_df)
                    col2a.plotly_chart(positive_lemma_pie)
                    col2a.table(pos_lemma_df)
                    col3a.plotly_chart(negative_lemma_pie)
                    col3a.table(neg_lemma_df)
        else:
            print("Error")
    except Exception as e:
        print("An error occurred here: ", e)
        tb = traceback.format_exc()
        st.error(tb)
