# Synthetic Sentiment and Intent Classification using XGBoost

## 📌 Project Overview
![App Demo]("C:\Users\dell\Downloads\demo 1.gif"
)

This project focuses on text classification using Natural Language Processing (NLP) and Machine Learning. It uses text data to classify messages into their respective categories. The project applies text preprocessing, TF-IDF vectorization, and an XGBoost classifier to train a model and predict labels for new text inputs.

## 📂 Dataset

- **Dataset Name:** Synthetic Sentiment and Intent Data
- **Source:** [Kaggle Dataset](https://www.kaggle.com/datasets/ahsanneural/synthetic-sentiment-and-intent-data)
- **Dataset Size:** 5,000 records
- **Input Feature:** Text
- **Target Feature:** Label

## 🛠️ Technologies Used

- Python
- Pandas and NumPy
- NLTK
- Scikit-learn
- XGBoost
- Matplotlib and Seaborn
- Joblib
- KaggleHub

## 🔄 Project Workflow

1. Download and load the dataset.
2. Perform data exploration and statistical analysis.
3. Check for missing values and duplicate records.
4. Visualize the distribution of target labels.
5. Clean text by removing URLs, special characters, and unnecessary spaces.
6. Convert text to lowercase.
7. Remove stopwords and apply lemmatization.
8. Encode target labels using LabelEncoder.
9. Convert text into numerical features using TF-IDF Vectorization.
10. Split the dataset into training and testing sets.
11. Train the XGBoost classification model.
12. Evaluate the model using classification metrics.
13. Save the trained model and preprocessing objects.
14. Load the saved files to make predictions on new text.

## 🤖 Machine Learning Model

The project uses the **XGBoost Classifier**, a gradient-boosting algorithm that combines multiple decision trees to perform classification.

TF-IDF (Term Frequency–Inverse Document Frequency) converts text into numerical features that can be used by the machine learning model.

## 📊 Model Evaluation

The model is evaluated using the following metrics:

- Accuracy Score
- Precision
- Recall
- F1-Score
- Confusion Matrix

These metrics help measure the model's classification performance. The actual results can be obtained by running the notebook.

## 📦 Installation

Install the required Python libraries:

```bash
pip install pandas numpy nltk scikit-learn xgboost matplotlib seaborn joblib kagglehub
```

## ▶️ How to Run

1. Clone this repository:

   ```bash
   git clone YOUR_GITHUB_REPOSITORY_URL
   ```

2. Open the project folder.

3. Install the required libraries.

4. Open `synthetic_sentiment_and_intent_data.ipynb` in Jupyter Notebook or Google Colab.

5. Download the dataset and execute the notebook cells in order.

6. Train the model and evaluate its performance.

7. Run the prediction section to classify new text messages.

## 💾 Saved Model Files

The notebook saves the following files in the `xgboost_saved_model/` directory:

- `xgb_model.pkl` — Trained XGBoost classifier.
- `tfidf_vectorizer.pkl` — Fitted TF-IDF vectorizer.
- `label_encoder.pkl` — Label encoder for the target classes.

These files are required to reuse the trained model without training it again.

## 💡 Applications

- Text classification
- Sentiment analysis
- Intent detection
- Customer feedback analysis
- Automated text categorization

## 🚀 Future Improvements

- Test the model on real-world text data.
- Compare XGBoost with Logistic Regression, Naive Bayes, and SVM.
- Improve text preprocessing and feature extraction.
- Deploy the trained model using Streamlit or Flask.
- Build a simple web interface for real-time text predictions.

## 📝 Conclusion

This project demonstrates the use of NLP and machine learning for text classification. By combining text preprocessing, TF-IDF vectorization, and XGBoost, the system learns patterns from text data and predicts the corresponding class. It also demonstrates model evaluation and saving trained components for future predictions.

---

**Project Type:** Natural Language Processing (NLP) / Machine Learning  
**Language:** Python  
**Model:** XGBoost Classifier
