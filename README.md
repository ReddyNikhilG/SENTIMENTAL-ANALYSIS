# Sentiment Analysis Web Application

## 📌 Project Overview

This project is a **Sentiment Analysis Web Application** built using **Java Spring Boot**.
The system analyzes the sentiment of user-provided text and classifies it into **Positive, Negative, or Neutral** sentiment.

Sentiment analysis is a Natural Language Processing (NLP) technique used to determine the emotional tone behind a piece of text. It is widely used to analyze opinions, reviews, and social media comments. ([ResearchGate][1])

This application provides a **simple web interface** where users can enter text and instantly view the predicted sentiment.

---

## 🚀 Features

* Text sentiment classification
* Web-based user interface
* Real-time sentiment prediction
* Simple and clean UI
* REST controller using Spring Boot
* Lightweight and easy to run locally

---

## 🛠️ Technologies Used

### Backend

* Java
* Spring Boot
* Maven

### Frontend

* HTML
* CSS
* Thymeleaf

### Tools

* Git
* GitHub
* Visual Studio Code
* IntelliJ IDEA (optional)

---

## 📂 Project Structure

```
SENTIMENTAL-ANALYSIS
│
├── src
│   └── main
│       ├── java
│       │   └── devxplaining.sentimentanalysis
│       │       ├── App.java
│       │       ├── SentimentController.java
│       │       ├── SentimentService.java
│       │       └── SentimentResult.java
│       │
│       └── resources
│           ├── templates
│           │   └── index.html
│           └── static
│               └── css
│                   └── style.css
│
├── pom.xml
└── README.md
```

---

## ⚙️ Installation and Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/ReddyNikhilG/SENTIMENTAL-ANALYSIS.git
```

### 2️⃣ Navigate to the Project Folder

```
cd SENTIMENTAL-ANALYSIS
```

### 3️⃣ Run the Spring Boot Application

Using Maven:

```
mvn spring-boot:run
```

Or run the **App.java** file directly from your IDE.

---

## 🌐 Access the Application

Once the server starts, open your browser and go to:

```
http://localhost:8080
```

Enter a sentence and the system will predict the sentiment.

---

## 📊 Example

Input:

```
I love this product!
```

Output:

```
Sentiment: Positive
```

---

## 🎯 Use Cases

Sentiment analysis applications include:

* Customer feedback analysis
* Product review monitoring
* Social media opinion analysis
* Brand reputation tracking

Organizations use sentiment analysis to analyze large volumes of user-generated text and understand public opinion. ([ResearchGate][1])

---

## 👨‍💻 Author

**Reddy Nikhil**

B.Tech Computer Science (AI & ML) Student

GitHub:
https://github.com/ReddyNikhilG

---

## 📜 License

This project is for **educational and learning purposes**.

[1]: https://www.researchgate.net/publication/392538982_Review_of_sentiment_analysis_in_social_media_using_big_data_data_techniques_tools_and_frameworks?utm_source=chatgpt.com "Review of sentiment analysis in social media using big ..."
