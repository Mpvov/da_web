import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import os
import pickle
import re

# Directory to save all country-specific models
MODEL_DIR = "app/trained_models"
os.makedirs(MODEL_DIR, exist_ok=True)

class OutbreakPredictor:
    def __init__(self):
        # Cache to store loaded models in memory so we don't read from disk every request
        self.models_cache = {}

    def _get_model_filename(self, country_name):
        """Sanitizes country name to create a safe filename."""
        # e.g. "S. Korea" -> "S__Korea", "Vietnam" -> "Vietnam"
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', country_name)
        return os.path.join(MODEL_DIR, f"model_{safe_name}.pkl")

    def get_model(self, country_name):
        """Lazy loads a model for a specific country."""
        # 1. Check cache first
        if country_name in self.models_cache:
            return self.models_cache[country_name]
        
        # 2. Check disk
        filepath = self._get_model_filename(country_name)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    model = pickle.load(f)
                    self.models_cache[country_name] = model
                    return model
            except Exception as e:
                print(f"Error loading model for {country_name}: {e}")
                return None
        
        return None

    def predict(self, country, current, lag_7, lag_14):
        """
        Predicts using the SPECIFIC model for the requested country.
        """
        model = self.get_model(country)
        
        # 1. Feature Engineering
        growth_7d = current - lag_7
        growth_14d = current - lag_14
        feature_names = ['avg_new_cases_7d', 'lag_7d', 'lag_14d', 'growth_rate_7d', 'growth_rate_14d']
        features = pd.DataFrame([[current, lag_7, lag_14, growth_7d, growth_14d]], columns=feature_names)

        # 2. Prediction
        if model:
            # === REAL AI PREDICTION ===
            prediction = model.predict(features)[0]
            proba = model.predict_proba(features)[0][1]
            used_logic = f"Mô hình Random Forest đã được huấn luyện theo ({country})"
        else:
            # === DEMO/FALLBACK LOGIC ===
            # Used if country has no data or hasn't been trained yet
            ratio = current / lag_14 if lag_14 > 0 else 0
            if ratio > 1.2: 
                prediction = 1
                proba = 0.85 + (ratio * 0.05)
            else:
                prediction = 0
                proba = 0.10
            used_logic = "Phương pháp Heuristic (Demo)"
        
        # 3. Output Formatting
        label = "Có khả năng bùng phát" if prediction == 1 else "Bình thường"
        
        if prediction == 1:
            explanation = (
                f"[{used_logic}] Dự đoán có khả năng bùng dịch dựa trên xu hướng. "
                f"Số ca mắc có thể tăng {growth_14d:.1f} trong vòng 14 ngày tới."
            )
        else:
            explanation = (
                f"[{used_logic}] Dự đoán không có khả năng bùng dịch (ổn định). "
                f"Số ca mắc có thể tăng {growth_14d:.1f} trong vòng 14 ngày tới."
            )

        return {
            "prediction_class": int(prediction),
            "prediction_label": label,
            "probability": f"{min(proba * 100, 99.9):.1f}%",
            "explanation": explanation
        }

    def train_model_from_db(self, connection_string):
        """
        Trains a separate model for EVERY country found in the database.
        """
        from pymongo import MongoClient
        
        print("Connecting to MongoDB...")
        try:
            client = MongoClient(connection_string)
            db = client["covid_db"]
            col = db["countries"]
            
            # Get list of all distinct countries
            all_countries = col.distinct("country")
            print(f"Found {len(all_countries)} countries. Starting batch training...")

            for country_name in all_countries:
                self._train_single_country(col, country_name)

            print(f"--- All training complete. Models saved in {MODEL_DIR} ---")
            
        except Exception as e:
            print(f"Global training failed: {e}")

    def _train_single_country(self, collection, country_name):
        """Helper to train and save one country."""
        try:
            doc = collection.find_one({'country': country_name})
            if not doc: return

            # Data Prep
            data = doc.get('timeline', {}).get('cases', {})
            if len(data) < 50: # Skip if not enough data
                print(f"Skipping {country_name} (Not enough data)")
                return

            df = pd.DataFrame.from_dict(data, orient='index', columns=['total_cases'])
            df.index = pd.to_datetime(df.index, format='mixed')
            df = df.sort_index()
            
            df['new_cases'] = df['total_cases'].diff().clip(lower=0).fillna(0)
            df['avg_new_cases_7d'] = df['new_cases'].rolling(window=7).mean()
            df = df.dropna()

            # Labeling
            FUTURE = 14
            THRESHOLD = 1.5
            df['future_rate'] = df['avg_new_cases_7d'].shift(-FUTURE)
            df['y'] = np.where(df['future_rate'] >= (df['avg_new_cases_7d'] * THRESHOLD), 1, 0)

            # Features
            df['lag_7d'] = df['avg_new_cases_7d'].shift(7)
            df['lag_14d'] = df['avg_new_cases_7d'].shift(14)
            df['growth_rate_7d'] = df['avg_new_cases_7d'] - df['lag_7d']
            df['growth_rate_14d'] = df['avg_new_cases_7d'] - df['lag_14d']
            
            df_final = df.dropna()
            
            if df_final.empty: return

            features = ['avg_new_cases_7d', 'lag_7d', 'lag_14d', 'growth_rate_7d', 'growth_rate_14d']
            X = df_final[features]
            y = df_final['y']

            # Check if we have both classes (0 and 1) to train effectively
            if len(y.unique()) < 2:
                # If a country NEVER had an outbreak (or ALWAYS had one), we can't train a classifier
                # We skip saving a model, so it falls back to Demo Logic, which is safer.
                print(f"Skipping {country_name} (Only one class found: {y.unique()})")
                return

            # Train
            model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
            model.fit(X, y)
            
            # Save
            filepath = self._get_model_filename(country_name)
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
            
            print(f"Saved: {country_name}")

        except Exception as e:
            print(f"Failed to train {country_name}: {e}")

# Singleton
predictor = OutbreakPredictor()