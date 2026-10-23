"""Shared feature contract: only calendar and weather inputs, never rental totals."""
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parent
FEATURES = ['yr','mnth','hr','holiday','weekday','workingday','weathersit','temp','hum','windspeed','hour_sin','hour_cos','month_sin','month_cos']

def features(df):
    x = df.copy()
    for field, period, name in [('hr',24,'hour'),('mnth',12,'month')]:
        x[name+'_sin'] = np.sin(2*np.pi*x[field]/period)
        x[name+'_cos'] = np.cos(2*np.pi*x[field]/period)
    return x[FEATURES].astype(float)

def load_data():
    df = pd.read_csv(ROOT/'data/hour.csv')
    before = len(df)
    df = df.drop_duplicates().dropna(subset=['cnt','dteday','hr'])
    df['timestamp'] = pd.to_datetime(df.dteday) + pd.to_timedelta(df.hr, unit='h')
    df = df.sort_values('timestamp').reset_index(drop=True)
    if not df.timestamp.is_unique:
        raise ValueError('Duplicate hourly timestamps in source data')
    return df, {'raw_rows':before,'clean_rows':len(df),'removed_rows':before-len(df),'missing_feature_cells':int(df[FEATURES[:10]].isna().sum().sum())}
