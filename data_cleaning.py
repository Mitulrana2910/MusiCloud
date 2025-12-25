import joblib
import pandas as pd
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download tokenizer if not already installed
nltk.download('punkt')
nltk.download('punkt_tab')

stemmer = PorterStemmer()

def tokenization(txt):
    tokens = nltk.word_tokenize(txt)
    stemming = [stemmer.stem(w) for w in tokens]
    return " ".join(stemming)

# 1. Load dataset
df = pd.read_csv("spotify_millsongdata.csv")

# 2. Sample 5000 rows and drop unnecessary column
df = df.sample(5000).drop('link', axis=1).reset_index(drop=True)

# 3. Clean text
df['text'] = (
    df['text']
    .str.lower()
    .replace(r'^\w\s', ' ')
    .replace(r'\n', ' ', regex=True)
)

# 4. Tokenize + Stem
df['text'] = df['text'].apply(tokenization)

# 5. TF-IDF Vectorization
tfidf = TfidfVectorizer(analyzer='word', stop_words='english')
matrix = tfidf.fit_transform(df['text'])

# 6. Similarity Matrix
similarity = cosine_similarity(matrix)

# 7. Save Pickle Files (Compressed)
joblib.dump(df, 'df.pkl', compress=3)
joblib.dump(similarity, 'similarity.pkl', compress=9)

print("Processing Completed. Files Saved Successfully!")
