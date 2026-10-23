from datetime import date
import json
import joblib
import pandas as pd
import streamlit as st
from model import ROOT, features, load_data
st.set_page_config(page_title='CycleScope | Bike Demand',page_icon='🚲',layout='wide')
st.markdown("""<style>
:root{--ink:#1a1820;--paper:#f6f2eb;--lav:#c7b1f0;--acid:#d5f65a}
.stApp{background:var(--paper);color:var(--ink)}
[data-testid="stHeader"]{background:var(--paper)}
.block-container{max-width:1280px;padding-top:2rem;padding-bottom:3rem}
h1,h2,h3,p,label,li,[data-testid="stCaptionContainer"]{color:var(--ink)!important}
h1,h2,h3{font-weight:850!important;letter-spacing:-1px}
[data-testid="stCaptionContainer"]{opacity:.85}
.brandbar{display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid var(--ink);padding:0 0 18px;margin-bottom:26px;font-weight:800;letter-spacing:1px;font-size:13px}
.brand{font-size:23px;letter-spacing:-1px}.brand span{background:var(--acid);border:2px solid var(--ink);padding:3px 9px;margin-right:8px}
.hero{background:var(--lav);border:3px solid var(--ink);box-shadow:8px 8px 0 var(--ink);padding:34px 38px;margin-bottom:30px;display:grid;grid-template-columns:1fr 260px;gap:24px;overflow:hidden}
.eyebrow{font:700 12px monospace;letter-spacing:2px;text-transform:uppercase}
.hero h1{font-size:clamp(42px,5.2vw,70px)!important;line-height:1.02;margin:15px 0!important;padding:0!important;max-width:700px}
.hero p{font-size:16px;max-width:570px;line-height:1.55;margin-bottom:0}
.hero-art{display:flex;align-items:center;justify-content:center;transform:rotate(-7deg)}
.art-card{background:var(--acid);border:3px solid var(--ink);box-shadow:7px 7px 0 var(--ink);padding:22px;width:230px;text-align:center}
.art-card svg{width:175px;height:115px}.art-card small{font:800 12px monospace;display:block;border-top:2px solid var(--ink);padding-top:12px}
.steps{display:grid;grid-template-columns:repeat(3,1fr);border:2px solid var(--ink);background:#fffdf8;margin:12px 0 28px}
.step{padding:16px 19px;font-size:14px}.step+.step{border-left:2px solid var(--ink)}.step b{display:block;font-size:15px;margin-bottom:5px}.step span{font-family:monospace;background:var(--acid);padding:2px 6px;margin-right:7px;border:1px solid var(--ink)}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:12px;border-bottom:0;margin:0 0 22px;flex-wrap:wrap}
button[data-baseweb="tab"]{border:2px solid var(--ink)!important;background:#fffdf8!important;padding:12px 22px!important;border-radius:0!important;height:auto!important;font-weight:750!important;color:var(--ink)!important}
button[data-baseweb="tab"][aria-selected="true"]{background:var(--acid)!important;box-shadow:4px 4px 0 var(--ink)}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none}
[data-testid="stForm"]{background:#fffdf8;border:3px solid var(--ink);border-radius:0;padding:25px;box-shadow:6px 6px 0 var(--ink)}
[data-testid="stForm"] h3{font-size:23px}
[data-testid="stNumberInputContainer"],[data-baseweb="select"]>div,[data-testid="stDateInput"] [data-baseweb="input"]{background:#f3edfc!important;color:var(--ink)!important;border:2px solid var(--ink)!important;border-radius:0!important}
input{color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important}
[data-baseweb="select"] span{color:var(--ink)!important}
[data-testid="stWidgetLabel"] p{font-weight:700!important;font-size:14px!important}
[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button{background:var(--acid)!important;border:2px solid var(--ink)!important;box-shadow:4px 4px 0 var(--ink);border-radius:0!important;color:var(--ink)!important;padding:12px 24px!important;font-weight:800!important;transition:transform .15s,box-shadow .15s}
[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover{transform:translate(2px,2px);box-shadow:2px 2px 0 var(--ink)}
.result-card{background:var(--acid);border:3px solid var(--ink);box-shadow:6px 6px 0 var(--ink);padding:25px;margin-bottom:22px}
.result-card .count{font-size:76px;font-weight:900;letter-spacing:-5px;line-height:1.1;margin:18px 0 8px}
.result-card h3{margin:0;padding:0;font-size:23px}.result-card p{font-size:14px;line-height:1.6}
.result-card .tag{display:inline-block;background:var(--ink);color:white;padding:5px 9px;font:700 11px monospace;letter-spacing:1px}
.note{border:2px solid var(--ink);padding:18px;background:var(--lav);font-size:14px;line-height:1.6}
[data-testid="stMetric"]{border:2px solid var(--ink);background:var(--lav);padding:18px;box-shadow:4px 4px 0 var(--ink)}
[data-testid="stMetricValue"]{color:var(--ink)!important;font-weight:850}
[data-testid="stExpander"]{background:#fffdf8;border:2px solid var(--ink);border-radius:0}
a{color:#563091!important}hr{border-color:var(--ink)!important}
@media(max-width:700px){.hero{grid-template-columns:1fr;padding:24px}.hero-art{display:none}.steps{grid-template-columns:1fr}.step+.step{border-left:0;border-top:2px solid var(--ink)}.brandbar{font-size:10px}.block-container{padding:1rem}.hero h1{font-size:44px!important}}
</style>""",unsafe_allow_html=True)
st.markdown("""<div class="brandbar"><div class="brand"><span>↗</span> CycleScope</div><div>DEMAND LAB / VOL. 01</div></div>
<div class="hero"><div><div class="eyebrow">REAL DATA. BETTER ESTIMATES.</div><h1>Small inputs.<br>Big bike energy.</h1><p>Turn an hour, a little weather, and historical patterns into an estimate of bike rental demand.</p></div><div class="hero-art"><div class="art-card"><svg viewBox="0 0 220 135" fill="none" stroke="#1a1820" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><circle cx="48" cy="91" r="31"/><circle cx="172" cy="91" r="31"/><path d="M48 91L85 34 119 91H48L76 47H145L172 91M119 91L145 25H163M73 29H94"/><path d="M15 12H45M30 1V24" stroke-width="3"/></svg><small>MORE PATTERNS. LESS GUESSWORK.</small></div></div></div>""",unsafe_allow_html=True)
if not (ROOT/'artifacts/model.joblib').exists():
    st.error('Train the model first: run python train.py in your terminal.'); st.stop()
