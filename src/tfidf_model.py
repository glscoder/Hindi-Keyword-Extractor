import re 
from sklearn.feature_extraction.text import TfidfVectorizer
from preprocess import HINDI_STOPWORDS, ENGLISH_STOPWORDS

def extract_tfidf_keywords(text, top_n=20, lang='hi'):
    try:
        # --- 1. THE HARD BOUNDARY FIX ---
        if lang == 'hi':
            # Replacing Danda with a hard punctuation mark (.)
            # Scikit-learn physically cannot cross punctuation to make n-grams!
            text = text.replace('।', '.').replace('॥', '.')
            token_pattern = r'(?u)[\u0900-\u097F0-9a-zA-Z]+' 
            ngram_range = (1, 3) 
            stop_words_list = list(HINDI_STOPWORDS)
        else:
            text = re.sub(r'[.!?;:\n\r]+', '.', text)
            token_pattern = r'(?u)\b[a-zA-Z0-9\-]+\b' 
            ngram_range = (1, 3)
            stop_words_list = list(ENGLISH_STOPWORDS)

        # Initialize core NLP Model
        vectorizer = TfidfVectorizer(
            analyzer="word",
            token_pattern=token_pattern,
            ngram_range=ngram_range,
            stop_words=stop_words_list,
            max_features=1000,
            sublinear_tf=True 
        )
        
        tfidf_matrix = vectorizer.fit_transform([text])
        features = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        
        # Sort entirely by Score to prevent forcing weird, long chunks
        raw_candidates = sorted(zip(features, scores), key=lambda x: x[1], reverse=True)
        
        # --- 2. JUNK FILTERING ---
        valid_candidates = []
        for phrase, score in raw_candidates:
            if phrase.isdigit() and len(phrase) != 4: 
                continue
            if lang == 'en' and len(phrase) < 3 and not phrase.isdigit(): 
                continue
            valid_candidates.append(phrase)

        # --- 3. THE BALANCED BUCKET STRATEGY ---
        unigrams, bigrams, trigrams = [], [], []
        
        for candidate in valid_candidates:
            wc = len(candidate.split())
            if wc == 1 and candidate not in unigrams: unigrams.append(candidate)
            elif wc == 2 and candidate not in bigrams: bigrams.append(candidate)
            elif wc >= 3 and candidate not in trigrams: trigrams.append(candidate)

        # Rebalanced to ensure Unigrams (Single words) return to the UI
        pool_size = top_n + 10 
        u_limit = int(pool_size * 0.40) # 40% Single words
        b_limit = int(pool_size * 0.40) # 40% Two-word pairs
        t_limit = int(pool_size * 0.20) # 20% Three-word phrases
        
        raw_mix = unigrams[:u_limit] + bigrams[:b_limit] + trigrams[:t_limit]
        
        if len(raw_mix) < pool_size:
            leftovers = unigrams[u_limit:] + bigrams[b_limit:] + trigrams[t_limit:]
            for phrase in leftovers:
                if phrase not in raw_mix: 
                    raw_mix.append(phrase)

        # --- 4. SMART DEDUPLICATION ---
        raw_mix.sort(key=len, reverse=True)
        final_keywords = []
        
        for candidate in raw_mix:
            is_overlap = False
            c_words = set(candidate.split()) 
            
            for existing in final_keywords:
                e_words = set(existing.split()) 
                
                # Only delete a word if it is completely inside a bigger phrase
                if c_words.issubset(e_words):
                    is_overlap = True
                    break

            if not is_overlap:
                final_keywords.append(candidate)
                
            if len(final_keywords) >= top_n:
                break
        
        # Final polish: Sort output shortest to longest so it looks organized on screen
        final_keywords.sort(key=len)
        return final_keywords
        
    except Exception as e:
        print(f"TFIDF Error: {e}")
        return []