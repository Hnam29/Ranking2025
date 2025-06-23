# import os
# import pandas as pd
# import torch
# import numpy as np
# import re
# from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
# from underthesea import word_tokenize

# # Load model and tokenizer
# model_path = '5CD-AI/Vietnamese-Sentiment-visobert'
# tokenizer = AutoTokenizer.from_pretrained(model_path)
# config = AutoConfig.from_pretrained(model_path)
# model = AutoModelForSequenceClassification.from_pretrained(model_path)

# def load_stop_words(file_path):
#     with open(file_path, 'r') as file:
#         stop_words = file.read().splitlines()
#     return set(stop_words)

# vietnamese_stopwords = load_stop_words('/Users/vuhainam/Downloads/vietnamese-stopwords.txt')

# def clean_text(text):
#     """Preprocess text: remove special characters, numbers, and stopwords"""
#     if not isinstance(text, str) or text.strip() == "":
#         return ""
        
#     text = text.lower()  # Convert to lowercase
#     text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
#     text = re.sub(r'[^a-zA-ZÀ-ỹ0-9\s]', '', text)  # Remove special characters
#     words = word_tokenize(text)  # Tokenize words
#     words = [word for word in words if word not in vietnamese_stopwords]  # Remove stopwords
#     return ' '.join(words)

# # Function to predict sentiment
# def analyze_sentiment(text):
#     if not isinstance(text, str) or text.strip() == "":
#         return {"Positive": 0, "Neutral": 0, "Negative": 0}  # Handle empty or invalid text
    
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    
#     with torch.no_grad():
#         outputs = model(**inputs)
#         scores = outputs.logits.softmax(dim=-1).cpu().numpy()[0]
    
#     ranking = np.argsort(scores)[::-1]  # Sort scores in descending order
#     return {config.id2label[ranking[i]]: np.round(float(scores[ranking[i]]), 4) for i in range(scores.shape[0])}

# # Load dataset
# file_path = "/Users/vuhainam/Downloads/Reviews/Android/total.csv"
# df = pd.read_csv(file_path)

# # Clean content column
# df["content"] = df["content"].astype(str).apply(clean_text)

# # Batch processing sentiment analysis
# batch_size = 512  # Adjust batch size based on available memory
# sentiments = []
# for i in range(0, len(df), batch_size):
#     batch = df["content"].iloc[i:i+batch_size].tolist()
#     batch_sentiments = [analyze_sentiment(text) for text in batch]
#     sentiments.extend(batch_sentiments)

# df["Sentiment_Scores"] = sentiments

# # Extract sentiment percentages
# def extract_sentiments(sentiment_scores):
#     pos = sentiment_scores.get("POS", 0)
#     neu = sentiment_scores.get("NEU", 0)
#     neg = sentiment_scores.get("NEG", 0)
        
#     total = pos + neu + neg
#     if total == 0:
#         return pd.Series([0, 0, 0])  # Avoid division by zero
    
#     return pd.Series([pos * 100, neu * 100, neg * 100])  # Convert to percentage

# df[["Positive", "Neutral", "Negative"]] = df["Sentiment_Scores"].apply(extract_sentiments)

# # Extract dominant sentiment
# def extract_dominant_sentiment(sentiment_scores):
#     if not sentiment_scores:
#         return "Unknown"
    
#     dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
#     sentiment_mapping = {"POS": "Positive", "NEU": "Neutral", "NEG": "Negative"}
        
#     return sentiment_mapping.get(dominant_sentiment, "Unknown")

# df["Dominant_Sentiment"] = df["Sentiment_Scores"].apply(extract_dominant_sentiment)

# # Save the updated dataset as CSV instead of Excel
# output_file_path = "/Users/vuhainam/Downloads/sentiment_analysis.csv"
# df.to_csv(output_file_path, index=False)

# print(f"Sentiment analysis completed! Processed {len(df)} reviews.")
# print(f"Results saved to CSV file: {output_file_path}")



import os
import pandas as pd
import torch
import numpy as np
import re
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from underthesea import word_tokenize

# Load model and tokenizer
model_path = '5CD-AI/Vietnamese-Sentiment-visobert'
tokenizer = AutoTokenizer.from_pretrained(model_path)
config = AutoConfig.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

def load_stop_words(file_path):
    with open(file_path, 'r') as file:
        stop_words = file.read().splitlines()
    return set(stop_words)

# vietnamese_stopwords = load_stop_words('/Users/vuhainam/Downloads/vietnamese-stopwords.txt')

def clean_text(text):
    """Preprocess text: remove special characters, numbers, and stopwords"""
    if not isinstance(text, str) or text.strip() == "":
        return ""

    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = re.sub(r'[^a-zA-ZÀ-ỹ0-9\s]', '', text)  # Remove special characters
    words = word_tokenize(text)  # Tokenize words
    # words = [word for word in words if word not in vietnamese_stopwords]  # Remove stopwords
    return ' '.join(words)

# Function to predict sentiment
def analyze_sentiment(text):
    if not isinstance(text, str) or text.strip() == "":
        return {"Positive": 0, "Neutral": 0, "Negative": 0}  # Handle empty or invalid text

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)
        scores = outputs.logits.softmax(dim=-1).cpu().numpy()[0]

    ranking = np.argsort(scores)[::-1]  # Sort scores in descending order
    return {config.id2label[ranking[i]]: np.round(float(scores[ranking[i]]), 4) for i in range(scores.shape[0])}

# Load dataset
file_path = "/Users/vuhainam/Downloads/data_ios.xlsx"
df = pd.read_excel(file_path)

# Clean content column
df["content"] = df["review"].astype(str).apply(clean_text)

# Batch processing sentiment analysis
batch_size = 512  # Adjust batch size based on available memory
sentiments = []
for i in range(0, len(df), batch_size):
    batch = df["content"].iloc[i:i+batch_size].tolist()
    batch_sentiments = [analyze_sentiment(text) for text in batch]
    sentiments.extend(batch_sentiments)

df["Sentiment_Scores"] = sentiments

# Extract sentiment percentages
def extract_sentiments(sentiment_scores):
    pos = sentiment_scores.get("POS", 0)
    neu = sentiment_scores.get("NEU", 0)
    neg = sentiment_scores.get("NEG", 0)

    total = pos + neu + neg
    if total == 0:
        return pd.Series([0, 0, 0])  # Avoid division by zero

    return pd.Series([pos * 100, neu * 100, neg * 100])  # Convert to percentage

df[["Positive", "Neutral", "Negative"]] = df["Sentiment_Scores"].apply(extract_sentiments)

# Extract dominant sentiment
def extract_dominant_sentiment(sentiment_scores):
    if not sentiment_scores:
        return "Unknown"

    dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
    sentiment_mapping = {"POS": "Positive", "NEU": "Neutral", "NEG": "Negative"}

    return sentiment_mapping.get(dominant_sentiment, "Unknown")

df["Dominant_Sentiment"] = df["Sentiment_Scores"].apply(extract_dominant_sentiment)

df.drop('Sentiment_Scores',axis=1,inplace=True)

# Save the updated dataset as CSV instead of Excel
output_file_path = "/Users/vuhainam/Downloads/sentiment_analysis_ios.xlsx"
df.to_excel(output_file_path, index=False)

print(f"Sentiment analysis completed! Processed {len(df)} reviews.")