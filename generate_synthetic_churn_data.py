"""
CUSTOMER CHURN DATA GENERATOR - INDUSTRY LEVEL
Generates realistic synthetic telecom customer data (7000+ customers)
With realistic churn patterns and business logic
"""

import pandas as pd
import numpy as np
from datetime import datetime
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

print("=" * 70)
print("CUSTOMER CHURN SYNTHETIC DATA GENERATOR - INDUSTRY LEVEL")
print("=" * 70)

# ============================================================================
# CONFIGURATION
# ============================================================================
NUM_CUSTOMERS = 7000
CHURN_RATE = 0.27  # 27% churn (realistic for telecom)
CURRENT_DATE = datetime(2024, 4, 27)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_tenure():
    """Generate tenure in months (0-72 months) with realistic distribution"""
    # More customers churn in first 6 months, tail off over time
    return np.random.exponential(scale=20) + 1
    
def calculate_churn_probability(tenure, contract, monthly_charges, internet_service):
    """Calculate probability of churn based on customer characteristics"""
    base_churn = 0.27
    
    # Tenure effect: newer customers churn more
    if tenure < 6:
        base_churn += 0.20  # +20% for new customers
    elif tenure < 12:
        base_churn += 0.10  # +10% for first year
    elif tenure > 48:
        base_churn -= 0.10  # -10% for loyal customers
    
    # Contract effect: month-to-month is risky
    if contract == "Month-to-month":
        base_churn += 0.15
    elif contract == "One year":
        base_churn -= 0.05
    elif contract == "Two year":
        base_churn -= 0.12
    
    # Monthly charges effect: expensive = more churn
    if monthly_charges > 100:
        base_churn += 0.08
    
    # Internet service effect: Fiber optic = less stable
    if internet_service == "Fiber optic":
        base_churn += 0.05
    
    return min(max(base_churn, 0.01), 0.99)

# ============================================================================
# GENERATE DATA
# ============================================================================

print("\n📊 Generating synthetic customer data...")

data = {
    'customerID': [f'CUST_{i+1:06d}' for i in range(NUM_CUSTOMERS)],
    'gender': np.random.choice(['Male', 'Female'], NUM_CUSTOMERS),
    'SeniorCitizen': np.random.binomial(1, 0.16, NUM_CUSTOMERS),  # 16% seniors
    'Partner': np.random.choice(['Yes', 'No'], NUM_CUSTOMERS, p=[0.48, 0.52]),
    'Dependents': np.random.choice(['Yes', 'No'], NUM_CUSTOMERS, p=[0.30, 0.70]),
}

df = pd.DataFrame(data)

# Generate tenure (months with company)
df['tenure'] = [int(generate_tenure()) for _ in range(NUM_CUSTOMERS)]
df['tenure'] = np.clip(df['tenure'], 1, 72)  # Cap at 72 months (6 years)

# Generate contract types (weighted towards month-to-month)
df['Contract'] = np.random.choice(
    ['Month-to-month', 'One year', 'Two year'],
    NUM_CUSTOMERS,
    p=[0.55, 0.25, 0.20]
)

# Generate internet service (most have DSL/Fiber)
df['InternetService'] = np.random.choice(
    ['DSL', 'Fiber optic', 'No'],
    NUM_CUSTOMERS,
    p=[0.40, 0.35, 0.25]
)

# Generate phone service
df['PhoneService'] = np.random.choice(['Yes', 'No'], NUM_CUSTOMERS, p=[0.90, 0.10])

# Generate multiple lines
df['MultipleLines'] = df.apply(
    lambda row: np.random.choice(['Yes', 'No', 'No phone service']) 
    if row['PhoneService'] == 'Yes' 
    else 'No phone service',
    axis=1
)

# Generate online services (conditional on internet)
def has_service(internet_service):
    if internet_service == 'No':
        return 'No internet service'
    return np.random.choice(['Yes', 'No'], p=[0.35, 0.65])

df['OnlineSecurity'] = df['InternetService'].apply(has_service)
df['OnlineBackup'] = df['InternetService'].apply(has_service)
df['DeviceProtection'] = df['InternetService'].apply(has_service)
df['TechSupport'] = df['InternetService'].apply(has_service)
df['StreamingTV'] = df['InternetService'].apply(has_service)
df['StreamingMovies'] = df['InternetService'].apply(has_service)

