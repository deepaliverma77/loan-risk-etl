import pandas as pd
import os

input_path = os.path.join("..", "data", "loan_2014_18.csv")
output_path = os.path.join("..", "data", "loan_cleaned_data.csv")
df=pd.read_csv(input_path, low_memory=False)

df.drop_duplicates(inplace=True)
df.drop(columns=[col for col in df.columns if 'unnamed'in col.lower()], inplace=True)
null_thresh=0.8
df=df.loc[:,df.isnull().mean()<null_thresh]
drop_cols=[
    'id',  'member_id', 'url', 'desc', 'title', 'zip_code',
    'emp_title', 'pymnt_plan', 'application_type', 'initial_list_status',
    'policy_code', 'sub_grade', 'issue_d'
]
df.drop(columns=[col for col in drop_cols if col in df.columns],inplace=True)
df=df[df['loan_status'].isin(['Fully paid', 'Charged Off'])]

df['loan_status']= df['loan_status'].map({'Fully Paid': 0, 'Charged Off': 1})

df['int_rate']= df['int_rate'].str.replace('%','').astype(float)
if 'revol_util' in df.columns:
    df['revol_util']= df['revol_util'].str.replace('%','').astype(float)
    
def clean_emp_length(val):
    if pd.isna(val):
        return None
    if '< 1' in val:
        return 0
    if '10+' in val:
        return 10
    return int(''.join(filter(str.isdigit, val)))
df['emp_length']= df['emp_length'].apply(clean_emp_length)

date_cols= ['earliest_cr_line', 'last_pymnt_d', 'next_pymnt_d', 'last_credit_pull_d']
for col in date_cols:
    if col in df.columns:
        df[col]=pd.to_datetime(df[col], errors='coerce')
        
num_cols= df.select_dtypes(include='number').columns
for col in num_cols:
    df[col].fillna(df[col].median(), inplace=True)

cat_cols= df.select_dtypes(include='object').columns
for col in cat_cols:
    df[col].fillna(df[col].mode()[0], inplace=True)
    
df.pd.get_dummies(df, drop_first=True)

df.to_csv(output_path, index=False)

print('Data cleaning complete. Rows:',df.shape[0], "| Columns:", df.shape[1])