import re
from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator
from preprocess import preprocess_text

# Direct Import
from tfidf_model import extract_tfidf_keywords

app = Flask(__name__)

def validate_language(text, lang):
    if lang == 'hi':
        pattern = re.compile(r'[\u0900-\u097F]')
        return bool(pattern.search(text))
    else:
        pattern = re.compile(r'[a-zA-Z]')
        return bool(pattern.search(text))

# --- SMART CATEGORIZATION LOGIC ---
def categorize_keywords(keywords, original_text, lang):
    
    if lang == 'hi':
        CAT_DATES = "📅 तिथियाँ और समय"
        CAT_ENTITIES = "👤 नाम और स्थान"
        CAT_THEMES = "✨ मुख्य विषय"
    else:
        CAT_DATES = "📅 Dates & Timelines"
        CAT_ENTITIES = "👤 Names & Entities"
        CAT_THEMES = "✨ Core Themes"

    grouped = {CAT_DATES: [], CAT_ENTITIES: [], CAT_THEMES: []}
    
    # Regex for Years (1000-2999)
    year_pattern = r'\b[12]\d{3}\b'
    
    # Strict Date Regex: "28 2 2026" or "28 02 2026"
    # Matches: 1-2 digits, space, 1-2 digits, space, 4 digits
    strict_full_date = r'\b\d{1,2}\s\d{1,2}\s\d{4}\b'

    en_time_words = {
        "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "today", "tomorrow", "yesterday", "morning", "evening", "night", "daily", "weekly", "annual", "year", "month",
        "decade", "century", "era", "ad", "bc", "time"
    }
    
    hi_time_words = {
        "जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर",
        "सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार",
        "वर्ष", "साल", "महीना", "तारीख", "बजे", "घंटा", "मिनट",
        "सप्ताह", "दशक", "शताब्दी", "युग", "समय", "ईस्वी", "सन", "संवत",
        "आज", "कल", "परसों", "सुबह", "शाम", "रात", "दिन", "दोपहर"
    }

    def is_pure_date(phrase, lang):
        words = phrase.lower().split()
        time_set = hi_time_words if lang == 'hi' else en_time_words
        for w in words:
            if w.isdigit(): continue
            if w not in time_set: return False
        return True

    # 1. INITIAL SORTING
    for kw in keywords:
        kw_lower = kw.lower()
        categorized = False

        # --- A. DATES CHECK ---
        if re.search(strict_full_date, kw): # "28 2 2026" -> Instant Date
            grouped[CAT_DATES].append(kw)
            categorized = True
        elif re.search(year_pattern, kw):
            if is_pure_date(kw, lang):
                grouped[CAT_DATES].append(kw)
                categorized = True
        elif (lang == 'en' and any(t in kw_lower for t in en_time_words)) or \
             (lang == 'hi' and any(t in kw for t in hi_time_words)):
            if is_pure_date(kw, lang):
                grouped[CAT_DATES].append(kw)
                categorized = True
        
        if categorized: continue

        # --- B. ENTITIES CHECK ---
        if lang == 'en':
            pattern = r'\b' + re.escape(kw.title()) + r'\b'
            if re.search(pattern, original_text) and not kw.isdigit():
                grouped[CAT_ENTITIES].append(kw)
                categorized = True
            elif kw.isupper() and len(kw) > 1: 
                grouped[CAT_ENTITIES].append(kw)
                categorized = True
        else: 
            name_suffixes = ["जी", "बाई", "भाई", "लाल", "राव", "साहब", "अली", "बली", "देवी", "कुमार", "सिंग", "सिंह", "पाटिल", "जाधव", "राणा", "प्रताप", "अकबर", "हुमायूँ", "शेरशाह"]
            context_words = ["बाजार", "मन्नत", "शहर", "गाव", "स्थान", "मंडल", "समूह", "योजना", "मंदिर", "नगर", "राज्य", "देश", "युद्ध", "किला", "गढ़", "कुंभलगढ़", "हल्दीघाटी", "स्वागत", "सिंगापुर", "गोवा"]
            
            for s in name_suffixes:
                if kw.endswith(s) or s in kw:
                    grouped[CAT_ENTITIES].append(kw)
                    categorized = True
                    break
            if not categorized:
                if any(c in kw for c in context_words):
                     grouped[CAT_ENTITIES].append(kw)
                     categorized = True

        if categorized: continue

        # --- C. THEMES ---
        grouped[CAT_THEMES].append(kw)

    # 2. CLEANUP PHASE (The Fix for "2 2026" leaking into Themes)
    # If a theme is just a substring of a Date we already found, kill it.
    final_themes = []
    found_dates = grouped[CAT_DATES]
    
    for theme in grouped[CAT_THEMES]:
        is_junk = False
        # Check if theme is inside any date (e.g. "2 2026" inside "28 2 2026")
        for d in found_dates:
            if theme in d:
                is_junk = True
                break
        
        # Check if theme is just a standalone broken number
        if theme.replace(" ", "").isdigit():
            is_junk = True

        if not is_junk:
            final_themes.append(theme)
            
    grouped[CAT_THEMES] = final_themes
    
    return {k: v for k, v in grouped.items() if v}

@app.route('/', methods=['GET', 'POST'])
def index():
    cleaned_text = ""
    keywords = [] 
    text = ""
    error_message = None
    selected_lang = 'hi'
    is_categorized = False

    if request.method == 'POST':
        text = request.form.get('text', '')
        selected_lang = request.form.get('language', 'hi')
        
        if text:
            if not validate_language(text, selected_lang):
                if selected_lang == 'hi':
                    error_message = "⚠️ Error: No Hindi text detected. Please switch to English mode."
                else:
                    error_message = "⚠️ Error: No English text detected. Please switch to Hindi mode."
            else:
                cleaned_text = preprocess_text(text, lang=selected_lang)
                raw_keywords = extract_tfidf_keywords(text, top_n=20, lang=selected_lang)
                
                if raw_keywords:
                    keywords = categorize_keywords(raw_keywords, text, selected_lang)
                    is_categorized = isinstance(keywords, dict)
                else:
                    error_message = "⚠️ Text contained only stopwords."

    return render_template('index.html', 
                           text=text, 
                           cleaned_text=cleaned_text, 
                           keywords=keywords,
                           is_categorized=is_categorized,
                           error=error_message, 
                           selected_lang=selected_lang)

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text', '')
    source_lang = data.get('source_lang', 'hi')
    target_lang = 'en' if source_lang == 'hi' else 'hi'
    
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated_text = translator.translate(text)
        return jsonify({'status': 'success', 'translated_text': translated_text, 'target_lang': target_lang})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)