import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from joblib import dump

# Load the dataset
df = pd.read_csv('/Users/yeduruabhiram/Desktop/nxtwave buildthon/Crop_recommendation.csv')

# Prepare features and target
X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = df['label']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Save the model
dump(rf_model, '/Users/yeduruabhiram/Desktop/nxtwave buildthon/AgriMindAI/backend/models/crop_rf_model.joblib')