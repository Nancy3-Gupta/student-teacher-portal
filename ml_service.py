from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np

def predict_final_score(month_indices, scores):
    # month_indices: [1, 2, 3, 4...] (The months recorded so far)
    # scores: [70, 72, 75, 78...] (The marks achieved)
    
    X = np.array(month_indices).reshape(-1, 1)
    y = np.array(scores)

    # 1. Create a curve (degree 2) to fit the learning trend
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)

    # 2. Train the model
    model = LinearRegression()
    model.fit(X_poly, y)

    # 3. Predict for the 10th month (Final Exam)
    final_month = np.array([[10]]) 
    final_month_poly = poly.transform(final_month)
    prediction = model.predict(final_month_poly)

    return round(float(prediction[0]), 2)