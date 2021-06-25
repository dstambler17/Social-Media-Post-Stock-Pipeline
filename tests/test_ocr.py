from src.machine_learning.OCR import OCR

def test_sentiment_analysis():
    res = OCR.get_text_from_image('https://pbs.twimg.com/media/E1OEK8jVEAMEv5A?format=jpg&name=medium')
    assert "Tesla will not be selling any Bitcoin and" in res

def test_ocr_rocket():
    res = OCR.get_text_from_image('https://pbs.twimg.com/media/EwvnaXyW8AQKlNz.jpg')
    assert res is None

def test_special_meme():
    res = OCR.get_text_from_image('https://pbs.twimg.com/media/EdK4VrtUYAAaQ-h.jpg')
    assert res is None