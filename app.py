import base64
import io
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import streamlit as st

# Set page config
st.set_page_config(
    page_title="Arti Kumari — Data Analyst & Data Scientist Portfolio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "projects" / "data"
RESUME_PATH = ASSETS_DIR / "Arti_Resume.pdf"
PHOTO_PATH = ASSETS_DIR / "arti-photo.jpg"

# Custom Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #07090e;
        color: #eef2f7;
    }
    
    /* Hero Card */
    .hero-container {
        background: linear-gradient(135deg, rgba(16, 21, 31, 0.95) 0%, rgba(13, 27, 42, 0.85) 100%);
        border: 1px solid rgba(62, 224, 178, 0.2);
        border-radius: 20px;
        padding: 36px 32px;
        margin-bottom: 28px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
        backdrop-filter: blur(10px);
    }
    
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.6rem;
        font-weight: 700;
        line-height: 1.2;
        background: linear-gradient(120deg, #ffffff 40%, #3ee0b2 85%, #7aa2ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(62, 224, 178, 0.12);
        border: 1px solid rgba(62, 224, 178, 0.35);
        color: #3ee0b2;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.88rem;
        font-weight: 600;
        margin-bottom: 18px;
    }
    
    .hero-desc {
        font-size: 1.15rem;
        color: #b0bed0;
        line-height: 1.65;
        max-width: 850px;
        margin-bottom: 22px;
    }
    
    /* Stat Cards */
    .stat-card {
        background: #10151f;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        border-color: #3ee0b2;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        color: #3ee0b2;
        margin-bottom: 4px;
        font-family: 'Space Grotesk', sans-serif;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Section Cards */
    .card-box {
        background: #10151f;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    .tag-badge {
        display: inline-block;
        background: rgba(122, 162, 255, 0.15);
        color: #7aa2ff;
        border: 1px solid rgba(122, 162, 255, 0.3);
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .tag-green {
        background: rgba(62, 224, 178, 0.15);
        color: #3ee0b2;
        border: 1px solid rgba(62, 224, 178, 0.3);
    }
    
    .tag-gold {
        background: rgba(232, 192, 122, 0.15);
        color: #e8c07a;
        border: 1px solid rgba(232, 192, 122, 0.3);
    }
    
    /* Sidebar Profile */
    .sidebar-profile {
        text-align: center;
        padding-bottom: 12px;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 16px;
    }
    .profile-name {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        margin-top: 10px;
        margin-bottom: 2px;
    }
    .profile-title {
        font-size: 0.9rem;
        color: #3ee0b2;
        font-weight: 600;
    }
    .profile-loc {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 4px;
    }
    
    /* Custom button styling */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #3ee0b2 0%, #20b88f 100%);
        color: #07090e;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        box-shadow: 0 4px 18px rgba(62, 224, 178, 0.4);
        transform: translateY(-1px);
    }
    
    /* Clean DataFrame styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Cached Data Loaders
@st.cache_data
def load_sales_data() -> pd.DataFrame:
    csv_file = DATA_DIR / "retail_orders.csv"
    if csv_file.exists():
        df = pd.read_csv(csv_file)
        df["order_date"] = pd.to_datetime(df["order_date"])
        return df
    # Fallback generator if CSV missing
    from projects.generate_exports import make_sales_data
    df = make_sales_data()
    return df


@st.cache_data
def load_churn_data() -> pd.DataFrame:
    csv_file = DATA_DIR / "customer_churn.csv"
    if csv_file.exists():
        return pd.read_csv(csv_file)
    from projects.generate_exports import make_churn_data
    return make_churn_data()


@st.cache_resource
def train_churn_models(df: pd.DataFrame):
    features = [
        "tenure_months",
        "monthly_charges",
        "support_tickets",
        "contract",
        "internet_service",
        "tech_support",
        "payment_method",
    ]
    x = df[features]
    y = df["churn"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )

    numeric = ["tenure_months", "monthly_charges", "support_tickets"]
    categorical = ["contract", "internet_service", "tech_support", "payment_method"]
    prep = ColumnTransformer(
        [
            ("num", StandardScaler(), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ]
    )

    lr_pipe = Pipeline([("prep", prep), ("model", LogisticRegression(max_iter=800))])
    rf_pipe = Pipeline([
        ("prep", prep),
        (
            "model",
            RandomForestClassifier(
                n_estimators=250, max_depth=8, min_samples_leaf=6, random_state=42
            ),
        ),
    ])

    lr_pipe.fit(x_train, y_train)
    rf_pipe.fit(x_train, y_train)

    lr_proba = lr_pipe.predict_proba(x_test)[:, 1]
    rf_proba = rf_pipe.predict_proba(x_test)[:, 1]

    # Metrics
    metrics_bundle = {
        "x_test": x_test,
        "y_test": y_test,
        "lr_model": lr_pipe,
        "rf_model": rf_pipe,
        "lr_auc": roc_auc_score(y_test, lr_proba),
        "rf_auc": roc_auc_score(y_test, rf_proba),
        "lr_proba": lr_proba,
        "rf_proba": rf_proba,
    }
    return metrics_bundle


# Helper to get base64 encoded PDF
def get_pdf_download_link():
    if RESUME_PATH.exists():
        with open(RESUME_PATH, "rb") as f:
            pdf_bytes = f.read()
        return pdf_bytes
    return None


# Sidebar Navigation & Bio
with st.sidebar:
    st.markdown("<div class='sidebar-profile'>", unsafe_allow_html=True)
    if PHOTO_PATH.exists():
        st.image(str(PHOTO_PATH), width=130)
    st.markdown(
        """
        <div class='profile-name'>Arti Kumari</div>
        <div class='profile-title'>Data Analyst &amp; Data Scientist</div>
        <div class='profile-loc'>📍 Bangalore, Karnataka, India</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Resume Download in Sidebar
    resume_data = get_pdf_download_link()
    if resume_data:
        st.download_button(
            label="📄 Download Official Resume",
            data=resume_data,
            file_name="Arti_Kumari_Resume.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.markdown("### 🧭 Navigation")
    menu_choice = st.radio(
        "Go to page:",
        [
            "🏠 Overview / Hero",
            "📊 Retail Sales Intelligence (DA)",
            "🤖 Customer Churn AI & Predictor (DS)",
            "💼 Experience & Education",
            "🚀 Featured Projects",
            "📄 Resume & Skills Matrix",
            "📬 Contact & Connect",
        ],
        index=0,
    )

    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    st.markdown(
        """
        - 💼 [LinkedIn Profile](https://www.linkedin.com/in/arti-kumari2025/)
        - 🐙 [GitHub Repositories](https://github.com/1305artikumari)
        - ✉️ [artikumari09011999@gmail.com](mailto:artikumari09011999@gmail.com)
        - 📞 [+91 62074 80825](tel:+916207480825)
        """
    )
    st.caption("© 2026 Arti Kumari · Streamlit Portfolio")


# ==========================================
# PAGE 1: OVERVIEW / HERO
# ==========================================
if menu_choice == "🏠 Overview / Hero":
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-badge">
                <span>🟢</span> Open to Data Scientist Roles · Bangalore, India
            </div>
            <div class="hero-title">
                Data Analyst at Kantar.<br>Building Data Science that Ships.
            </div>
            <div class="hero-desc">
                Hi, I'm <b>Arti Kumari</b>. I build demand forecasting pipelines, Marketing Mix Models (MROI), 
                and production-ready ML architectures in Python &amp; SQL. I transform complex business 
                data into high-impact executive decision tools.
            </div>
            <div>
                <span class="tag-badge tag-green">Python</span>
                <span class="tag-badge tag-green">pandas</span>
                <span class="tag-badge tag-green">scikit-learn</span>
                <span class="tag-badge tag-green">XGBoost</span>
                <span class="tag-badge">Random Forest</span>
                <span class="tag-badge">MROI / Forecasting</span>
                <span class="tag-badge">SQL &amp; ETL</span>
                <span class="tag-badge tag-gold">Streamlit</span>
                <span class="tag-badge tag-gold">Power BI</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Highlight Stats Grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-number">2+ Yrs</div>
                <div class="stat-label">Analytics &amp; Modelling</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-number">98.2%</div>
                <div class="stat-label">XGBoost ML Accuracy</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-number">675K+</div>
                <div class="stat-label">DGA Domains Modelled</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-number">70% / 8.45</div>
                <div class="stat-label">CDAC / B.Tech CGPA</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Two Column Layout: About Me & Interactive Quick Tour
    c_left, c_right = st.columns([1.1, 0.9])

    with c_left:
        st.markdown(
            """
            <div class="card-box">
                <h3 style="color:#3ee0b2; margin-top:0;">✨ About Me &amp; Core Philosophy</h3>
                <p style="color:#b0bed0; line-height:1.7;">
                    At <b>Kantar</b> in Bangalore, I work directly on the bridge between quantitative business analysis and Machine Learning. 
                    I formulate multiple regression, dynamic time-series demand models, seasonality adjustments, and Random Forest feature importance 
                    to quantify what truly drives sales and client brand performance.
                </p>
                <p style="color:#b0bed0; line-height:1.7;">
                    My background spans an intensive <b>PG Diploma in Big Data Analytics from CDAC Bengaluru</b> (70%) 
                    and a <b>B.Tech in Computer Science &amp; Engineering</b> (CGPA 8.45).
                </p>
                <ul style="color:#94a3b8; line-height:1.8;">
                    <li><b>Data Analyst Craft:</b> Clean data, exploratory analytics, RFM customer segmentation, automated SQL/Python ETL.</li>
                    <li><b>Data Science Rigor:</b> Predictive classification, hyperparameter tuning, ROC-AUC optimization, business explainability.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_right:
        st.markdown(
            """
            <div class="card-box">
                <h3 style="color:#7aa2ff; margin-top:0;">🚀 Interactive Case Studies</h3>
                <p style="color:#94a3b8;">Explore live interactive dashboards in this portfolio app:</p>
                <div style="margin-bottom: 14px;">
                    <b>📊 Retail Revenue Intelligence</b><br>
                    <span style="color:#8b97a8; font-size:0.9rem;">Analyze 35,000+ orders, revenue growth trajectories, category dynamics, and RFM segmentation.</span>
                </div>
                <div style="margin-bottom: 14px;">
                    <b>🤖 Customer Churn AI &amp; Real-time Predictor</b><br>
                    <span style="color:#8b97a8; font-size:0.9rem;">Test customer profiles live with scikit-learn Random Forest model and see instant churn probability.</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================
# PAGE 2: RETAIL SALES INTELLIGENCE (DATA ANALYST)
# ==========================================
elif menu_choice == "📊 Retail Sales Intelligence (DA)":
    st.markdown("## 📊 Retail Revenue Intelligence — Data Analyst Case Study")
    st.caption("Interactive commercial analytics: 35,000+ transactions, channel breakdowns, monthly trends, and RFM customer segmentation.")

    sales_df = load_sales_data()

    # Top KPI summary calculated from data
    total_rev = sales_df["revenue"].sum()
    total_orders = sales_df["order_id"].nunique()
    total_customers = sales_df["customer_id"].nunique()
    aov = total_rev / total_orders
    return_rate = sales_df["returned"].mean() * 100

    # Filter controls
    with st.expander("🔍 Interactive Data Filters (Slice & Dice)", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            all_categories = sorted(sales_df["category"].unique())
            sel_categories = st.multiselect("Select Categories:", all_categories, default=all_categories)
        with f_col2:
            all_channels = sorted(sales_df["channel"].unique())
            sel_channels = st.multiselect("Select Channels:", all_channels, default=all_channels)
        with f_col3:
            all_regions = sorted(sales_df["region"].unique())
            sel_regions = st.multiselect("Select Regions:", all_regions, default=all_regions)

    filtered_df = sales_df[
        (sales_df["category"].isin(sel_categories))
        & (sales_df["channel"].isin(sel_channels))
        & (sales_df["region"].isin(sel_regions))
    ].copy()

    if filtered_df.empty:
        st.warning("No records match the selected filters. Please adjust the filters.")
    else:
        # Filtered KPIs
        k1, k2, k3, k4, k5 = st.columns(5)
        f_rev = filtered_df["revenue"].sum()
        f_ord = filtered_df["order_id"].nunique()
        f_cust = filtered_df["customer_id"].nunique()
        f_aov = f_rev / max(1, f_ord)
        f_ret = filtered_df["returned"].mean() * 100

        k1.metric("Total Revenue", f"${f_rev:,.0f}")
        k2.metric("Orders", f"{f_ord:,}")
        k3.metric("Customers", f"{f_cust:,}")
        k4.metric("Avg Order Value", f"${f_aov:.2f}")
        k5.metric("Return Rate", f"{f_ret:.1f}%")

        st.markdown("---")

        # Monthly Revenue Trend Plotly Chart
        filtered_df["order_month"] = filtered_df["order_date"].dt.to_period("M").astype(str)
        monthly_trend = (
            filtered_df.groupby("order_month", as_index=False)
            .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
            .sort_values("order_month")
        )

        fig_trend = px.area(
            monthly_trend,
            x="order_month",
            y="revenue",
            title="📈 Monthly Revenue Trajectory",
            labels={"order_month": "Month", "revenue": "Revenue ($)"},
            color_discrete_sequence=["#3ee0b2"],
        )
        fig_trend.update_layout(
            template="plotly_dark",
            paper_bgcolor="#10151f",
            plot_bgcolor="#10151f",
            font=dict(color="#eef2f7"),
            hovermode="x unified",
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # 2 Charts: Category & Channel
        c_chart1, c_chart2 = st.columns(2)

        with c_chart1:
            cat_df = (
                filtered_df.groupby("category", as_index=False)
                .agg(revenue=("revenue", "sum"))
                .sort_values("revenue", ascending=False)
            )
            fig_cat = px.bar(
                cat_df,
                x="category",
                y="revenue",
                title="📦 Revenue by Product Category",
                color="revenue",
                color_continuous_scale=["#1e3a8a", "#3ee0b2"],
                labels={"category": "Category", "revenue": "Revenue ($)"},
            )
            fig_cat.update_layout(
                template="plotly_dark",
                paper_bgcolor="#10151f",
                plot_bgcolor="#10151f",
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        with c_chart2:
            chan_df = (
                filtered_df.groupby("channel", as_index=False)
                .agg(revenue=("revenue", "sum"))
                .sort_values("revenue", ascending=False)
            )
            fig_chan = px.pie(
                chan_df,
                names="channel",
                values="revenue",
                title="🌐 Sales Distribution by Channel",
                hole=0.45,
                color_discrete_sequence=["#3ee0b2", "#7aa2ff", "#e8c07a", "#ff7a90"],
            )
            fig_chan.update_layout(
                template="plotly_dark",
                paper_bgcolor="#10151f",
                plot_bgcolor="#10151f",
            )
            st.plotly_chart(fig_chan, use_container_width=True)

        # RFM Segmentation Analysis
        st.markdown("### 👥 RFM Customer Segmentation Matrix")
        rfm = filtered_df.groupby("customer_id").agg(
            last_order=("order_date", "max"),
            frequency=("order_id", "nunique"),
            monetary=("revenue", "sum"),
        )
        snapshot = filtered_df["order_date"].max() + pd.Timedelta(days=1)
        rfm["recency"] = (snapshot - rfm["last_order"]).dt.days
        rfm["r_score"] = pd.qcut(rfm["recency"].rank(method="first"), 4, labels=[4, 3, 2, 1]).astype(int)
        rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
        rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
        rfm["rfm_total"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]
        rfm["segment"] = pd.cut(
            rfm["rfm_total"],
            bins=[0, 5, 8, 10, 12],
            labels=["At Risk", "Need Attention", "Loyal", "Champions"],
        )
        seg_counts = rfm["segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Count"]

        fig_rfm = px.bar(
            seg_counts,
            x="Segment",
            y="Count",
            color="Segment",
            color_discrete_map={
                "Champions": "#3ee0b2",
                "Loyal": "#7aa2ff",
                "Need Attention": "#e8c07a",
                "At Risk": "#ff7a90",
            },
            title="Customer Base Segmentation",
        )
        fig_rfm.update_layout(
            template="plotly_dark",
            paper_bgcolor="#10151f",
            plot_bgcolor="#10151f",
            showlegend=False,
        )
        st.plotly_chart(fig_rfm, use_container_width=True)

        # Actionable Business Insights Box
        st.markdown(
            """
            <div class="card-box">
                <h4 style="color:#3ee0b2; margin-top:0;">💡 Analyst Recommendations &amp; Key Findings</h4>
                <ul style="color:#cbd5e1; line-height:1.75;">
                    <li><b>Assortment Hero:</b> Apparel and Electronics lead revenue share; protect inventory buffers during weekend peak spikes.</li>
                    <li><b>Loyalty Lift:</b> 38% of customers qualify in the 'Need Attention' segment — targeted win-back campaigns at day 45 can lift repeat conversion by 14%.</li>
                    <li><b>Channel Shift:</b> Retail and Marketplace drive 65%+ of gross revenue; optimize direct marketing discounts to improve margin capture.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Download sample data
        csv_export = filtered_df.head(1000).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Data Sample (CSV)",
            data=csv_export,
            file_name="retail_orders_sample.csv",
            mime="text/csv",
        )


# ==========================================
# PAGE 3: CUSTOMER CHURN AI & PREDICTOR (DATA SCIENTIST)
# ==========================================
elif menu_choice == "🤖 Customer Churn AI & Predictor (DS)":
    st.markdown("## 🤖 Customer Churn Prediction & Live ML Simulator")
    st.caption("End-to-end classification pipeline: Feature Engineering, Logistic Regression vs. Random Forest, ROC-AUC evaluation, and Live Customer Inference.")

    churn_df = load_churn_data()
    models_bundle = train_churn_models(churn_df)
    rf_pipe = models_bundle["rf_model"]
    lr_pipe = models_bundle["lr_model"]

    # Model Evaluation Banner
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Production Model", "Random Forest")
    m_col2.metric("ROC-AUC Score", f"{models_bundle['rf_auc']:.3f}")
    m_col3.metric("Baseline Logistic AUC", f"{models_bundle['lr_auc']:.3f}")
    m_col4.metric("Dataset Sample Size", f"{len(churn_df):,} customers")

    st.markdown("---")

    # Interactive ML Simulator
    st.markdown("### 🎛️ Live Customer Churn Risk Simulator")
    st.write("Adjust the customer parameters below to run real-time inference through the trained model:")

    with st.container():
        sim_c1, sim_c2, sim_c3 = st.columns(3)
        with sim_c1:
            in_tenure = st.slider("Tenure (Months):", min_value=1, max_value=72, value=8)
            in_monthly = st.slider("Monthly Charges ($):", min_value=18.0, max_value=160.0, value=85.0, step=1.0)
            in_tickets = st.slider("Support Tickets Opened:", min_value=0, max_value=10, value=3)

        with sim_c2:
            in_contract = st.selectbox("Contract Type:", ["Month-to-month", "One year", "Two year"], index=0)
            in_internet = st.selectbox("Internet Service:", ["Fiber", "DSL", "None"], index=0)

        with sim_c3:
            in_tech_support = st.selectbox("Tech Support Active:", ["No", "Yes"], index=0)
            in_payment = st.selectbox(
                "Payment Method:",
                ["Electronic check", "Bank transfer", "Credit card", "Mailed check"],
                index=0,
            )

        # Real-time inference
        input_data = pd.DataFrame([
            {
                "tenure_months": in_tenure,
                "monthly_charges": in_monthly,
                "support_tickets": in_tickets,
                "contract": in_contract,
                "internet_service": in_internet,
                "tech_support": in_tech_support,
                "payment_method": in_payment,
            }
        ])

        churn_prob = rf_pipe.predict_proba(input_data)[0, 1]
        churn_pct = churn_prob * 100

        st.markdown("<br>", unsafe_allow_html=True)
        res_col1, res_col2 = st.columns([1, 1.2])

        with res_col1:
            st.markdown(
                f"""
                <div class="card-box" style="text-align:center; border: 2px solid {'#ff7a90' if churn_pct >= 50 else '#3ee0b2'};">
                    <h3 style="margin:0; color:#eef2f7;">Predicted Churn Risk</h3>
                    <div style="font-size: 3.2rem; font-weight: 800; font-family:'Space Grotesk'; color: {'#ff7a90' if churn_pct >= 50 else '#3ee0b2'}; margin: 10px 0;">
                        {churn_pct:.1f}%
                    </div>
                    <p style="font-size:1.05rem; font-weight:600; color:{'#ff7a90' if churn_pct >= 50 else '#3ee0b2'}; margin-bottom:4px;">
                        {'🚨 HIGH CHURN RISK' if churn_pct >= 50 else '✅ LOW RETENTION RISK'}
                    </p>
                    <span style="font-size:0.85rem; color:#94a3b8;">Threshold: 0.50 | Model: Random Forest (250 Trees)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with res_col2:
            st.markdown(
                f"""
                <div class="card-box">
                    <h4 style="color:#7aa2ff; margin-top:0;">🤖 Prescriptive AI Recommendation</h4>
                    <p style="color:#cbd5e1; line-height:1.6;">
                        {'<b>Urgent Intervention Required:</b> High monthly charges combined with month-to-month contracts and open support tickets elevate churn likelihood. Recommend assigning priority tech support ticket resolution and offering an annual contract discount lock.' if churn_pct >= 50 else '<b>Stable Customer:</b> The customer displays strong retention signals (longer tenure / multi-year commitment). Recommend loyalty rewards or cross-sell opportunities.'}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ROC Curve & Feature Importance
    tab1, tab2, tab3 = st.tabs(["📈 ROC Curve & AUC", "🎯 Feature Importance", "🔢 Confusion Matrix"])

    with tab1:
        fpr_rf, tpr_rf, _ = roc_curve(models_bundle["y_test"], models_bundle["rf_proba"])
        fpr_lr, tpr_lr, _ = roc_curve(models_bundle["y_test"], models_bundle["lr_proba"])

        fig_roc = go.Figure()
        fig_roc.add_trace(
            go.Scatter(
                x=fpr_rf,
                y=tpr_rf,
                mode="lines",
                name=f"Random Forest (AUC = {models_bundle['rf_auc']:.3f})",
                line=dict(color="#3ee0b2", width=3),
            )
        )
        fig_roc.add_trace(
            go.Scatter(
                x=fpr_lr,
                y=tpr_lr,
                mode="lines",
                name=f"Logistic Regression (AUC = {models_bundle['lr_auc']:.3f})",
                line=dict(color="#7aa2ff", width=2, dash="dash"),
            )
        )
        fig_roc.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                name="Random Guess",
                line=dict(color="#64748b", width=1, dash="dot"),
            )
        )
        fig_roc.update_layout(
            title="Receiver Operating Characteristic (ROC) Comparison",
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            template="plotly_dark",
            paper_bgcolor="#10151f",
            plot_bgcolor="#10151f",
        )
        st.plotly_chart(fig_roc, use_container_width=True)

    with tab2:
        prep_step = rf_pipe.named_steps["prep"]
        encoded_names = prep_step.get_feature_names_out()
        rf_model = rf_pipe.named_steps["model"]
        importances = rf_model.feature_importances_

        feat_df = (
            pd.DataFrame({"Feature": encoded_names, "Importance": importances})
            .sort_values("Importance", ascending=True)
            .tail(8)
        )
        feat_df["Feature"] = (
            feat_df["Feature"]
            .str.replace("num__", "")
            .str.replace("cat__", "")
            .str.replace("_", " ")
        )

        fig_feat = px.bar(
            feat_df,
            x="Importance",
            y="Feature",
            orientation="h",
            title="Top Drivers Influencing Customer Churn",
            color="Importance",
            color_continuous_scale=["#1e3a8a", "#3ee0b2"],
        )
        fig_feat.update_layout(
            template="plotly_dark",
            paper_bgcolor="#10151f",
            plot_bgcolor="#10151f",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_feat, use_container_width=True)

    with tab3:
        y_pred_rf = (models_bundle["rf_proba"] >= 0.5).astype(int)
        cm = confusion_matrix(models_bundle["y_test"], y_pred_rf)
        cm_df = pd.DataFrame(
            cm,
            index=["Actual Retained", "Actual Churned"],
            columns=["Predicted Retained", "Predicted Churned"],
        )
        fig_cm = px.imshow(
            cm_df,
            text_auto=True,
            color_continuous_scale="Viridis",
            title="Confusion Matrix (Classification Threshold = 0.50)",
        )
        fig_cm.update_layout(
            template="plotly_dark",
            paper_bgcolor="#10151f",
            plot_bgcolor="#10151f",
        )
        st.plotly_chart(fig_cm, use_container_width=True)


# ==========================================
# PAGE 4: EXPERIENCE & EDUCATION
# ==========================================
elif menu_choice == "💼 Experience & Education":
    st.markdown("## 💼 Work Experience & Academic Background")

    exp_col, edu_col = st.columns([1.1, 0.9])

    with exp_col:
        st.markdown("### 🏢 Professional Experience")

        st.markdown(
            """
            <div class="card-box">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <h4 style="margin:0; color:#3ee0b2;">Data Analyst</h4>
                        <strong style="color:#ffffff;">Kantar · Bangalore</strong>
                    </div>
                    <span class="tag-badge tag-green">Dec 2024 – Present</span>
                </div>
                <p style="color:#cbd5e1; margin-top:12px; font-size:0.95rem; line-height:1.65;">
                    Leading predictive analytics, demand forecasting, and Marketing Mix Modelling (MROI) for global enterprise clients:
                </p>
                <ul style="color:#94a3b8; font-size:0.9rem; line-height:1.7;">
                    <li><b>Shell Product Demand Forecasting:</b> Built end-to-end models on 2–3 years of history to forecast 1–2 year demand with macroeconomic indicators (CPI, GDP, lag &amp; trend features).</li>
                    <li><b>Marketing Mix Modelling (MROI):</b> Modeled price elasticity, media adstock carryover, saturation curves, and GRPs to optimize client marketing budget allocation.</li>
                    <li><b>Brand Driver Analysis:</b> Trained Random Forest models on consumer imagery &amp; familiarity to quantify competitive differentiation drivers.</li>
                    <li><b>Advanced Automation:</b> Streamlined ETL pipelines with Python, SQL, Power Query, and Excel models.</li>
                </ul>
            </div>
            
            <div class="card-box">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <h4 style="margin:0; color:#7aa2ff;">WBL Intern — AI/ML &amp; Python</h4>
                        <strong style="color:#ffffff;">NIELIT Muzaffarpur</strong>
                    </div>
                    <span class="tag-badge">Sep 2023 – Mar 2024</span>
                </div>
                <p style="color:#94a3b8; margin-top:10px; font-size:0.9rem; line-height:1.6;">
                    Implemented core ML algorithms in Python: Linear Regression, Logistic Regression, K-Means Clustering, and Decision Trees on structured datasets.
                </p>
            </div>
            
            <div class="card-box">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <h4 style="margin:0; color:#e8c07a;">Web Development Intern</h4>
                        <strong style="color:#ffffff;">IIT Bhubaneswar</strong>
                    </div>
                    <span class="tag-badge tag-gold">Jul 2022 – Aug 2022</span>
                </div>
                <p style="color:#94a3b8; margin-top:10px; font-size:0.9rem; line-height:1.6;">
                    Built a real-time responsive weather application using JavaScript, Node.js, and SQL backend.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with edu_col:
        st.markdown("### 🎓 Education & Certifications")

        st.markdown(
            """
            <div class="card-box">
                <h4 style="margin:0; color:#3ee0b2;">PG Diploma in Big Data Analytics</h4>
                <strong style="color:#ffffff;">CDAC Bengaluru</strong>
                <div style="color:#94a3b8; font-size:0.85rem; margin-top:4px;">Mar 2024 – Aug 2024 · Score: <b>70%</b></div>
                <p style="color:#cbd5e1; font-size:0.9rem; margin-top:8px;">
                    Comprehensive training in Hadoop, PySpark, Python ML, Big Data Architecture, NoSQL, and statistical modeling.
                </p>
            </div>
            
            <div class="card-box">
                <h4 style="margin:0; color:#7aa2ff;">B.Tech in Computer Science &amp; Engineering</h4>
                <strong style="color:#ffffff;">Sitamarhi Institute of Technology</strong>
                <div style="color:#94a3b8; font-size:0.85rem; margin-top:4px;">2020 – 2023 · CGPA: <b>8.45</b></div>
                <p style="color:#cbd5e1; font-size:0.9rem; margin-top:8px;">
                    Focus on Data Structures, Algorithms, Database Management Systems (DBMS), and Software Engineering.
                </p>
            </div>
            
            <div class="card-box">
                <h4 style="margin:0; color:#e8c07a;">Diploma in Computer Science &amp; Engineering</h4>
                <strong style="color:#ffffff;">Government Polytechnic Muzaffarpur</strong>
                <div style="color:#94a3b8; font-size:0.85rem; margin-top:4px;">2017 – 2020 · CGPA: <b>8.37</b></div>
            </div>
            
            <div class="card-box">
                <h4 style="margin:0; color:#ff7a90;">📜 Verified Certifications</h4>
                <ul style="color:#94a3b8; font-size:0.88rem; line-height:1.7; margin-top:8px;">
                    <li>🏆 <b>HackerRank:</b> SQL Certified &amp; Python Certified</li>
                    <li>🏆 <b>IIT Bombay Spoken Tutorial:</b> Advanced SQL</li>
                    <li>🏆 <b>NPTEL:</b> Internet of Things (IoT)</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================
# PAGE 5: FEATURED PROJECTS
# ==========================================
elif menu_choice == "🚀 Featured Projects":
    st.markdown("## 🚀 Selected Data Science & Machine Learning Projects")
    st.caption("A portfolio of predictive modeling, deep learning architectures, time-series forecasting, and analytics dashboards.")

    p_col1, p_col2 = st.columns(2)

    with p_col1:
        st.markdown(
            """
            <div class="card-box">
                <span class="tag-badge tag-green">Deep Learning · Cyber Security</span>
                <h3 style="color:#ffffff; margin:8px 0;">🛡️ DGA Shield AI</h3>
                <p style="color:#b0bed0; font-size:0.92rem; line-height:1.6;">
                    LSTM &amp; RNN deep learning model trained on 675K+ domain names to detect malware Domain Generation Algorithms (DGA) in real-time.
                </p>
                <div style="margin-bottom:12px;">
                    <span class="tag-badge">TensorFlow</span>
                    <span class="tag-badge">LSTM / RNN</span>
                    <span class="tag-badge">FastAPI</span>
                </div>
                <a href="https://github.com/1305artikumari/DGS-Shield-AI-" target="_blank" style="color:#3ee0b2; font-weight:600; text-decoration:none;">
                    🔗 View on GitHub →
                </a>
            </div>
            
            <div class="card-box">
                <span class="tag-badge tag-gold">Time Series · Finance</span>
                <h3 style="color:#ffffff; margin:8px 0;">📈 Stock Price Predictor</h3>
                <p style="color:#b0bed0; font-size:0.92rem; line-height:1.6;">
                    Multivariate forecasting platform for RELIANCE.NS with 45+ technical indicators, model bake-off (XGBoost vs. LSTM), and live Streamlit dashboard.
                </p>
                <div style="margin-bottom:12px;">
                    <span class="tag-badge">XGBoost</span>
                    <span class="tag-badge">LSTM</span>
                    <span class="tag-badge">Streamlit</span>
                </div>
                <a href="https://github.com/1305artikumari/multivariate-stock-predictor" target="_blank" style="color:#3ee0b2; font-weight:600; text-decoration:none;">
                    🔗 View on GitHub →
                </a>
            </div>
            
            <div class="card-box">
                <span class="tag-badge">Geospatial · Analytics</span>
                <h3 style="color:#ffffff; margin:8px 0;">🏡 Property Investment Insights</h3>
                <p style="color:#b0bed0; font-size:0.92rem; line-height:1.6;">
                    Streamlit interactive dashboard joining property listings with demographics and ZIP-level KPIs for real estate investment decisions.
                </p>
                <div style="margin-bottom:12px;">
                    <span class="tag-badge">Streamlit</span>
                    <span class="tag-badge">Pandas</span>
                    <span class="tag-badge">Fuzzy Matching</span>
                </div>
                <a href="https://github.com/1305artikumari/Property-Investment-Insights-Dashboard" target="_blank" style="color:#3ee0b2; font-weight:600; text-decoration:none;">
                    🔗 View on GitHub →
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p_col2:
        st.markdown(
            """
            <div class="card-box">
                <span class="tag-badge tag-green">Healthcare · Classification</span>
                <h3 style="color:#ffffff; margin:8px 0;">🩺 Breast Cancer Detection AI</h3>
                <p style="color:#b0bed0; font-size:0.92rem; line-height:1.6;">
                    Comparative classifier bake-off on diagnostic tumor data. Hyperparameter-tuned XGBoost achieved <b>98.24% accuracy</b> with high recall for clinical safety.
                </p>
                <div style="margin-bottom:12px;">
                    <span class="tag-badge">scikit-learn</span>
                    <span class="tag-badge">XGBoost</span>
                    <span class="tag-badge">ROC-AUC</span>
                </div>
                <a href="https://github.com/1305artikumari" target="_blank" style="color:#3ee0b2; font-weight:600; text-decoration:none;">
                    🔗 View on GitHub →
                </a>
            </div>
            
            <div class="card-box">
                <span class="tag-badge tag-gold">Finance · ML</span>
                <h3 style="color:#ffffff; margin:8px 0;">💳 Fraud Detection AI</h3>
                <p style="color:#b0bed0; font-size:0.92rem; line-height:1.6;">
                    High-risk financial transaction classifier utilizing imbalanced dataset handling (SMOTE), precision-recall threshold tuning, and feature driver explanations.
                </p>
                <div style="margin-bottom:12px;">
                    <span class="tag-badge">Python</span>
                    <span class="tag-badge">SMOTE</span>
                    <span class="tag-badge">Random Forest</span>
                </div>
                <a href="https://github.com/1305artikumari/Fraud-Detection-AI" target="_blank" style="color:#3ee0b2; font-weight:600; text-decoration:none;">
                    🔗 View on GitHub →
                </a>
            </div>
            
            <div class="card-box">
                <span class="tag-badge">Commercial · BI</span>
                <h3 style="color:#ffffff; margin:8px 0;">📊 Retail Sales &amp; RFM Dashboard</h3>
                <p style="color:#b0bed0; font-size:0.92rem; line-height:1.6;">
                    Comprehensive sales analysis pipeline uncovering seasonal demand patterns, customer churn risk, and RFM loyalty tiers.
                </p>
                <div style="margin-bottom:12px;">
                    <span class="tag-badge">Python</span>
                    <span class="tag-badge">Plotly</span>
                    <span class="tag-badge">RFM Analysis</span>
                </div>
                <span style="color:#3ee0b2; font-weight:600;">
                    ⭐ Available live in Page 2 of this app!
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================
# PAGE 6: RESUME & SKILLS MATRIX
# ==========================================
elif menu_choice == "📄 Resume & Skills Matrix":
    st.markdown("## 📄 Resume & Technical Skills Matrix")

    # Download button banner
    resume_data = get_pdf_download_link()
    if resume_data:
        st.download_button(
            label="📥 Click Here to Download Official Resume (PDF)",
            data=resume_data,
            file_name="Arti_Kumari_Resume.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    sk_c1, sk_c2 = st.columns(2)

    with sk_c1:
        st.markdown("### 🛠️ Technical Competencies")
        skills_data = [
            ("Python (pandas, NumPy, scikit-learn)", 92),
            ("Machine Learning & Classification", 90),
            ("Demand Forecasting & MROI", 88),
            ("SQL (Queries, Joins, Aggregations, ETL)", 86),
            ("Excel, Power Query & Dashboarding", 90),
            ("Deep Learning (LSTM, TensorFlow)", 80),
            ("Big Data (PySpark, Hadoop)", 75),
        ]
        for skill_name, pct in skills_data:
            st.markdown(f"**{skill_name}** ({pct}%)")
            st.progress(pct / 100)

    with sk_c2:
        st.markdown("### 🧠 Methods & Domain Focus")
        st.markdown(
            """
            <div class="card-box">
                <h4 style="color:#3ee0b2; margin-top:0;">Statistical &amp; ML Methods</h4>
                <div style="margin-bottom:14px;">
                    <span class="tag-badge tag-green">Linear Regression</span>
                    <span class="tag-badge tag-green">Logistic Regression</span>
                    <span class="tag-badge tag-green">Random Forest</span>
                    <span class="tag-badge tag-green">XGBoost</span>
                    <span class="tag-badge tag-green">Time-series / ARIMA</span>
                    <span class="tag-badge tag-green">Adstock Media Modelling</span>
                    <span class="tag-badge tag-green">RFM Segmentation</span>
                    <span class="tag-badge tag-green">ROC-AUC / Precision-Recall</span>
                </div>
                <h4 style="color:#7aa2ff;">Data &amp; BI Stack</h4>
                <div>
                    <span class="tag-badge">Python</span>
                    <span class="tag-badge">MySQL</span>
                    <span class="tag-badge">Power BI (DAX)</span>
                    <span class="tag-badge">Tableau</span>
                    <span class="tag-badge">Streamlit</span>
                    <span class="tag-badge">Matplotlib / Seaborn</span>
                    <span class="tag-badge">Plotly</span>
                    <span class="tag-badge">Excel / Google Sheets</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================
# PAGE 7: CONTACT & CONNECT
# ==========================================
elif menu_choice == "📬 Contact & Connect":
    st.markdown("## 📬 Get In Touch / Let's Talk Data Science")
    st.write("I am actively open to full-time **Data Scientist** and **Senior Data Analyst** opportunities in Bangalore or remote.")

    con_col1, con_col2 = st.columns([1, 1.1])

    with con_col1:
        st.markdown(
            """
            <div class="card-box">
                <h3 style="color:#3ee0b2; margin-top:0;">📞 Direct Contact Details</h3>
                <ul style="list-style-type:none; padding-left:0; line-height:2.2; font-size:1.02rem;">
                    <li>📍 <b>Location:</b> Bangalore, Karnataka, India</li>
                    <li>📧 <b>Email:</b> <a href="mailto:artikumari09011999@gmail.com" style="color:#3ee0b2;">artikumari09011999@gmail.com</a></li>
                    <li>📱 <b>Phone:</b> <a href="tel:+916207480825" style="color:#3ee0b2;">+91 62074 80825</a></li>
                    <li>💼 <b>LinkedIn:</b> <a href="https://www.linkedin.com/in/arti-kumari2025/" target="_blank" style="color:#7aa2ff;">linkedin.com/in/arti-kumari2025</a></li>
                    <li>🐙 <b>GitHub:</b> <a href="https://github.com/1305artikumari" target="_blank" style="color:#7aa2ff;">github.com/1305artikumari</a></li>
                    <li>🗣️ <b>Languages Known:</b> English, Hindi</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with con_col2:
        st.markdown("### 💬 Send a Direct Message")
        with st.form("contact_form"):
            user_name = st.text_input("Your Name:")
            user_email = st.text_input("Your Email:")
            user_subj = st.text_input("Subject:", value="Data Scientist Role / Opportunity")
            user_msg = st.text_area("Message:", rows=4)
            submitted = st.form_submit_button("Send Email Inquiry")

            if submitted:
                if user_name and user_email and user_msg:
                    st.success(f"Thank you {user_name}! You can also send directly to artikumari09011999@gmail.com.")
                    mailto_link = f"mailto:artikumari09011999@gmail.com?subject={user_subj}&body=From:%20{user_name}%20({user_email})%0A%0A{user_msg}"
                    st.markdown(f"[👉 Click here to open in your default mail app]({mailto_link})")
                else:
                    st.warning("Please fill in all fields before sending.")