# Generate billing information
df['PaperlessBilling'] = np.random.choice(['Yes', 'No'], NUM_CUSTOMERS, p=[0.75, 0.25])
df['PaymentMethod'] = np.random.choice(
    ['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'],
    NUM_CUSTOMERS,
    p=[0.30, 0.22, 0.25, 0.23]
)

# Generate monthly charges (realistic distribution)
def generate_charges(row):
    base = 20
    
    # Internet service charges
    if row['InternetService'] == 'DSL':
        base += np.random.normal(55, 10)
    elif row['InternetService'] == 'Fiber optic':
        base += np.random.normal(75, 10)
    
    # Phone service
    if row['PhoneService'] == 'Yes':
        base += 20
    
    # Add-on services
    addons = sum([
        15 if row['OnlineSecurity'] == 'Yes' else 0,
        10 if row['OnlineBackup'] == 'Yes' else 0,
        15 if row['DeviceProtection'] == 'Yes' else 0,
        20 if row['TechSupport'] == 'Yes' else 0,
        15 if row['StreamingTV'] == 'Yes' else 0,
        15 if row['StreamingMovies'] == 'Yes' else 0,
    ])
    
    total = base + addons + np.random.normal(0, 5)
    return max(round(total, 2), 20)

df['MonthlyCharges'] = df.apply(generate_charges, axis=1)

# Generate total charges
df['TotalCharges'] = (df['MonthlyCharges'] * df['tenure']).round(2)
df['TotalCharges'] = df['TotalCharges'] * np.random.uniform(0.85, 1.15, NUM_CUSTOMERS)
df['TotalCharges'] = df['TotalCharges'].round(2)

# Calculate churn with realistic logic
print("📊 Calculating churn probabilities...")
df['churn_probability'] = df.apply(
    lambda row: calculate_churn_probability(
        row['tenure'],
        row['Contract'],
        row['MonthlyCharges'],
        row['InternetService']
    ),
    axis=1
)

# Generate churn
df['Churn'] = (np.random.random(NUM_CUSTOMERS) < df['churn_probability']).astype(int)
df['Churn'] = df['Churn'].apply(lambda x: 'Yes' if x == 1 else 'No')

# Verify churn rate
actual_churn_rate = (df['Churn'] == 'Yes').mean()
print(f"✅ Churn Rate: {actual_churn_rate:.1%} (Target: {CHURN_RATE:.1%})")

# Drop helper column
df = df.drop('churn_probability', axis=1)

# ============================================================================
# REORDER COLUMNS
# ============================================================================
column_order = [
    'customerID', 'gender', 'SeniorCitizen', 'Partner', 'Dependents',
    'tenure', 'PhoneService', 'MultipleLines', 'InternetService',
    'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport',
    'StreamingTV', 'StreamingMovies', 'Contract', 'PaperlessBilling',
    'PaymentMethod', 'MonthlyCharges', 'TotalCharges', 'Churn'
]

df = df[column_order]

# ============================================================================
# DATA VALIDATION
# ============================================================================
print("\n" + "=" * 70)
print("DATA QUALITY VALIDATION")
print("=" * 70)

print(f"\n📊 Dataset: {df.shape[0]:,} customers × {df.shape[1]} features")
print(f"✅ Missing Values: {df.isnull().sum().sum()}")
print(f"\n📊 Churn Distribution:")
print(df['Churn'].value_counts())
print(f"\n📊 Contract Distribution:")
print(df['Contract'].value_counts())
print(f"\n📊 Internet Service Distribution:")
print(df['InternetService'].value_counts())
print(f"\n📈 Numerical Summary:")
print(df[['tenure', 'MonthlyCharges', 'TotalCharges']].describe().round(2))

# ============================================================================
# SAVE DATA
# ============================================================================
output_path = r'c:\Users\Administrator\Desktop\project\p2\customer_churn_synthetic.csv'

print("\n" + "=" * 70)
print("SAVING DATA")
print("=" * 70)

df.to_csv(output_path, index=False)
print(f"✅ Data saved: {output_path}")
print(f"✅ Size: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
print(f"\n✅ DATA GENERATION COMPLETE!")
print("=" * 70)