@st.cache_resource
def bundle():
    return joblib.load(ROOT/'artifacts/model.joblib'),json.loads((ROOT/'artifacts/report.json').read_text())
@st.cache_data
def dataset(): return load_data()[0]
model,report=bundle(); df=dataset()
predict,explore,results=st.tabs(['Predict demand','Explore data','Model results'])
with predict:
    st.markdown('<div class="steps"><div class="step"><b><span>01</span> Set the scene</b>Choose a historical date and hour.</div><div class="step"><b><span>02</span> Add the weather</b>Adjust conditions for your scenario.</div><div class="step"><b><span>03</span> Get an estimate</b>See predicted rentals for that hour.</div></div>',unsafe_allow_html=True)
    left,right=st.columns([1.65,1],gap='large')
    with left:
        with st.form('prediction'):
            st.subheader('01 / Build your scenario')
            a,b=st.columns(2)
            with a:
                day=st.date_input('Date',date(2012,10,15),min_value=date(2011,1,1),max_value=date(2012,12,31))
                hour=st.slider('Hour of day',0,23,17,help='17 means 5 PM; 0 means midnight.')
                temperature=st.slider('Temperature (°C)',-8.0,39.0,20.0,.5)
            with b:
                weather=st.selectbox('Weather',[1,2,3],format_func=lambda n:{1:'Clear / partly cloudy',2:'Mist / cloudy',3:'Light rain / light snow'}[n])
                humidity=st.slider('Humidity (%)',0,100,60)
                wind=st.slider('Wind speed',0.0,67.0,10.0,.5,help='Original dataset wind-speed scale, divided by 67 before model input.')
            holiday=st.checkbox('This date is a public holiday in Washington, DC')
            submitted=st.form_submit_button('PREDICT RENTALS ↗',use_container_width=True)
    with right:
        if submitted:
            row=pd.DataFrame([dict(yr=day.year-2011,mnth=day.month,hr=hour,holiday=int(holiday),weekday=(day.weekday()+1)%7,workingday=int(day.weekday()<5 and not holiday),weathersit=weather,temp=(temperature+8)/47,hum=humidity/100,windspeed=wind/67)])
            value=max(0,float(model.predict(features(row))[0]))
            st.session_state['last_prediction']={'value':value,'date':day.strftime('%d %b %Y'),'hour':f'{hour:02d}:00','temperature':temperature}
        result=st.session_state.get('last_prediction')
        if result:
            st.markdown(f'<div class="result-card"><div class="tag">YOUR LAST PREDICTION</div><div class="count">{result["value"]:,.0f}</div><h3>rentals in one hour.</h3><p>{result["date"]} · {result["hour"]} · {result["temperature"]:g}°C<br>Total across the recorded bike-sharing system.</p></div>',unsafe_allow_html=True)
            st.caption('Change the inputs and press Predict rentals to update this result.')
        else:
            st.markdown('<div class="result-card"><div class="tag">READY WHEN YOU ARE</div><div class="count">— —</div><h3>Your next estimate<br>starts on the left.</h3><p>Try the prefilled scenario: a clear Monday at 5 PM, with 20°C temperature. Then press Predict rentals.</p></div>',unsafe_allow_html=True)
        st.markdown(f'<div class="note"><b>A prediction, in plain language.</b><br>The model learned patterns from past rentals. Your inputs help it estimate a similar hour.<br><br><b>Typical test error: {report["test_metrics"]["MAE"]:.0f} rentals/hour.</b><br>This is an average error, not a guaranteed range.</div>',unsafe_allow_html=True)
    st.caption('HISTORICAL SANDBOX · Washington, DC / 2011–2012. Weather is entered manually. These estimates do not represent current demand.')
