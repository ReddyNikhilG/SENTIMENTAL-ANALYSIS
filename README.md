# Sentiment Analysis App

## Project Overview

This repository now includes a **Streamlit** application for sentiment analysis. The app accepts user text, classifies it as **Positive, Negative, or Neutral**, shows a 0-4 score, confidence, emoji feedback, analysis history, charts, and CSV export.

The Streamlit version uses a lightweight local sentiment engine so it is easier to run and deploy on Streamlit Cloud.

## Features

- Text sentiment classification
- Streamlit web UI
- Live sentiment summary after analysis
- Session-based history tracking
- Score, confidence, and emoji output
- Sentiment score chart and keyword focus view
- CSV download for recent analyses

## Technologies Used

- Python
- Streamlit
- pandas
- Altair
- vaderSentiment

## Project Structure

```text
SENTIMENTAL-ANALYSIS
├── app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── src/
│   └── main/
│       └── java/
│           └── devxplaining/sentimentanalysis/
│               └── ... original Spring Boot sources
└── README.md
```

## Run Locally

1. Create or activate the virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Deploy to Streamlit Cloud

1. Push this repository to GitHub.
2. Create a new app in Streamlit Cloud.
3. Set the main file path to `app.py`.
4. Keep `requirements.txt` in the repository root.

## Notes

- History is stored in the current Streamlit session only.
- The original Java Spring Boot source remains in the repository, but the Streamlit app is now the primary runnable interface.
