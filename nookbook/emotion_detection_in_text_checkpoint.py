# -*- coding: utf-8 -*-
"""Emotion Detection in Text-checkpoint.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1CoQiAOsEfqgw3MkF2kpxpdPoZKYKY52H

# Emotions Detection in Text
"""

!pip install neattext

# EDA
import pandas as pd
import numpy as np

# Load Data Viz Pkgs
import seaborn as sns

# Load Text Cleaning Pkgs
import neattext.functions as nfx

# Load ML Pkgs
# Estimators
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB

# Transformers
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,classification_report,confusion_matrix

from google.colab import drive
drive.mount('/content/drive')

# Load Dataset
df = pd.read_csv("/content/drive/MyDrive/ICBT/MoodMap/emotion_dataset_raw.csv")

df.head()

# Value Counts
df['Emotion'].value_counts()

# Plot
sns.countplot(x='Emotion',data=df)

# Data Cleaning
dir(nfx)

# User handles
df['Clean_Text'] = df['Text'].apply(nfx.remove_userhandles)

# Stopwords
df['Clean_Text'] = df['Clean_Text'].apply(nfx.remove_stopwords)

"""## We are not removing Special Characters as some of the rows have just Special Characters and it'll result into empty row."""

df

# Features & Labels
Xfeatures = df['Clean_Text']
ylabels = df['Emotion']

"""# It is advisable to split before applying pipelines because it prevents data leakage."""

#  Split Data
x_train,x_test,y_train,y_test = train_test_split(Xfeatures,ylabels,test_size=0.3,random_state=42)

# Build Pipeline
from sklearn.pipeline import Pipeline

# LogisticRegression Pipeline
pipe_lr = Pipeline(steps=[('cv',CountVectorizer()),('lr',LogisticRegression())])

# Train and Fit Data
pipe_lr.fit(x_train,y_train)

pipe_lr

# Check Accuracy
pipe_lr.score(x_test,y_test)

# Make A Prediction
ex1 = "This book was so interesting it made me happy"

pipe_lr.predict([ex1])

# Prediction Prob
pipe_lr.predict_proba([ex1])

# To Know the classes
pipe_lr.classes_

# Save Model & Pipeline
import joblib
pipeline_file = open("../models/emotion_classifier_pipe_lr.pkl","wb")
joblib.dump(pipe_lr,pipeline_file)
pipeline_file.close()

