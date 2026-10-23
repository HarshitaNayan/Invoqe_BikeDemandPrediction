"""Run once: python train.py. Test period is never used to select a model."""
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from model import ROOT, FEATURES, features, load_data

def metrics(y, p):
    p = np.maximum(0,p)
    return {'MAE':float(mean_absolute_error(y,p)), 'RMSE':float(np.sqrt(mean_squared_error(y,p))), 'R2':float(r2_score(y,p))}

def main():
    out=ROOT/'artifacts'; out.mkdir(exist_ok=True)
    df, cleaning=load_data(); X=features(df); y=df.cnt
    # Split on whole dates so no day straddles the development/test boundary.
    days=df.dteday.unique(); cutoff=days[int(len(days)*.8)]
    mask=df.dteday < cutoff; xd,xt=X[mask],X[~mask]; yd,yt=y[mask],y[~mask]
    cv=TimeSeriesSplit(n_splits=3, gap=24)
    candidates={
      'Mean baseline': (DummyRegressor(), {}),
      'Linear regression': (make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LinearRegression()),{}),
      'Random forest': (make_pipeline(SimpleImputer(strategy='median'),RandomForestRegressor(n_estimators=100,n_jobs=-1,random_state=42)),{'randomforestregressor__min_samples_leaf':[2,5]}),
      'Gradient boosting': (make_pipeline(SimpleImputer(strategy='median'),HistGradientBoostingRegressor(max_iter=160,early_stopping=False,random_state=42)),{'histgradientboostingregressor__max_leaf_nodes':[15,31],'histgradientboostingregressor__l2_regularization':[0,1]})}
    rows=[]; fitted={}; params={}
    for name,(est,grid) in candidates.items():
        print('Training',name,flush=True)
        search=GridSearchCV(est,grid,scoring='neg_mean_absolute_error',cv=cv,n_jobs=1)
        search.fit(xd,yd); fitted[name]=search.best_estimator_; params[name]=search.best_params_
        rows.append({'Model':name,'CV_MAE':float(-search.best_score_)})
    winner=min(rows,key=lambda r:r['CV_MAE'])['Model']
    # All test scores are reporting only; winner was locked using development CV.
    for row in rows:
        row.update(metrics(yt,fitted[row['Model']].predict(xt)))
    pd.DataFrame(rows).to_csv(out/'metrics.csv',index=False)
    pred=np.maximum(0,fitted[winner].predict(xt))
    pd.DataFrame({'timestamp':df.loc[~mask,'timestamp'],'actual':yt,'predicted':pred}).to_csv(out/'test_predictions.csv',index=False)
    joblib.dump(fitted[winner],out/'model.joblib',compress=3)
    report={'selected_model':winner,'selection':'Lowest mean MAE in 3 expanding-window development folds, 24-observation gap; final 20% of dates held out.','features':FEATURES,'excluded':['instant','dteday','casual','registered','cnt','atemp','season'],'cleaning':cleaning,'train_rows':int(mask.sum()),'test_rows':int((~mask).sum()),'train_end':str(df.loc[mask,'timestamp'].max()),'test_start':str(df.loc[~mask,'timestamp'].min()),'test_end':str(df.timestamp.max()),'best_parameters':params,'test_metrics':metrics(yt,pred)}
    (out/'report.json').write_text(json.dumps(report,indent=2))
    fig,axs=plt.subplots(1,2,figsize=(12,4))
    df.groupby('hr').cnt.mean().plot(ax=axs[0],color='#166b63',title='Average rentals by hour',ylabel='Rentals / hour')
    df.groupby('mnth').cnt.mean().plot.bar(ax=axs[1],color='#166b63',title='Average rentals by month',ylabel='Rentals / hour')
    fig.tight_layout(); fig.savefig(out/'eda.png',dpi=150);plt.close(fig)
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
