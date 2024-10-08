import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import re
from wordcloud import WordCloud
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
from streamlit_lottie import st_lottie
from PIL import Image
import base64
import emoji
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import sklearn

# Download required NLTK data
nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Set page configuration
st.set_page_config(page_title="2024 Olympics Sentiment Analyzer", page_icon="🏅", layout="wide")

       
# Load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
    
st.markdown("---")

# Olympic ring colors
ring_colors = ["blue", "yellow", "black", "green", "red", "purple"]

# Create tabs
tabs = st.tabs(["🏠 Home", "📊 Analyzer", "📈 Dashboard", "👥 The Team", "ℹ️ Info", "💬 Feedback"])

# Apply Olympic ring colors to tabs and style them as rings
st.markdown(f"""
<style>
.stTabs {{
    display: flex;
    justify-content: space-evenly;
}}
    
.stTabs [data-baseweb="tab"] {{
    width: 100px;
    height: 100px;
    border-radius: 50%;
    border: 5px solid transparent;
    line-height: 60px;
    text-align: center;
    color: auto;
    font-weight: bold;
    transition: transform 0.3s ease; 
}}

.stTabs [data-baseweb="tab"]:nth-child(1) {{
    border-color: {ring_colors[0]};
}}

.stTabs [data-baseweb="tab"]:nth-child(2) {{
    border-color: {ring_colors[1]};
}}

.stTabs [data-baseweb="tab"]:nth-child(3) {{
    border-color: {ring_colors[2]};
}}

.stTabs [data-baseweb="tab"]:nth-child(4) {{
    border-color: {ring_colors[3]};
}}

.stTabs [data-baseweb="tab"]:nth-child(5) {{
    border-color: {ring_colors[4]};
}}

.stTabs [data-baseweb="tab"]:nth-child(6) {{
    border-color: {ring_colors[5]};
}}

.stTabs [data-baseweb="tab"]:hover {{
    transform: scale(1.1);
}}

</style>
""", unsafe_allow_html=True)

# Home tab
with tabs[0]:
    st.title("Welcome to the 2024 Paris Olympics Sentiment Analyzer")
    
    lottie_url = "https://lottie.host/fe78a580-e21b-4613-b5d6-cc64b1a934b7/vDApSHkH81.json"  
    lottie_json = load_lottieurl(lottie_url)
    st_lottie(lottie_json, height=200)
    st.write("Analyze sentiments of the 2024 Paris Olympics with our advanced tool.")

 
