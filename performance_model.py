import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

def train_model(csv_path):
    df = pd.read_csv(csv_path)
    
    # Convert Yes/No to 1/0 for binary columns
    binary_columns = ["physical_activity", "academic_goal"]
    for col in binary_columns:
        df[col] = df[col].map({"Yes": 1, "No": 0})

    # Prepare features and target
    X = df.drop("Performance_Label", axis=1)
    y = df["Performance_Label"]

    # Encode target variable
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    # Train model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Evaluate
    accuracy = model.score(X_test, y_test)
    print(f"✅ Model Accuracy: {accuracy:.2f}")

    return model, label_encoder

def predict_performance(model, label_encoder, input_data):
    # Convert input to DataFrame
    input_df = pd.DataFrame([input_data])
    
    # Predict
    prediction_encoded = model.predict(input_df)[0]
    prediction_label = label_encoder.inverse_transform([prediction_encoded])[0]
    return prediction_label