with explore:
    st.subheader('Understand the rental patterns')
    a,b,c=st.columns(3);a.metric('Hourly records',f'{len(df):,}');b.metric('Total rentals',f'{df.cnt.sum():,}');c.metric('Removed rows',report['cleaning']['removed_rows'])
    st.line_chart(df.groupby(['hr','workingday']).cnt.mean().unstack().rename(columns={0:'Weekend / holiday',1:'Working day'}))
    st.caption('Average rental count by hour of day')
    st.bar_chart(df.groupby('mnth').cnt.mean());st.caption('Average hourly rental count by month')
    st.dataframe(df.drop(columns=['timestamp']).head(30),hide_index=True)
    st.write('Missing values by column');st.dataframe(df.isna().sum().rename('Missing cells'))
    st.caption('This dataset has no missing values in its original release. Cleaning is checked rather than inventing missing data; model pipelines still handle missing feature cells.')
with results:
    st.subheader('Measured performance')
    st.write(report['selection'])
    a,b,c=st.columns(3);a.metric('MAE',f"{report['test_metrics']['MAE']:.2f}");b.metric('RMSE',f"{report['test_metrics']['RMSE']:.2f}");c.metric('R²',f"{report['test_metrics']['R2']:.3f}")
    st.dataframe(pd.read_csv(ROOT/'artifacts/metrics.csv'),hide_index=True)
    st.caption('CV_MAE selects the model. MAE, RMSE and R² describe the untouched final test period. Lower MAE/RMSE is better; higher R² is better.')
    st.write(f"Development: {report['train_rows']:,} hours through {report['train_end']}. Test: {report['test_rows']:,} hours, {report['test_start']} to {report['test_end']}.")
    predictions=pd.read_csv(ROOT/'artifacts/test_predictions.csv',parse_dates=['timestamp'])
    st.line_chart(predictions.set_index('timestamp')[['actual','predicted']].head(168))
    st.caption('First seven days of held-out predictions')
    st.download_button('Download held-out predictions',predictions.to_csv(index=False),'test_predictions.csv','text/csv')
    with st.expander('Features, tuning and limitations'):
        st.json(report)
        st.write('casual and registered are excluded because they sum to the target. IDs and raw dates are excluded. Apparent temperature is omitted to reduce redundant inputs. Calendar cycles are engineered. No accuracy threshold is promised. Historical weather observations make this a conditional estimate; a live forecast would need weather forecast inputs and evaluation under forecast error.')
st.divider()
st.markdown('Dataset: [UCI Bike Sharing](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) · Hadi Fanaee-T (2013), [DOI](https://doi.org/10.24432/C5W894) · CC BY 4.0. Historical Capital Bikeshare observations, 2011–2012.')
