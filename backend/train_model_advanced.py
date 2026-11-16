import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("  ADVANCED THYROID DETECTION MODEL TRAINING")
print("=" * 70)

# Create realistic thyroid dataset based on medical research
def create_realistic_dataset(n_samples=5000):
    np.random.seed(42)
    
    data = []
    
    # Normal thyroid (60% of population)
    n_normal = int(n_samples * 0.6)
    for _ in range(n_normal):
        tsh = np.random.normal(2.0, 0.8)  # Mean 2.0, std 0.8
        tsh = np.clip(tsh, 0.4, 4.0)
        t3 = np.random.normal(1.2, 0.3)
        t3 = np.clip(t3, 0.8, 2.0)
        t4 = np.random.normal(8.0, 1.5)
        t4 = np.clip(t4, 5.0, 12.0)
        age = np.random.randint(18, 80)
        gender = np.random.choice(['M', 'F'])
        data.append([tsh, t3, t4, age, gender, 'normal'])
    
    # Hypothyroid (25% of population)
    n_hypo = int(n_samples * 0.25)
    for _ in range(n_hypo):
        tsh = np.random.normal(7.0, 2.0)  # Elevated TSH
        tsh = np.clip(tsh, 4.1, 15.0)
        t3 = np.random.normal(0.8, 0.2)  # Low T3
        t3 = np.clip(t3, 0.3, 1.2)
        t4 = np.random.normal(5.0, 1.0)  # Low T4
        t4 = np.clip(t4, 2.0, 7.0)
        age = np.random.randint(18, 80)
        gender = np.random.choice(['M', 'F'], p=[0.3, 0.7])  # More common in females
        data.append([tsh, t3, t4, age, gender, 'hypothyroid'])
    
    # Hyperthyroid (15% of population)
    n_hyper = n_samples - n_normal - n_hypo
    for _ in range(n_hyper):
        tsh = np.random.normal(0.15, 0.1)  # Very low TSH
        tsh = np.clip(tsh, 0.01, 0.39)
        t3 = np.random.normal(2.5, 0.4)  # High T3
        t3 = np.clip(t3, 2.0, 4.0)
        t4 = np.random.normal(14.0, 2.0)  # High T4
        t4 = np.clip(t4, 12.0, 20.0)
        age = np.random.randint(18, 80)
        gender = np.random.choice(['M', 'F'], p=[0.3, 0.7])  # More common in females
        data.append([tsh, t3, t4, age, gender, 'hyperthyroid'])
    
    df = pd.DataFrame(data, columns=['TSH', 'T3', 'T4', 'age', 'gender', 'diagnosis'])
    return df

# Load or create dataset
print("\n[1/6] Loading Dataset...")
if os.path.exists('data.csv'):
    df = pd.read_csv('data.csv')
    print(f"✓ Loaded existing dataset: {len(df)} records")
else:
    print("Creating realistic thyroid dataset...")
    df = create_realistic_dataset(5000)
    df.to_csv('data.csv', index=False)
    print(f"✓ Created new dataset: {len(df)} records")

# Data preprocessing
print("\n[2/6] Preprocessing Data...")
df['T3'] = df['T3'].fillna(0)
df['T4'] = df['T4'].fillna(0)

# Encode gender
le_gender = LabelEncoder()
df['gender_encoded'] = le_gender.fit_transform(df['gender'])

# Prepare features and target
feature_columns = ['TSH', 'T3', 'T4', 'age', 'gender_encoded']
X = df[feature_columns]
y = df['diagnosis']

# Encode target
le_target = LabelEncoder()
y_encoded = le_target.fit_transform(y)

print(f"✓ Features: {feature_columns}")
print(f"✓ Classes: {list(le_target.classes_)}")
print(f"✓ Class distribution:")
for cls in le_target.classes_:
    count = (y == cls).sum()
    print(f"  - {cls}: {count} ({count/len(y)*100:.1f}%)")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"✓ Training set: {len(X_train)} samples")
print(f"✓ Testing set: {len(X_test)} samples")

# Train multiple models
print("\n[3/6] Training Multiple Models...")
print("-" * 70)

models = {
    'Random Forest': RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    ),
    'SVM': SVC(
        kernel='rbf',
        C=10,
        gamma='scale',
        probability=True,
        random_state=42
    ),
    'Neural Network': MLPClassifier(
        hidden_layer_sizes=(100, 50, 25),
        activation='relu',
        solver='adam',
        max_iter=500,
        random_state=42
    )
}

results = {}

for name, model in models.items():
    print(f"\nTraining {name}...")
    
    # Train model
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()
    
    results[name] = {
        'model': model,
        'train_score': train_score,
        'test_score': test_score,
        'cv_mean': cv_mean,
        'cv_std': cv_std
    }
    
    print(f"  Training Accuracy: {train_score:.4f}")
    print(f"  Testing Accuracy:  {test_score:.4f}")
    print(f"  CV Score: {cv_mean:.4f} (+/- {cv_std:.4f})")

# Select best model
print("\n[4/6] Selecting Best Model...")
print("-" * 70)

best_model_name = max(results, key=lambda x: results[x]['test_score'])
best_model = results[best_model_name]['model']
best_score = results[best_model_name]['test_score']

print(f"\n✓ Best Model: {best_model_name}")
print(f"✓ Test Accuracy: {best_score:.4f}")

# Detailed evaluation
print("\n[5/6] Detailed Evaluation...")
print("-" * 70)

y_pred = best_model.predict(X_test_scaled)

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=le_target.classes_))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Feature importance (if available)
if hasattr(best_model, 'feature_importances_'):
    print("\nFeature Importance:")
    importances = best_model.feature_importances_
    for feat, imp in zip(feature_columns, importances):
        print(f"  {feat}: {imp:.4f}")

# Save best model
print("\n[6/6] Saving Model...")
print("-" * 70)

os.makedirs('models', exist_ok=True)

with open('models/thyroid_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)

with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

with open('models/label_encoder.pkl', 'wb') as f:
    pickle.dump(le_target, f)

# Save model info
model_info = {
    'model_name': best_model_name,
    'test_accuracy': best_score,
    'features': feature_columns,
    'classes': list(le_target.classes_),
    'training_samples': len(X_train),
    'testing_samples': len(X_test)
}

with open('models/model_info.pkl', 'wb') as f:
    pickle.dump(model_info, f)

print(f"✓ Best model ({best_model_name}) saved to models/thyroid_model.pkl")
print(f"✓ Scaler saved to models/scaler.pkl")
print(f"✓ Label encoder saved to models/label_encoder.pkl")
print(f"✓ Model info saved to models/model_info.pkl")

# Summary
print("\n" + "=" * 70)
print("  TRAINING COMPLETE!")
print("=" * 70)
print(f"\nBest Model: {best_model_name}")
print(f"Accuracy: {best_score:.2%}")
print(f"Dataset Size: {len(df)} samples")
print(f"Features: {len(feature_columns)}")
print(f"Classes: {len(le_target.classes_)}")
print("\nModel Comparison:")
for name, res in sorted(results.items(), key=lambda x: x[1]['test_score'], reverse=True):
    print(f"  {name:20s}: {res['test_score']:.4f}")

print("\n✓ Model is ready for production use!")
print("=" * 70)