# Sentiment analyzer tab
with tabs[1]:
    st.title("Olympic Sentiment Analyzer")
    
    lottie_url = "https://lottie.host/83213d4d-0fde-4804-86d7-03b17919cf3b/nYDHta6PFS.json"  
    lottie_json = load_lottieurl(lottie_url)
    st_lottie(lottie_json, height=200)

     # Load the pickled VADER model
    with open('Models/vader_model.pkl', 'rb') as vader_file:
        loaded_vader = pickle.load(vader_file)
        
    def clean_tweet(tweet):
        # Remove URLs
        tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet, flags=re.MULTILINE)
        # Remove user @ references
        tweet = re.sub(r'\@\w+', '', tweet)
        return tweet.strip()
    
    # Function to get sentiment emoticon
    def get_sentiment_emoticon(sentiment):
        emoticons = {
            "POSITIVE": "😄",
            "NEUTRAL": "😐",
            "NEGATIVE": "😞"
        }
        return emoticons.get(sentiment, "❓") 

    # Function to analyze sentiment using VADER
    def analyze_sentiment_vader(text):
    
        # Use the VADER model to predict the sentiment
        vader_scores = loaded_vader.polarity_scores(text)
        
        # Determine sentiment based on VADER compound score
        compound_score = vader_scores['compound']
        if compound_score >= 0.05:
            sentiment = 'POSITIVE'
        elif compound_score <= -0.05:
            sentiment = 'NEGATIVE'
        else:
            sentiment = 'NEUTRAL'
        
        return sentiment, compound_score, get_sentiment_emoticon(sentiment)

    # Option to choose between manual input and file upload
    analysis_option = st.radio("Choose analysis option:", ["Manual Input", "File Upload"])

    if analysis_option == "Manual Input":
        tweet = st.text_area("Enter a tweet to analyze sentiment:")
        
        if st.button("Analyze"):
            if tweet:
                label, score, emoticon = analyze_sentiment_vader(tweet)
                st.markdown(f"""
                <div style="text-align: center;">
                    <span style="font-size: 100px;">{emoticon}</span>
                    <div style="font-size: 24px;">Sentiment: {label}</div>
                    <div style="font-size: 18px;">Confidence Score: {score:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Please enter a tweet before analyzing.")

    else:  # File Upload option
        uploaded_file = st.file_uploader("Upload a CSV or TXT file", type=["csv", "txt"])
        
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'): # .csv file
                df = pd.read_csv(uploaded_file)
                text_column = st.selectbox("Select the column containing the text to analyze:", df.columns)
            else:  # .txt file
                content = uploaded_file.getvalue().decode("utf-8")
                df = pd.DataFrame({"Text": content.split('\n')})
                text_column = "Text"

            if st.button("Analyze File"):
                # Apply sentiment analysis to each row
                results = [analyze_sentiment_vader(text) for text in df[text_column]]
                
                # Create new columns for sentiment, score and emoticon
                df['Sentiment'] = [r[0] for r in results]
                df['Score'] = [r[1] for r in results]
                df['Emoticon'] = [r[2] for r in results]

                # Display results
                st.write(df)

                # Display summary
                st.subheader("Summary")
                sentiment_counts = df['Sentiment'].value_counts()
                
                # Map sentiments to colors
                colors = sentiment_counts.index.map({
                    'POSITIVE': 'blue',
                    'NEGATIVE': 'red',
                    'NEUTRAL': 'gray'
                })
                
                # Create a bar plot color coded as per sentiment
                fig, ax = plt.subplots()
                sentiment_counts.plot(kind='bar', ax=ax, color=colors)
                plt.title("Sentiment Distribution")
                plt.xlabel("Sentiment")
                plt.ylabel("Count")
                st.pyplot(fig)

    st.markdown("---")

# Dashboard tab
with tabs[2]:
    st.title("Olympics Twitter Sentiment Stats")
    
    lottie_url = "https://lottie.host/a96d76d8-f260-420f-98be-03cf4f377403/NKKum85jXp.json"  # Olympic stats animation
    lottie_json = load_lottieurl(lottie_url)
    st_lottie(lottie_json, height=200)

    def preprocess_text(text):
        if not isinstance(text, str):
            return str(text)
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove user @ references and '#' from hashtags
        text = re.sub(r'\@\w+|\#', '', text)
        
        # Replace emojis with their text description
        text = emoji.demojize(text)
        
        # Remove non-alphanumeric characters
        text = re.sub(r'[^\w\s]', '', text)
        
        # Tokenize the text
        tokens = word_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        
        # Lemmatize the tokens
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        
        # Join the tokens back into a single string
        cleaned_text = ' '.join(tokens)
        
        return cleaned_text
    
    def preprocess_dataframe(df):
        
        # Preprocess the 'Tweet_Content' column
        df['Cleaned_Tweet'] = df['Tweet_Content'].apply(preprocess_text)
        
        # Convert 'Tweet_Timestamp' to datetime and extract date
        df['Tweet_Timestamp'] = pd.to_datetime(df['Tweet_Timestamp'])
        df['date'] = df['Tweet_Timestamp'].dt.date
        
        # Apply sentiment analysis
        df['sentiment'] = df['Cleaned_Tweet'].apply(lambda x: analyze_sentiment_vader(x)[0])
        df['sentiment_score'] = df['Cleaned_Tweet'].apply(lambda x: analyze_sentiment_vader(x)[1])
        
        return df

    uploaded_file = st.file_uploader("Upload a CSV file of The Paris Olympics-related tweets", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        # Preprocess the dataframe
        df = preprocess_dataframe(df)
    
        # 1. Word Cloud
        st.subheader("Word Cloud of Tweets")
        # Convert all Tweet_Content entries to strings and handle NaNs
        df['Tweet_Content'] = df['Tweet_Content'].astype(str).fillna('')
        # Join the tweets into a single text
        text = " ".join(tweet for tweet in df['Tweet_Content'])
        wordcloud = WordCloud(width=800, height=400, background_color='white', colormap="Dark2").generate(text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt)
        
        # 2. Sentiment Distribution
        st.subheader("Sentiment Distribution")
        fig, ax = plt.subplots()
        df['sentiment'].value_counts().plot(kind='bar', ax=ax , colormap="viridis")
        plt.title("Sentiment Distribution")
        plt.xlabel("Sentiment")
        plt.ylabel("Count")
        st.pyplot(fig)
        
        # 3. Sentiment Over Time
        st.subheader("Sentiment Over Time")
        daily_sentiment = df.groupby('date')['sentiment_score'].mean().reset_index()
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(daily_sentiment['date'], daily_sentiment['sentiment_score'], color='#000080')
        plt.title("Average Sentiment Score Over Time")
        plt.xlabel("Date")
        plt.ylabel("Average Sentiment Score")
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # 4. Top Hashtags
        st.subheader("Top Hashtags")
        hashtags = ' '.join(df['Tweet_Content'].apply(lambda x: ' '.join(re.findall(r'#\w+', x.lower())))).split()
        hashtag_counts = pd.Series(hashtags).value_counts().head(10)
        fig, ax = plt.subplots()
        hashtag_counts.plot(kind='bar', ax=ax, colormap="Dark2")
        plt.title("Top 10 Hashtags")
        plt.xlabel("Hashtag")
        plt.ylabel("Count")
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # 5. Tweet Volume Over Time
        st.subheader("Tweet Volume Over Time")
        tweet_volume = df.groupby('date').size().reset_index(name='count')
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(tweet_volume['date'], tweet_volume['count'], color='#FFD700')
        plt.title("Tweet Volume Over Time")
        plt.xlabel("Date")
        plt.ylabel("Number of Tweets")
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # 6. Most Common Words
        st.subheader("Most Common Words")
        stop_words = set(stopwords.words('english'))
        words = ' '.join(df['Tweet_Content']).lower().split()
        words = [word for word in words if word not in stop_words and len(word) > 3]
        word_freq = pd.Series(words).value_counts().head(20)
        fig, ax = plt.subplots(figsize=(12, 6))
        word_freq.plot(kind='bar', ax=ax, colormap="Dark2")
        plt.title("Top 20 Most Common Words")
        plt.xlabel("Word")
        plt.ylabel("Frequency")
        plt.xticks(rotation=45)
        st.pyplot(fig)
        

# Team tab
with tabs[3]:
    st.title("The Data Sentinels")
    # Load Lottie animation
    lottie_url = "https://lottie.host/18039274-4e01-4558-845e-a1d1d3b950eb/cKT9Btma01.json"  
    lottie_json = load_lottieurl(lottie_url)
    st_lottie(lottie_json, height=200)
    # Style contact icons
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .social-icon {
            font-size: 24px;
            margin-right: 10px;
            color: #1a1a1a;
            text-decoration: none;
        }
        .social-icon:hover {
            opacity: 0.7;
        }
    </style>
    """, unsafe_allow_html=True)
    # Team member details
    team_members = [
        {
            "name": "Ivy Atieng",
            "title": "Scrum Master",
            "bio": "Ivy is an experienced data scientist with a focus on natural language processing and sentiment analysis. She is our data pipeline expert and brings valuable insights to the team.",
            "image": "the_team/ivy.jpg",
            "github": "Atieng",
            "email": "atiengivylisa@gmail.com",
            "linkedin": "ivy-atieng/"
        },
        {
            "name": "Titus Kaluma",
            "title": "Project Manager",
            "bio": "Titus coordinates the team's efforts and ensures that we meet our project milestones. His background in both data science and project management keeps us on track and aligned with our goals.",
            "image": "the_team/titus.jpg",
            "github": "Kaluma-67",
            "email": "mwirigikaluma@gmail.com",
            "linkedin": "titus-mwirigi-62952972/"
        },
        {
            "name": "Elizabeth Masai",
            "title": "Data Visualization Specialist",
            "bio": "Elizabeth excels at creating insightful and interactive data visualizations. Her skills are essential for presenting our findings in a clear and impactful manner.",
            "image": "the_team/elizabeth.jpg",
            "github": "ElizabethMasai",
            "email": "elizabethchemtaim@gmail.com",
            "linkedin": "elizabeth-masai-6aab8118a"
        },
        {
            "name": "Sheila Mulwa",
            "title": "Data Narrative Architect",
            "bio": "Sheila blends her data science and machine learning expertise with creativity, turning complex datasets into insightful visual narratives. Her engaging presentations make our models and findings accessible to both technical and non-technical audiences.",
            "image": "the_team/sheila.jpg",
            "github": "Sheila-Mulwa",
            "email": "sheila.n.mulwa@gmail.com",
            "linkedin": "sheila-mulwa?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app"
        },
        {
            "name": "Evaclaire Munyika",
            "title": "Deployment Specialist",
            "bio": "Claire is our go-to expert for turning our sentiment analysis models into robust, scalable applications. Her knowledge of serverless computing allows us to deploy our sentiment analysis tools in a cost-effective and highly available manner.",
            "image": "the_team/claire.jpg",
            "github": "Eva-Claire",
            "email": "evamunyika@gmail.com",
            "linkedin": "evaclaire-munyika-991295114"
        }
    ]
    # Create two columns and loop through each member applying custom styles
    for member in team_members:
        col1, col2 = st.columns([1, 3])
        
        with col1: # Add member images
            try:
                image = Image.open(member["image"])
                st.image(image, width=150)
            except FileNotFoundError:
                st.image("https://via.placeholder.com/200", width=1500)
                
        with col2: # Apply custom styles
            st.markdown(f"""
            <style>
            .team-member {{
                background-color: #f0f0f0; 
                padding: 20px;
                border-radius: 15px; 
                border: 1px solid #ddd; 
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); 
                margin-bottom: 20px; 
            }}
            .member-name {{
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 5px;
                color: black;
            }}
            .member-title {{
                font-size: 16px;
                color: blue;
                margin-bottom: 10px;
                font-style: italic;
            }}
            .member-bio {{
                margin-bottom: 10px;
                color: black;
            }}
            .member-contact a {{
                margin-right: 10px;
                color: #007bff;
                text-decoration: none;
            }}
            .member-contact a:hover {{
                color: #0056b3;
            }}
            </style>
            <div class="team-member">
                <div class="member-name">{member['name']}</div>
                <div class="member-title">{member['title']}</div>
                <div class="member-bio">{member['bio']}</div>
                <div class="member-contact">
                    <a href="https://github.com/{member['github']}" target="_blank">
                        <i class="fab fa-github"></i>
                    </a>
                    <a href="mailto:{member['email']}">
                        <i class="far fa-envelope"></i>
                    </a>
                    <a href="https://www.linkedin.com/in/{member['linkedin']}" target="_blank">
                        <i class="fab fa-linkedin"></i>
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
# About tab
with tabs[4]:
    st.title("About The App")
    # Load lottie animation
    lottie_url = "https://lottie.host/93047e01-af1c-425a-89f5-c4d49abc3aaa/LVMzN5PPXM.json"  
    lottie_json = load_lottieurl(lottie_url)
    st_lottie(lottie_json, height=200)
    
    st.write(""" The Olympic Sentiment Analyzer is a powerful tool designed to analyze public sentiment surrounding the 2024 Paris Olympic Games. Our application leverages advanced natural language processing and machine learning techniques to process large volumes of text data from X and user-submitted content.
    
Key features:

⭐️Real-time sentiment analysis of Olympic-related tweets

⭐️User-friendly interface for analyzing individual tweets or batch uploads

⭐️Comprehensive dashboard with visualizations of sentiment trends, word clouds and key statistics

⭐️Ability to track sentiment changes over time and identify emerging topics
   
Our goal is to provide valuable insights into the global conversation surrounding this major sporting event.
    
Developed by a team of passionate data scientists and machine learning experts, the Olympic Sentiment Analyzer combines cutting-edge technology with a user-friendly interface to make complex data analysis accessible to all.

We invite you to explore the app, analyze tweets and gain insights into the pulse of the 2024 Paris Olympics. Your feedback is crucial in helping us improve and refine our tool so please don't hesitate to share your thoughts and suggestions.
""")


# Feedback tab
with tabs[5]:
    st.title("We Value Your Feedback")
    
    st.subheader("Share Your Thoughts")
    feedback = st.text_area("What do you think about our Olympic Sentiment Analyzer?")
    
    if st.button("Submit Feedback"):
        if feedback:
            st.success("Thank you for your feedback!")
        else:
            st.warning("Please enter your feedback before submitting.")

    st.markdown("---")
            
    st.subheader("Rate Our App")

    rating = st.radio("Select your rating:", options=[1, 2, 3, 4, 5], index=2)
    
    if st.button("Submit Rating"):
        st.success(f"Thank you for rating us {rating} star(s)!")



# Footer 
st.markdown("---")
st.markdown("© 2024 Olympic Sentiment Analyzer. All rights reserved.")
