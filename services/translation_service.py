import os
import requests

GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")

def translate_to_english(text: str, src_lang: str = "auto") -> str:
    """
    Translate text to English using Google Translate API.
    """
    if not GOOGLE_TRANSLATE_API_KEY:
        raise ValueError("GOOGLE_TRANSLATE_API_KEY is not set")
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        "q": text,
        "source": src_lang,
        "target": "en",
        "format": "text",
        "key": GOOGLE_TRANSLATE_API_KEY,
    }
    response = requests.post(url, data=params)
    resp_json = response.json()
    return resp_json["data"]["translations"][0]["translatedText"]

# For dev/test (if you don't have an API key)
def fake_translate_to_english(text: str, src_lang: str = "auto") -> str:
    # Simply returns the input text, simulating a translation
    return text
