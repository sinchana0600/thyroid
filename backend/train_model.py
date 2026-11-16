import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

print("Training Thyroid Detection Model...")
print("=" * 50)

# Check if data.csv exists
if not os.path.exists('data.csv'):
    print("Warning: data.csv not found. Creating sample dataset...")
    
    # Create sample thyroid dataset
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'TSH': np.random.uniform(0.1, 10.0, n_samples),
        'T3': np.random.uniform(0.5, 3.0, n_samples),
        'T4': np.random.uniform(4.0, 12.0, n_samples),
        'age': np.random.randint(18, 80, n_samples),
        'gender': np.random.choice(['M', 'F'], n_samples)
    }
    
    # Create target based on TSH levels
    diagnosis = []
    for tsh in data['TSH']:
        if tsh < 0.4:
            diagnosis.append('hyperthyroid')
        elif tsh <= 4.0:
            diagnosis.append('normal')
        else:
            diagnosis.append('hypothyroid')
    data['diagnosis'] = diagnosis
    
    df = pd.DataFrame(data)
    df.to_csv('data.csv', index=False)
    print("✓ Sample dataset created")
else:
    df = pd.read_csv('data.csv')
    print(f"✓ Loaded dataset with {len(df)} records")

# Prepare features
print("\nPreparing features...")

# Handle missing values
df['T3'] = df['T3'].fillna(0)
df['T4'] = df['T4'].fillna(0)

# Encode gender if present
if 'gender' in df.columns:
    le_gender = LabelEncoder()
    df['gender_encoded'] = le_gender.fit_transform(df['gender'])
    feature_columns = ['TSH', 'T3', 'T4', 'age', 'gender_encoded']
else:
    feature_columns = ['TSH', 'T3', 'T4']

# Prepare X and y
X = df[feature_columns]
y = df['diagnosis'] if 'diagnosis' in df.columns else df.iloc[:, -1]

# Encode target
le_target = LabelEncoder()
y_encoded = le_target.fit_transform(y)

print(f"✓ Features: {feature_columns}")
print(f"✓ Classes: {list(le_target.classes_)}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nTraining model...")

# Train Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
model.fit(X_train_scaled, y_train)

# Evaluate
train_score = model.score(X_train_scaled, y_train)
test_score = model.score(X_test_scaled, y_test)

print(f"✓ Training accuracy: {train_score:.2%}")
print(f"✓ Testing accuracy: {test_score:.2%}")

# Save model and preprocessors
print("\nSaving model...")
os.makedirs('models', exist_ok=True)

with open('models/thyroid_model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

with open('models/label_encoder.pkl', 'wb') as f:
    pickle.dump(le_target, f)

print("✓ Model saved to models/thyroid_model.pkl")
print("✓ Scaler saved to models/scaler.pkl")
print("✓ Label encoder saved to models/label_encoder.pkl")

print("\n" + "=" * 50)
print("Model training complete!")
print("\nModel is ready to use for predictions.")
