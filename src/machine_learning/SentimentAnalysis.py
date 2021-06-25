
import random
import logging
import statistics
import pandas as pd
from src.utils.custom_decorators import time_func
from nltk.sentiment.vader import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

class SentimentAnalysis:
    
    @staticmethod
    def scale_compound_score(compound_score, text):
        '''
        Effecitvely takes
        in a score between -1 and 1, and then converts
        (based on predetermined rules) what the score will be
        '''
        if compound_score == 0: #if 0, then the sentiment analysis didn't work, so need to log
            logger.info("ERROR, NLTK WAS NOT ABLE TO ANALYZE THE SENTIMENT of this statement: %s" % text)
            return None

        if compound_score >= 0.5:
            return 0.75
        elif compound_score < 0.5 and compound_score >= 0:
            return 0.52
        elif compound_score < 0 and compound_score >= -0.5:
            return 0.39
        else:
            return 0.2

    @staticmethod
    @time_func
    def analyze_text_sentiment(text, mentioned_words) -> float:
        sent_analysis_list = [[word, text] for word in mentioned_words]
        nltk_vader = SentimentIntensityAnalyzer()
        columns = ['ticker', 'post']

        post_df = pd.DataFrame(sent_analysis_list, columns=columns)

        scores = post_df['post'].apply(nltk_vader.polarity_scores).tolist()
        mean_compound_score = statistics.mean([score['compound'] for score in scores])

        final_score = SentimentAnalysis.scale_compound_score(mean_compound_score, text)
        if final_score is not None:
            logger.info("returning a final sentiment score of %f for this text: %s" % (final_score, text))
        print(final_score)
        return final_score

