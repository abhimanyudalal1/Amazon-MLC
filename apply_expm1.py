import pandas as pd
import numpy as np

# Read the CSV file
print("Reading lgbm_oof_preds.csv...")
df = pd.read_csv('lgbm_oof_preds.csv')

print('Original data:')
print(df.head())
print(f'Original lgbm_oof_preds range: {df["lgbm_oof_preds"].min():.4f} to {df["lgbm_oof_preds"].max():.4f}')

# Apply expm1 to lgbm_oof_preds column
print("\nApplying expm1 transformation...")
df['lgbm_oof_preds'] = np.expm1(df['lgbm_oof_preds'])

print(f'After applying expm1:')
print(df.head())
print(f'Transformed lgbm_oof_preds range: {df["lgbm_oof_preds"].min():.4f} to {df["lgbm_oof_preds"].max():.4f}')

# Save the updated CSV
print("\nSaving updated CSV...")
df.to_csv('lgbm_oof_preds.csv', index=False)
print(f'✅ Successfully applied expm1 and updated lgbm_oof_preds.csv')
print(f'Total rows processed: {len(df)}')
