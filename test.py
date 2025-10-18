import os
import random
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import lightgbm as lgb
import pickle
import re

def predictor(sample_id, catalog_content, image_link):
    '''
    Call your model/approach here
    
    Parameters:
    - sample_id: Unique identifier for the sample
    - catalog_content: Text containing product title and description
    - image_link: URL to product image
    
    Returns:
    - price: Predicted price as a float
    '''
    # Load model and vectorizer
    try:
        model = lgb.Booster(model_file='price_prediction_model.txt')
        with open('tfidf_vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
    except:
        return round(random.uniform(5.0, 500.0), 2)
    
    def parse_catalog_content(content):
        if pd.isna(content) or content == '':
            return {'item_name': '', 'catalog_value': np.nan, 'catalog_unit': ''}
        parts = content.split('item_name:')
        if len(parts) < 2:
            return {'item_name': '', 'catalog_value': np.nan, 'catalog_unit': ''}
        item_section = parts[1].strip()
        item_name = item_section.split('|')[0].strip()
        value_pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+(?:\s+[a-zA-Z]+)*)'
        matches = re.findall(value_pattern, content)
        if matches:
            value, unit = matches[0]
            return {'item_name': item_name, 'catalog_value': float(value), 'catalog_unit': unit.strip()}
        else:
            return {'item_name': item_name, 'catalog_value': np.nan, 'catalog_unit': ''}
    
    def standardize_unit(unit, value):
        if pd.isna(value) or unit == '':
            return value, ''
        unit_lower = unit.lower().strip()
        weight_conversions = {'oz': 28.3495, 'ounce': 28.3495, 'ounces': 28.3495, 'lb': 453.592, 'lbs': 453.592, 'pound': 453.592, 'pounds': 453.592, 'kg': 1000, 'kilogram': 1000, 'kilograms': 1000, 'g': 1, 'gram': 1, 'grams': 1, 'mg': 0.001, 'milligram': 0.001, 'milligrams': 0.001}
        volume_conversions = {'fl oz': 29.5735, 'fluid ounce': 29.5735, 'fluid ounces': 29.5735, 'cup': 236.588, 'cups': 236.588, 'pint': 473.176, 'pints': 473.176, 'quart': 946.353, 'quarts': 946.353, 'gallon': 3785.41, 'gallons': 3785.41, 'l': 1000, 'liter': 1000, 'liters': 1000, 'litre': 1000, 'litres': 1000, 'ml': 1, 'milliliter': 1, 'milliliters': 1, 'millilitre': 1, 'millilitres': 1}
        if unit_lower in weight_conversions:
            return value * weight_conversions[unit_lower], 'g'
        elif unit_lower in volume_conversions:
            return value * volume_conversions[unit_lower], 'ml'
        else:
            return value, unit_lower
    
    parsed = parse_catalog_content(catalog_content)
    item_name = parsed['item_name']
    catalog_value = parsed['catalog_value']
    catalog_unit = parsed['catalog_unit']
    standardized_value, standardized_unit = standardize_unit(catalog_unit, catalog_value)
    
    # Create text features - combine item_name and catalog_content like in training
    text_content = f"{catalog_content}".strip()  # Use full catalog_content for text features
    if text_content == '':
        text_content = 'unknown product'
    
    text_features = vectorizer.transform([text_content])
    text_features_dense = text_features.toarray()
    
    # Create features to match training (without price-per-unit circular logic)
    # Use only: text_features + log_standardized_value + measurement_type indicators
    
    # Calculate log_standardized_value (like in training)
    log_standardized_value = np.log1p(standardized_value) if not pd.isna(standardized_value) and standardized_value > 0 else 0
    
    # Create measurement type indicators (like categorical encoding)
    measurement_type = 'weight' if standardized_unit == 'g' else 'volume' if standardized_unit == 'ml' else 'other'
    is_weight = 1 if measurement_type == 'weight' else 0
    is_volume = 1 if measurement_type == 'volume' else 0
    is_other = 1 if measurement_type == 'other' else 0
    
    # Build feature vector
    features = []
    features.extend(text_features_dense[0])  # Text features (TF-IDF)
    features.append(log_standardized_value)  # Log of standardized value
    features.append(is_weight)               # Weight indicator
    features.append(is_volume)               # Volume indicator  
    features.append(is_other)                # Other measurement indicator
    
    features = np.array(features).reshape(1, -1)
    
    # Make prediction
    try:
        prediction = model.predict(features)
        # Convert to numpy array and extract scalar
        pred_array = np.asarray(prediction).flatten()
        log_price_pred = pred_array[0]
        
        # Convert from log scale back to actual price
        price_pred = np.expm1(log_price_pred)
        
        # Ensure reasonable price bounds
        price_pred = max(1.0, min(price_pred, 1000.0))
        
        return round(price_pred, 2)
    except Exception as e:
        # Fallback to random if prediction fails
        print(f"Prediction error: {e}")
        return round(random.uniform(10.0, 200.0), 2)

if __name__ == "__main__":
    # DATASET_FOLDER = ''
    
    # Read test data
    test = pd.read_csv(os.path.join( 'test.csv'))
    
    # Apply predictor function to each row
    test['price'] = test.apply(
        lambda row: predictor(row['sample_id'], row['catalog_content'], row['image_link']), 
        axis=1
    )
    
    # Select only required columns for output
    output_df = test[['sample_id', 'price']]
    
    # Save predictions
    output_filename = os.path.join( 'test_out1.csv')
    output_df.to_csv(output_filename, index=False)
    
    print(f"Predictions saved to {output_filename}")
    print(f"Total predictions: {len(output_df)}")
    print(f"Sample predictions:\n{output_df.head()}")