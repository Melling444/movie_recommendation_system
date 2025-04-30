import sys
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from datetime import timedelta
import os
import boto3
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

def load_data():
    
    bucket_name = 'practice-bucket-24'
    file_key = 'rotten_tomatoes_data.csv'
    github_url = 'https://raw.githubusercontent.com/Melling444/movie_recommendation_system/main/rotten_tomatoes_data.csv'

    try:
        print("🔄 Attempting to load dataset from S3...")
        s3_client = boto3.client('s3',
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
        )
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        df = pd.read_csv(response['Body'])
        print("✅ Loaded dataset from S3.")
    except (NoCredentialsError, Exception) as e:
        print(f"⚠️ AWS load failed: {e}")
        print("🔁 Falling back to GitHub CSV...")
        df = pd.read_csv(github_url)
        print("✅ Loaded dataset from GitHub.")

    return df

df = load_data()

df.rename(columns = {'Unnamed: 0' : 'id'}, inplace= True)

for col in df.columns:
    if 'Aspect Ratio' in col:
        df[col] = df[col].astype('object')

df['Audience Score'] = df['Audience Score'].str.replace('%', '').astype(float) / 100

df['Critic Score'] = df['Critic Score'].str.replace('%', '').astype(float) / 100

df['Release Date (Streaming)'] = pd.to_datetime(df['Release Date (Streaming)'], format = 'mixed')

df[['Release Date (Theaters)', 'Release Type']] = df['Release Date (Theaters)'].astype('string').str.extract(r'([A-Za-z]{3} \d{1,2}, \d{4})(?:,\s*(\w+))?')

df['Release Date (Theaters)'] = pd.to_datetime(df['Release Date (Theaters)']).replace({pd.NA: np.nan})

#add a section for rerelease?

df['Release Type'] = df['Release Type'].astype(object).replace({pd.NA: np.nan})

def str_to_float(value):

    if pd.isna(value):
        return None 
    if isinstance(value, (int, float)):
        return value 

    value = value.replace('$', '').strip()

    if value.endswith('B'):
        return float(value[:-1]) * 1_000_000_000
    elif value.endswith('M'):
        return float(value[:-1]) * 1_000_000
    elif value.endswith('K'):
        return float(value[:-1]) * 1_000
    else:
        return float(value)

df['Box Office (Gross USA)'] = df['Box Office (Gross USA)'].apply(str_to_float)

def convert_time(time_str):
    if pd.isna(time_str) or not isinstance(time_str, str):
        return pd.NA, pd.NA  # Handle missing or non-string values
    
    time_str = time_str.strip()

    try:
        hours = int(time_str.split('h')[0].strip())
        minutes = int(time_str.split('h')[1].split('m')[0].strip())
    except (IndexError, ValueError):
        return pd.NA, pd.NA  # Handle bad formatting gracefully

    time_duration = timedelta(hours=hours, minutes=minutes)
    total_minutes = hours * 60 + minutes

    time_str_format = str(time_duration).split(' ')[-1]

    return time_str_format, total_minutes


df[['time_duration', 'total_minutes']] = df['Runtime'].apply(lambda x: pd.Series(convert_time(x)))


s_list = ['Cast', 'Director', 'Producer', 'Screenwriter', 'Genre']

for i in s_list:
    df[i] = df[i].str.split(', ')

categorical_cols = df.select_dtypes(object).columns

int_cols = df.select_dtypes([float, 'int64']).columns

all_cols = df.columns

df[categorical_cols] = df[categorical_cols].fillna("")

df[["Critic Score", "Audience Score"]] = df[["Critic Score", "Audience Score"]].fillna(0.50)

tfidf = TfidfVectorizer(stop_words = 'english')

tfidf_matrix = tfidf.fit_transform(df['Synopsis'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

feature_names = np.array(tfidf.get_feature_names_out())

def extract_keywords(row_idx, top_n = 4):
    row = tfidf_matrix[row_idx].toarray().flatten()
    top_indices = row.argsort()[-top_n:][::-1]
    return feature_names[top_indices].tolist()

df['keywords'] = [extract_keywords(i) for i in range(len(df))]

clean_titles = df[['Movie Title']].drop_duplicates().copy()

indices = pd.Series(clean_titles.index, index = clean_titles['Movie Title'].drop_duplicates().str.strip().str.lower())

def get_recommendations(title, cosine_sim = cosine_sim):

    normalize_titles = [t.strip().lower() for t in title]

    valid_titles = [t for t in normalize_titles if t in indices.index]
    invalid_titles = [t for t in normalize_titles if t not in indices.index]

    if not valid_titles:
        return ["Movie not found"]
    new = []
    for i in valid_titles:
        idx = indices[i]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key = lambda x: x[1], reverse = True)  
        sim_scores = sim_scores[1:6]
        new.extend(sim_scores)
    
    unique = {}
    for idx, score in new:
        if idx not in unique or score > unique[idx]:
            unique[idx] = score
    
    sorted_indices = sorted(unique.items(), key = lambda x: x[1], reverse = True)
    final_indices = [idx for idx, score in sorted_indices]
    final_indices = final_indices[:5]

    return df['Movie Title'].iloc[final_indices].tolist()

soup_list = ['Cast', 'Director', 'Producer', 'Screenwriter', 'Genre', 'keywords']

def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    else:
        if isinstance(x, str):
            return str.lower(x.replace(" ", ""))
        else:
            return ''

for feature in soup_list:
    df[feature] = df[feature].apply(clean_data)

def create_soup(x):
    return ' '.join(
        map(str, x.get('keywords', []))
    ) + ' ' + ' '.join(
        map(str, x.get('Cast', []))
    ) + ' ' + str(
        x.get('Director', '')
    ) + ' ' + ' '.join(
        map(str, x.get('Genre', []))
    ) + ' ' + ' '.join(
        map(str, x.get('Screenwriter', []))
    )
df['soup'] = df.apply(create_soup, axis=1)

count = CountVectorizer(stop_words = 'english')
count_matrix = count.fit_transform(df['soup'])

cosine_sim2 = cosine_similarity(count_matrix, count_matrix) 

@app.route('/recommend', methods = ['POST'])
def recommend():
    input_string = request.json.get('input')
    if not input_string:
        return jsonify({'error': 'No input provided'}), 400

    input_list = [item.strip() for item in input_string.split(',')]
    recommendations = get_recommendations(title=input_list, cosine_sim=cosine_sim2)
    return jsonify({'recommendations': recommendations})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)