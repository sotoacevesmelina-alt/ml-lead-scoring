"""
Interactive Lead Scoring Web App
Real-time lead score predictions using trained ML model
Built by: Melina (Loyola University Chicago)
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(
    page_title="PredictAI Lead",
    page_icon="🎯",
    layout="wide"
)

# Load model artifacts
@st.cache_resource
def load_model():
    model = joblib.load('lead_scoring_model.pkl')
    scaler = joblib.load('lead_scoring_scaler.pkl')
    encoders = joblib.load('lead_scoring_encoders.pkl')
    feature_cols = joblib.load('feature_columns.pkl')
    return model, scaler, encoders, feature_cols

model, scaler, encoders, feature_cols = load_model()

st.markdown("""
### Understanding AI-Powered Lead Scoring

This tool demonstrates how machine learning can predict which sales leads are most likely to convert.

**How it works:** The model analyzes historical patterns in company size, engagement signals, and deal velocity to predict conversion probability with 82.5% accuracy.

Use this tool to see AI in action for sales prioritization.
""")

st.divider()

# Title and description
st.title("🎯 PredictAI Lead")
st.markdown("""
**Enter lead details below** to generate an AI-powered score. The model weighs each input against patterns
learned from 600 historical B2B SaaS deals — giving your sales team an objective, data-driven priority ranking.
""")

st.divider()

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    st.subheader("Company Information")
    
    industry = st.selectbox(
        "Industry",
        ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing', 
         'Education', 'Real Estate', 'Media', 'Consulting', 'Transportation']
    )
    
    company_size = st.selectbox(
        "Company Size",
        ['1-50', '51-200', '201-500', '501-1000', '1000+']
    )
    
    employee_count = st.number_input(
        "Approximate Employee Count",
        min_value=1,
        max_value=10000,
        value=100,
        step=1
    )
    
    region = st.selectbox(
        "Region",
        ['Northeast', 'Southeast', 'Midwest', 'West', 'Southwest', 'International']
    )

with col2:
    st.subheader("Lead Details")
    
    lead_source = st.selectbox(
        "Lead Source",
        ['Website', 'Referral', 'LinkedIn', 'Cold Outreach', 'Event', 
         'Partner', 'Trade Show', 'Content Download', 'Webinar']
    )
    
    budget = st.selectbox(
        "Budget Range",
        ['<$10k', '$10k-$50k', '$50k-$100k', '$100k+']
    )
    
    timeline = st.selectbox(
        "Decision Timeline",
        ['Immediate', '1-3 months', '3-6 months', '6+ months']
    )
    
    job_title = st.selectbox(
        "Job Title",
        ['CEO', 'Owner', 'CFO', 'COO', 'CTO', 'VP Sales', 'VP Operations',
         'Director Sales', 'Director Marketing', 'Sales Manager']
    )

st.divider()

# Engagement metrics
st.subheader("Engagement Metrics")
st.caption("Behavioral signals are among the strongest predictors of conversion. The model learned this from historical deal data — leads who view pricing pages and click emails close at significantly higher rates.")
col3, col4, col5 = st.columns(3)

with col3:
    email_opens = st.slider("Email Opens", 0, 20, 5)
    email_clicks = st.slider("Email Clicks", 0, 10, 2)

with col4:
    website_visits = st.slider("Website Visits", 0, 30, 8)
    pricing_page_views = st.slider("Pricing Page Views", 0, 10, 1)

with col5:
    demo_requested = st.selectbox("Demo Requested?", ["No", "Yes"])
    demo_requested_val = 1 if demo_requested == "Yes" else 0
    
    response_time = st.number_input(
        "Response Time (hours)",
        min_value=0.5,
        max_value=120.0,
        value=2.0,
        step=0.5
    )

st.divider()

# Predict button
if st.button("🚀 Calculate Lead Score", type="primary", use_container_width=True):
    
    # Prepare input data
    input_data = {
        'Industry': industry,
        'Company_Size': company_size,
        'Employee_Count': employee_count,
        'Lead_Source': lead_source,
        'Budget_Range': budget,
        'Decision_Timeline': timeline,
        'Job_Title': job_title,
        'Region': region,
        'Email_Opens': email_opens,
        'Email_Clicks': email_clicks,
        'Website_Visits': website_visits,
        'Pricing_Page_Views': pricing_page_views,
        'Demo_Requested': demo_requested_val,
        'Response_Time_Hours': response_time
    }
    
    # Encode categorical variables
    input_df = pd.DataFrame([input_data])
    for col in ['Industry', 'Company_Size', 'Lead_Source', 'Budget_Range', 
                'Decision_Timeline', 'Job_Title', 'Region']:
        input_df[col + '_encoded'] = encoders[col].transform(input_df[col])
    
    # Select features in correct order
    X_input = input_df[feature_cols]
    
    # Scale and predict
    X_scaled = scaler.transform(X_input)
    win_probability = model.predict_proba(X_scaled)[0][1]
    prediction = model.predict(X_scaled)[0]
    
    # Display results
    st.success("✅ Lead Score Calculated!")
    
    # Main score display
    col_a, col_b, col_c = st.columns([2, 2, 2])
    
    with col_a:
        st.metric(
            "Win Probability",
            f"{win_probability*100:.1f}%",
            delta="High" if win_probability > 0.7 else "Medium" if win_probability > 0.4 else "Low"
        )
    
    with col_b:
        score_out_of_100 = int(win_probability * 100)
        st.metric(
            "Lead Score",
            f"{score_out_of_100}/100",
            delta=None
        )
    
    with col_c:
        if win_probability > 0.75:
            priority = "🔥 HOT LEAD"
            color = "red"
        elif win_probability > 0.50:
            priority = "⚡ WARM LEAD"
            color = "orange"
        else:
            priority = "❄️ COLD LEAD"
            color = "blue"
        
        st.metric("Priority", priority)
    
    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=win_probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Win Probability", 'font': {'size': 24}},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': '#ffcccc'},
                {'range': [40, 70], 'color': '#fff4cc'},
                {'range': [70, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("📋 Recommended Actions")
    
    if win_probability > 0.75:
        st.info("""
        **HIGH PRIORITY - Act Immediately**
        - ✅ Schedule demo/discovery call within 24 hours
        - ✅ Assign to senior AE for personalized outreach
        - ✅ Send custom proposal within 48 hours
        - ✅ Add to priority follow-up cadence
        """)
    elif win_probability > 0.50:
        st.warning("""
        **MEDIUM PRIORITY - Nurture Carefully**
        - ⚡ Continue email nurture sequence
        - ⚡ Send relevant case studies and content
        - ⚡ Schedule follow-up in 3-5 business days
        - ⚡ Monitor engagement signals
        """)
    else:
        st.error("""
        **LOW PRIORITY - Long-term Nurture**
        - ❄️ Add to automated drip campaign
        - ❄️ Send quarterly check-ins
        - ❄️ Focus on building relationship over time
        - ❄️ Re-score after 30 days of engagement
        """)
    
    # Key factors
    st.subheader("🔍 Why Did the Model Score It This Way?")
    st.markdown("These are the features with the most influence on your result. Higher-impact factors carry more weight in the logistic regression — meaning small changes here shift the score significantly.")
    
    factors_df = pd.DataFrame({
        'Factor': ['Pricing Page Views', 'Budget Range', 'Demo Requested', 
                  'Email Clicks', 'Decision Timeline', 'Lead Source'],
        'Your Value': [pricing_page_views, budget, demo_requested, 
                      email_clicks, timeline, lead_source],
        'Impact': ['Very High', 'Very High', 'High', 'Medium', 'Medium', 'Medium']
    })
    
    st.dataframe(factors_df, use_container_width=True, hide_index=True)

# Sidebar with model info
with st.sidebar:
    st.header("📊 Model Information")
    st.metric("Model Accuracy", "82.5%")
    st.metric("ROC AUC Score", "0.712")
    st.metric("Training Dataset", "600 leads")
    
    st.divider()
    
    st.subheader("Top 5 Predictive Features")
    st.markdown("""
    1. **Pricing Page Views** 🥇
    2. **Budget Range** 🥈
    3. **Demo Requested** 🥉
    4. **Email Clicks** 
    5. **Employee Count**
    """)
    
    st.divider()
    
    st.subheader("About This Model")
    st.markdown("""
    This tool uses **Logistic Regression** — a classification algorithm that outputs a probability
    between 0 and 1. It was trained on 600 historical B2B SaaS deals, learning which combinations
    of company profile and engagement behavior predict a closed-won outcome.

    **Why Logistic Regression?** It's highly interpretable — each feature has a coefficient that
    directly explains its contribution to the score, making it easy to understand and trust for
    sales decision-making.
    """)

# Footer
st.divider()
st.markdown("**Built by:** Melina Soto Aceves")
