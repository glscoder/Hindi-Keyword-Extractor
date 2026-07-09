import re

# -------------------------------------------------------------------------
# 1. TITANIUM-GRADE HINDI STOPWORDS
# -------------------------------------------------------------------------
HINDI_STOPWORDS = {
    # Pronouns & Basics
    "मैं", "हम", "तुम", "आप", "वह", "वे", "यह", "ये", 
    "मेरा", "मेरी", "मेरे", "हमारा", "हमारी", "हमारे", 
    "तुम्हारा", "तुम्हारी", "तुम्हारे", "आपका", "आपकी", "आपके",
    "उसका", "उसकी", "उसके", "उनका", "उनकी", "उनके", 
    "इसका", "इसकी", "इसके", "इनका", "इनकी", "इनके",
    "अपना", "अपनी", "अपने", "स्वयं", "खुद", "उनमें", "इनमें",
    "नहीं", "ना", "न", "मत", "उन्होंने", "इन्होंने", "उन्होने",
    "एक", "दो", "तीन", "कभी", "अभी", "जभी", "तभी",
    
    # Prepositions & Conjunctions
    "का", "की", "के", "को", "में", "पे", "पर", "से", "ने", "तक", 
    "लिए", "लिये", "द्वारा", "साथ", "बाद", "पहले", "बीच", "ऊपर", 
    "नीचे", "सामने", "पीछे", "तरफ", "अंदर", "बाहर", "दौरान", "संग", "तहत",
    "और", "एवं", "तथा", "या", "कि", "जो", "क्योंकि", "चूंकि",
    "लेकिन", "किंतु", "परंतु", "मगर", "वरना", "बल्कि", 
    "इसलिए", "ताकि", "अगर", "यदि", "तो", "भी", "ही", 
    
    # Verbs (Auxiliary & Common)
    "है", "हैं", "हूँ", "हो", "था", "थी", "थे", "थीं", 
    "गा", "गी", "गे", "हूंगा", "हुंगी", "होगे", "होगी",
    "हुआ", "हुई", "हुए", "हुये", "होना", "होता", "होती", "होते",
    "रहा", "रही", "रहे", "सकता", "सक्ति", "सकते", "सका", "सकी",
    "चाहिए", "चाहिये", "गया", "गयी", "गए", "गये", "जा", "जाता", "जाती", "जाते",
    "करना", "कर", "करें", "करते", "करता", "करती", "किया", "किये", "कीजिए", "करने",
    "देना", "दे", "दी", "दिये", "दिया", "देते", "देता", "देती",
    "लेना", "ले", "ली", "लिये", "लिया", "लेते", "लेता", "लेती",
    "रखना", "रखा", "रखे", "पाना", "पाई", "पाए", "लगना", "लगा", "लगे",
    "बनाना", "बनी", "बने", "बना", "बनाया", "बनाए", "रख",
    "कहा", "कही", "कहते", "कहना", "कहे", "बोला", "बोली", "बोले", "बोलना", 
    "बताया", "बताई", "बताते", "बताना", "पूछा", "पूछी", "पूछते", "लिखा", "लिखी", 
    "माना", "मानी", "माने", "समझा", "समझे", "साबित", "स्थापित", "निर्माण",
    
    # Generic Adjectives/Nouns & Junk
    "अच्छा", "अच्छी", "अच्छे", "बुरा", "बूरी", "बुरे",
    "बहुत", "कम", "ज्यादा", "अधिक", "काफी", "बिलकुल", "थोड़ा", "थोड़ी", 
    "पूरा", "पूरी", "पूरे", "सिर्फ", "केवल", "मात्र", "शायद", "अक्सर", "हमेशा", 
    "लगातार", "फिर", "भी", "जैसे", "वैसे", "तैसे", "ऐसे", "मानो", 
    "जब", "तब", "अब", "कई", "कुछ", "सभी", "सब", "हर", "प्रत्येक",
    "तरह", "रूप", "वाले", "वाला", "वाली", "सहित", "आदि", "इत्यादि",
    "वगैरह", "चीज", "बात", "जगह", "नाम", "भाग", "हिस्सा", "श्रेणी", "रूप",

    # 🚨 BANNED TIME WORDS (Hides 'Aaj/Kal' but preserves dates)
    "आज", "कल", "परसों", "सुबह", "शाम", "रात", "दिन", "दोपहर"
}

# -------------------------------------------------------------------------
# 2. ENGLISH STOPWORDS
# -------------------------------------------------------------------------
ENGLISH_STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
    "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "can", "will", "just", "don", "should", "now",
    "example", "examples", "compare", "compares", "comparing", "contrast", "contrasts",
    "note", "noting", "notes", "highlight", "highlighting", "highlights", "key",
    "include", "includes", "including", "feature", "features", "suggest", "suggests",
    "create", "creates", "creating", "creation", "make", "makes", "making",
    "use", "uses", "using", "work", "works", "working", "live", "lives", "living",
    "love", "loves", "loving", "say", "says", "said", "go", "goes", "going", "come", "came",
    "allows", "allow", "allowing", "completed", "complete", "completing", "ensure", "ensures",
    "establish", "establishing", "established", "remain", "remains", "remaining",
    "every", "everywhere", "everyone", "everything", "near", "nearest", "nearby",
    "since", "until", "upon", "whenever", "wherever", "whichever",
    "one", "two", "three", "first", "second", "third", "also", "like", "really",
    "mostly", "currently", "recently", "usually", "always", "never", "sometimes",
    "often", "across", "beyond", "behind", "within", "without", "especially",
    "specifically", "actually", "basically", "literally", "simply", "merely",
    "surrounding", "environment", "bodies", "similarities", "differences",
    "complex", "deeply", "effective", "essential", "various", "diverse",
    "furthermore", "ways", "way", "set", "sets", "well", "good", "bad", "great",
    "throughout", "ultimately", "foundation", "framework", "focus"
}

# -------------------------------------------------------------------------
# 3. COMPILED REGEX OPTIMIZATIONS
# -------------------------------------------------------------------------
HI_PUNCTUATION = re.compile(r"[\u0964\u0965.,!?:;\"'()]") 
HI_CLEANER = re.compile(r"[^\u0900-\u097F0-9a-zA-Z\-\s]")
EN_CLEANER = re.compile(r"[^a-z0-9\-\s]")
WHITESPACE = re.compile(r"\s+")

def preprocess_text(text: str, lang: str = 'hi') -> str:
    if not text or not isinstance(text, str):
        return ""

    if lang == 'hi':
        text = text.replace("/", " ").replace("-", " ")
        text = HI_PUNCTUATION.sub(" ", text) 
        text = HI_CLEANER.sub(" ", text)
        text = WHITESPACE.sub(" ", text).strip()
        words = text.split()
        cleaned_words = [w for w in words if w not in HINDI_STOPWORDS]
        
    else: 
        text = text.lower()
        text = text.replace("/", " ").replace("-", " ")
        text = EN_CLEANER.sub(" ", text)
        text = WHITESPACE.sub(" ", text).strip()
        words = text.split()
        cleaned_words = [w for w in words if w not in ENGLISH_STOPWORDS]

    return " ".join(cleaned_words)