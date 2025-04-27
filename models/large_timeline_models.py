import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier , GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import RidgeClassifier
from lightgbm import LGBMClassifier
from sklearn.naive_bayes import GaussianNB
import time

train_df = pd.read_csv("ranked_matches_at_15_large.csv")
test_df = pd.read_csv("ranked_matches_at_15_test.csv")

X_train = train_df.drop("Winning team", axis=1)
y_train = train_df["Winning team"]

X_test = test_df.drop("Winning team", axis=1)
y_test = test_df["Winning team"]

start = time.time()

models = {
    "Support Vector Machine": SVC(),
    "Random Forest": RandomForestClassifier(),
    "kNearestNeighbours": KNeighborsClassifier(),
    "decisionTree": DecisionTreeClassifier(),
    "Gradient Boosting": GradientBoostingClassifier(),    
    "AdaBoost": AdaBoostClassifier(),
    "LightGBM": LGBMClassifier(),
    "Ridge Classifier": RidgeClassifier(),
}

for name, model in models.items():
    start_timestamp = time.time()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    end_timestamp = time.time()
    
    print(f"Model: {name}")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred, digits=3))
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print(f"Training and prediction took {end_timestamp - start_timestamp:.3f} seconds")
    print("-" * 50)


