# Unit Conversion Quick Reference

## 🎯 Quick Summary
All weight units → **grams**
All volume units → **milliliters**
Quantity units → **unchanged**

## 📊 New Columns Created

| Column Name | Description | Example Values |
|------------|-------------|----------------|
| `standardized_value` | Converted numeric value | 453.6, 1000.0, 236.6 |
| `standardized_unit` | Base unit | 'gram', 'ml', 'count' |
| `measurement_category` | Measurement type | 'Weight', 'Volume', 'Quantity' |

## 🔄 Conversion Factors

### Weight to Grams
```
1 gram (g)     = 1.0 g
1 kilogram (kg) = 1000.0 g
1 ounce (oz)   = 28.3495 g
1 pound (lb)   = 453.592 g
```

### Volume to Milliliters
```
1 milliliter (ml) = 1.0 ml
1 liter (L)       = 1000.0 ml
1 fluid ounce     = 29.5735 ml
1 cup             = 236.588 ml
1 pint            = 473.176 ml
1 quart           = 946.353 ml
1 gallon          = 3785.41 ml
```

## 💡 Common Use Cases

### Filter by Weight Range
```python
# Products between 100g and 500g
df[(df['measurement_category'] == 'Weight') & 
   (df['standardized_value'] >= 100) & 
   (df['standardized_value'] <= 500)]
```

### Sort by Volume
```python
# All volume products sorted by size
df[df['measurement_category'] == 'Volume'].sort_values('standardized_value')
```

### Calculate Price Per Unit
```python
# Price per gram for weight items
df['price_per_gram'] = df['price'] / df['standardized_value']
```

### Find Best Value
```python
# Cheapest per gram
df[df['measurement_category'] == 'Weight'].nsmallest(10, 'price_per_gram')
```

### Group Analysis
```python
# Average standardized value by category
df.groupby('measurement_category')['standardized_value'].mean()
```

## ✅ Data Quality Checks

The conversion automatically checks for:
- ❌ Negative values
- ⚠️  Zero values
- ℹ️  Missing values
- 🔍 Outliers (extremely high values)

## 🚀 Quick Start

Run these cells in order:
1. ✓ Load and clean data (existing cells)
2. ✓ Unit conversion function (new cell 1)
3. ✓ Apply conversions (new cell 2)
4. ✓ View results (new cell 3)

## 📈 Example Results

**Before Conversion:**
```
Item: Coffee Beans
Value: 1
Unit: pound
Price: $12.99
```

**After Conversion:**
```
Item: Coffee Beans
Standardized Value: 453.592
Standardized Unit: gram
Measurement Category: Weight
Price per Gram: $0.0286
```

## 💾 Save Results
```python
df.to_csv('train_cleaned_with_standardized_units.csv', index=False)
```

## 📌 Column Reference

**Original columns used:**
- `catalog_value` - Original numeric value
- `catalog_unit_clean` - Cleaned unit name

**New columns created:**
- `standardized_value` - Converted value in base unit
- `standardized_unit` - Base unit (gram/ml/original)
- `measurement_category` - Type (Weight/Volume/Quantity/Other)

**Optional columns:**
- `price_per_gram` - Price per gram for weight items
- `price_per_ml` - Price per ml for volume items
- `price_per_unit` - Price per unit for quantity items

---

**Status**: ✅ Ready to use
**All conversions**: Fully automated
**Data validation**: Included
