import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Sample data (replace with actual data)
data = {
    "emissions": [5.779],  # Emissions in g CO2
    "pollution": [46.629629629629626],    # Pollution level (could be some air quality measure)
    "distance": [1.5673],       # Distance in kilometers
    "high_aqi_area": [0],       # High AQI Area (0 = No, 1 = Yes)
    "score": [0.797571848237334]                # Route score (0 = best, 2 = worst)
}

# Convert data into a pandas DataFrame
df = pd.DataFrame(data)

# Feature matrix (X) and target vector (y)
X = df[["emissions", "pollution", "distance", "high_aqi_area"]].values
y = df["score"].values

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Predict route scores using the trained model
y_pred = model.predict(X_test)

# Evaluate the model's performance using Mean Squared Error
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# Output the learned model coefficients (weights)
print("Learned coefficients (weights):")
print(f"Emissions weight: {model.coef_[0]}")
print(f"Pollution weight: {model.coef_[1]}")
print(f"Distance weight: {model.coef_[2]}")
print(f"High AQI Area weight: {model.coef_[3]}")
print(f"Intercept: {model.intercept_}")

# Print the final linear regression equation
equation = f"Score = {model.intercept_:.2f} + ({model.coef_[0]:.2f} * Emissions) + ({model.coef_[1]:.2f} * Pollution) + ({model.coef_[2]:.2f} * Distance) + ({model.coef_[3]:.2f} * High AQI Area)"
print("\nFinal Linear Regression Equation:")
print(equation)

# --- PREDICT NEW ROUTE ---

# Predict route score for a new route (with given features)
new_route = np.array([[110, 90, 16, 1]])  # Example: Emissions = 110, Pollution = 90, Distance = 16, High AQI Area = Yes (1)
predicted_score = model.predict(new_route)
predicted_score_clamped = np.clip(predicted_score, 0, 2)  # Clamping the score to the range [0, 2]

# Map the clamped score (0-2) to AQI range (0-500)
# Linear Transformation: 
# score = 0 -> AQI = 0, score = 2 -> AQI = 500
# Transformation formula: aqi = (score / 2) * 500
predicted_aqi = (predicted_score_clamped[0] / 2) * 500

# Display the predicted AQI for the new route
print(f"Predicted route score (scaled AQI) for new route: {predicted_aqi}")

# --- ADDITIONAL PLOTTING BELOW ---

# 1. Plot Actual vs Predicted scores
plt.figure(figsize=(8,6))
plt.scatter(y_test, y_pred, color='blue', edgecolor='k')
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--')  # perfect prediction line
plt.xlabel('Actual Score')
plt.ylabel('Predicted Score')
plt.title('Actual vs Predicted Route Scores')
plt.grid(True)
plt.show()

# 2. Plot Feature Importances (Weights)
features = ["Emissions", "Pollution", "Distance", "High AQI Area"]
weights = model.coef_

plt.figure(figsize=(8,6))
plt.bar(features, weights, color='teal', edgecolor='k')
plt.xlabel('Features')
plt.ylabel('Weight')
plt.title('Feature Importance Based on Learned Weights')
plt.grid(axis='y')
plt.show()

# 3. Plot Emissions vs Score (only varying emissions, fixing other features)

# Set fixed values for other features
pollution_fixed = df["pollution"].mean()  # average pollution
distance_fixed = df["distance"].mean()    # average distance
high_aqi_fixed = 0  # Assume not passing through high AQI

# Create emissions range
emissions_range = np.linspace(df["emissions"].min(), df["emissions"].max(), 100)

# Build full X input for prediction
X_emissions_varied = np.column_stack([
    emissions_range, 
    np.full_like(emissions_range, pollution_fixed),
    np.full_like(emissions_range, distance_fixed),
    np.full_like(emissions_range, high_aqi_fixed)
])

# Predict
y_emissions_pred = model.predict(X_emissions_varied)

# Plot emissions vs predicted score
plt.figure(figsize=(8,6))
plt.scatter(df["emissions"], df["score"], color='blue', label='Original Data Points')
plt.plot(emissions_range, y_emissions_pred, color='red', label='Regression Line (Others Fixed)')
plt.xlabel('Emissions (g CO2)')
plt.ylabel('Route Score')
plt.title('Emissions vs Route Score with Regression Line')
plt.legend()
plt.grid(True)
plt.show()
