from src.machine_learning.SentimentAnalysis import SentimentAnalysis

def test_sentiment_analysis_btc_fud_one():
    text = 'Bitcoin is actually highly centralized, with supermajority controlled by handful of big mining (aka hashing) companies. A single coal mine in Xinjiang flooded, almost killing miners, and Bitcoin hash rate dropped 35%. Sound “decentralized” to you?'
    score = SentimentAnalysis.analyze_text_sentiment(text, ['BTC'])
    assert score == 0.2

def test_sentiment_analysis_btc_fud_two():
    text = "Tesla has suspended vehicle purchases made using bitcoin. We are concerned about the rapidly increasing use of fossil fuels for Bitcoin mining and transactions, especially coal, which has the worst emissions of any fuel.\n Cryptocurrency is a good idea on many levels and we believe it has a promising future, but this cannot come at great cost to the environment.\n. TSLA will continue to hold BTC"
    score = SentimentAnalysis.analyze_text_sentiment(text, ['bitcoin'])
    assert score == 0.2

def test_sentiment_analysis_positive():
    text = "I like etsy!"
    score = SentimentAnalysis.analyze_text_sentiment(text, ['ETSY'])
    assert score == 0.52

def test_sentiment_analysis_none():
    text = "I am the senate"
    score = SentimentAnalysis.analyze_text_sentiment(text, ['senate'])
    assert score is None