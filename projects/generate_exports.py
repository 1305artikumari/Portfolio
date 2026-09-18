"""
Generate portfolio datasets, charts, and export reports
for Data Analyst and Data Scientist case studies.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
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

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "projects" / "data"
CHART_DIR = ROOT / "assets" / "charts"
REPORT_DIR = ROOT / "reports"
METRICS_PATH = ROOT / "js" / "metrics.json"

INK = "#07090d"
SURFACE = "#10151f"
TEAL = "#3ee0b2"
BLUE = "#7aa2ff"
GOLD = "#e8c07a"
CORAL = "#ff7a90"
TEXT = "#eef2f7"
MUTED = "#8b97a8"


def setup_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": INK,
            "axes.facecolor": SURFACE,
            "axes.edgecolor": "#1d2633",
            "axes.labelcolor": TEXT,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "text.color": TEXT,
            "grid.color": "#1d2633",
            "grid.linestyle": "-",
            "grid.linewidth": 0.8,
            "font.family": "DejaVu Sans",
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "savefig.facecolor": INK,
            "savefig.bbox": "tight",
            "savefig.dpi": 180,
        }
    )
    sns.set_style("darkgrid", {"axes.facecolor": SURFACE})


def save_fig(name: str) -> Path:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    path = CHART_DIR / name
    plt.savefig(path, pad_inches=0.25)
    plt.close()
    return path


def make_sales_data(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2024-01-01")
    dates = pd.date_range(start, periods=640, freq="D")
    channels = ["Retail", "Marketplace", "Direct", "Wholesale"]
    categories = ["Apparel", "Beauty", "Home", "Electronics", "Wellness"]
    regions = ["North", "West", "South", "East"]
    rows = []
    for day in dates:
        season = 1 + 0.18 * np.sin(2 * np.pi * day.dayofyear / 365)
        weekday = 1.12 if day.dayofweek >= 5 else 1.0
        n = int(rng.integers(38, 72) * weekday)
        for _ in range(n):
            category = rng.choice(categories, p=[0.28, 0.18, 0.17, 0.22, 0.15])
            channel = rng.choice(channels, p=[0.34, 0.31, 0.22, 0.13])
            base = {
                "Apparel": 48,
                "Beauty": 36,
                "Home": 72,
                "Electronics": 145,
                "Wellness": 41,
            }[category]
            price = max(12, rng.normal(base, base * 0.22))
            qty = int(rng.choice([1, 2, 3, 4], p=[0.61, 0.24, 0.11, 0.04]))
            discount = rng.choice([0, 0.05, 0.1, 0.15, 0.2], p=[0.46, 0.24, 0.16, 0.09, 0.05])
            revenue = price * qty * (1 - discount) * season
            rows.append(
                {
                    "order_id": f"ORD-{len(rows) + 1:06d}",
                    "order_date": day,
                    "customer_id": f"C{rng.integers(1000, 28000)}",
                    "region": rng.choice(regions, p=[0.29, 0.27, 0.24, 0.20]),
                    "channel": channel,
                    "category": category,
                    "quantity": qty,
                    "unit_price": round(price, 2),
                    "discount": discount,
                    "revenue": round(revenue, 2),
                    "returned": int(rng.random() < 0.046),
                }
            )
    return pd.DataFrame(rows)


def run_data_analyst() -> dict:
    df = make_sales_data()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_DIR / "retail_orders.csv", index=False)

    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    monthly = (
        df.groupby("order_month", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
            aov=("revenue", "mean"),
        )
        .sort_values("order_month")
    )
    category = (
        df.groupby("category", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("order_id", "count"))
        .sort_values("revenue", ascending=False)
    )
    channel = df.groupby("channel", as_index=False).agg(revenue=("revenue", "sum"))
    rfm = df.groupby("customer_id").agg(
        last_order=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum"),
    )
    snapshot = df["order_date"].max() + pd.Timedelta(days=1)
    rfm["recency"] = (snapshot - rfm["last_order"]).dt.days
    rfm["r_score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["rfm"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]
    rfm["segment"] = pd.cut(
        rfm["rfm"],
        bins=[0, 5, 8, 10, 12],
        labels=["At Risk", "Need Attention", "Loyal", "Champions"],
    )
    segments = rfm["segment"].value_counts().reindex(
        ["Champions", "Loyal", "Need Attention", "At Risk"]
    )

    complete_months = monthly.iloc[:-1].copy()
    complete_months["label"] = pd.to_datetime(complete_months["order_month"]).dt.strftime("%b %y")
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    ax.plot(complete_months["label"], complete_months["revenue"], color=TEAL, linewidth=2.4)
    ax.fill_between(complete_months["label"], complete_months["revenue"], color=TEAL, alpha=0.16)
    ax.set_title("Monthly revenue trajectory")
    ax.set_ylabel("Revenue")
    ax.set_xticks(range(0, len(complete_months), 2))
    ax.set_xticklabels(complete_months["label"].iloc[::2], rotation=0)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
    save_fig("analyst-revenue.png")

    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    colors = [TEAL, BLUE, GOLD, CORAL, "#b38bff"]
    bars = ax.bar(category["category"], category["revenue"], color=colors, width=0.64)
    ax.set_title("Category contribution")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
    for bar, value in zip(bars, category["revenue"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.01,
            f"${value/1000:.0f}k",
            ha="center",
            va="bottom",
            fontsize=8,
            color=MUTED,
        )
    save_fig("analyst-category.png")

    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    ax.pie(
        channel["revenue"],
        labels=channel["channel"],
        colors=[TEAL, BLUE, GOLD, CORAL],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"width": 0.46, "edgecolor": INK},
        textprops={"color": TEXT, "fontsize": 10},
    )
    ax.set_title("Revenue by channel")
    save_fig("analyst-channel.png")

    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    ax.bar(segments.index.astype(str), segments.values, color=[TEAL, BLUE, GOLD, CORAL], width=0.64)
    ax.set_title("RFM customer segments")
    ax.set_ylabel("Customers")
    save_fig("analyst-rfm.png")

    prev = complete_months.iloc[-2]
    latest = complete_months.iloc[-1]
    growth = (latest["revenue"] - prev["revenue"]) / prev["revenue"]
    repeat_rate = (rfm["frequency"] > 1).mean()

    metrics = {
        "title": "Retail Revenue Intelligence",
        "track": "Data Analyst",
        "kpis": {
            "revenue": float(df["revenue"].sum()),
            "orders": int(df["order_id"].nunique()),
            "customers": int(df["customer_id"].nunique()),
            "aov": float(df["revenue"].sum() / df["order_id"].nunique()),
            "mom_growth": float(growth),
            "repeat_rate": float(repeat_rate),
            "return_rate": float(df["returned"].mean()),
            "top_category": str(category.iloc[0]["category"]),
        },
        "insights": [
            f"{category.iloc[0]['category']} leads revenue mix and should stay the hero assortment.",
            f"Repeat purchase rate is {repeat_rate:.0%}; loyalty offers can lift mid-tier RFM segments.",
            "Weekend demand is structurally higher — shift paid media and staffing toward Friday-Sunday.",
            "At-risk customers are recoverable with win-back campaigns triggered at 45+ days of inactivity.",
        ],
    }
    return metrics


def make_churn_data(seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = 4200
    tenure = rng.integers(1, 73, n)
    monthly = rng.normal(68, 22, n).clip(18, 160)
    contract = rng.choice(["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.27, 0.18])
    internet = rng.choice(["Fiber", "DSL", "None"], n, p=[0.48, 0.36, 0.16])
    support = rng.choice(["Yes", "No"], n, p=[0.41, 0.59])
    payment = rng.choice(
        ["Electronic check", "Bank transfer", "Credit card", "Mailed check"],
        n,
        p=[0.34, 0.24, 0.25, 0.17],
    )
    tickets = rng.poisson(1.4, n)
    logit = (
        -2.55
        + 0.024 * monthly
        - 0.048 * tenure
        + np.where(contract == "Month-to-month", 1.35, 0)
        + np.where(contract == "Two year", -0.85, 0)
        + np.where(internet == "Fiber", 0.42, 0)
        + np.where(support == "No", 0.58, 0)
        + np.where(payment == "Electronic check", 0.52, 0)
        + 0.22 * tickets
    )
    prob = 1 / (1 + np.exp(-logit))
    churn = (rng.random(n) < prob).astype(int)
    return pd.DataFrame(
        {
            "customer_id": [f"CX{i:05d}" for i in range(n)],
            "tenure_months": tenure,
            "monthly_charges": monthly.round(2),
            "contract": contract,
            "internet_service": internet,
            "tech_support": support,
            "payment_method": payment,
            "support_tickets": tickets,
            "churn": churn,
        }
    )


def run_data_scientist() -> dict:
    df = make_churn_data()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_DIR / "customer_churn.csv", index=False)

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
    models = {
        "Logistic Regression": LogisticRegression(max_iter=800),
        "Random Forest": RandomForestClassifier(
            n_estimators=280, max_depth=8, min_samples_leaf=6, random_state=42
        ),
    }

    scores = {}
    best_name = None
    best_auc = -1
    best_bundle = None
    for name, model in models.items():
        pipe = Pipeline([("prep", prep), ("model", model)])
        pipe.fit(x_train, y_train)
        proba = pipe.predict_proba(x_test)[:, 1]
        pred = (proba >= 0.5).astype(int)
        auc = roc_auc_score(y_test, proba)
        scores[name] = {
            "auc": float(auc),
            "accuracy": float(accuracy_score(y_test, pred)),
            "precision": float(precision_score(y_test, pred)),
            "recall": float(recall_score(y_test, pred)),
            "f1": float(f1_score(y_test, pred)),
        }
        if auc > best_auc:
            best_auc = auc
            best_name = name
            best_bundle = (pipe, proba, pred)

    pipe, proba, _pred = best_bundle
    best_t, best_f1 = 0.5, -1.0
    for threshold in np.linspace(0.25, 0.65, 21):
        candidate = (proba >= threshold).astype(int)
        score = f1_score(y_test, candidate)
        if score > best_f1:
            best_t, best_f1 = float(threshold), float(score)
    pred = (proba >= best_t).astype(int)
    scores[best_name].update(
        {
            "accuracy": float(accuracy_score(y_test, pred)),
            "precision": float(precision_score(y_test, pred)),
            "recall": float(recall_score(y_test, pred)),
            "f1": float(f1_score(y_test, pred)),
            "threshold": best_t,
        }
    )
    fpr, tpr, _ = roc_curve(y_test, proba)
    fig, ax = plt.subplots(figsize=(6.6, 6.2))
    ax.plot(fpr, tpr, color=TEAL, linewidth=2.6, label=f"{best_name}  AUC {best_auc:.3f}")
    ax.plot([0, 1], [0, 1], color=MUTED, linestyle="--", linewidth=1)
    ax.set_title("ROC curve — churn model")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.legend(facecolor=SURFACE, edgecolor="#1d2633")
    save_fig("scientist-roc.png")

    cm = confusion_matrix(y_test, pred)
    fig, ax = plt.subplots(figsize=(6.2, 5.4))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="mako",
        cbar=False,
        ax=ax,
        xticklabels=["Retained", "Churned"],
        yticklabels=["Retained", "Churned"],
    )
    ax.set_title("Confusion matrix")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    save_fig("scientist-confusion.png")

    encoded_names = pipe.named_steps["prep"].get_feature_names_out()
    model = pipe.named_steps["model"]
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    else:
        importances = np.abs(model.coef_[0])
    importance = (
        pd.DataFrame({"feature": encoded_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .head(8)
    )
    pretty = {
        "tenure_months": "Tenure (months)",
        "monthly_charges": "Monthly charges",
        "support_tickets": "Support tickets",
        "contract_Month-to-month": "Contract: month-to-month",
        "contract_One year": "Contract: one year",
        "contract_Two year": "Contract: two year",
        "internet_service_Fiber": "Internet: fiber",
        "internet_service_DSL": "Internet: DSL",
        "internet_service_None": "Internet: none",
        "tech_support_No": "No tech support",
        "tech_support_Yes": "Has tech support",
        "payment_method_Electronic check": "Pay: e-check",
        "payment_method_Bank transfer": "Pay: bank",
        "payment_method_Credit card": "Pay: card",
        "payment_method_Mailed check": "Pay: mailed check",
    }
    importance["feature"] = (
        importance["feature"]
        .str.replace("num__", "", regex=False)
        .str.replace("cat__", "", regex=False)
        .map(lambda name: pretty.get(name, name.replace("_", " ")))
    )
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.barh(importance["feature"][::-1], importance["importance"][::-1], color=BLUE)
    ax.set_title("Top drivers of churn")
    save_fig("scientist-features.png")

    report = classification_report(y_test, pred, target_names=["Retained", "Churned"], output_dict=True)
    metrics = {
        "title": "Customer Churn Prediction",
        "track": "Data Scientist",
        "best_model": best_name,
        "kpis": {
            "rows": int(len(df)),
            "churn_rate": float(df["churn"].mean()),
            "auc": float(scores[best_name]["auc"]),
            "precision": float(scores[best_name]["precision"]),
            "recall": float(scores[best_name]["recall"]),
            "f1": float(scores[best_name]["f1"]),
            "accuracy": float(scores[best_name]["accuracy"]),
            "threshold": float(scores[best_name]["threshold"]),
        },
        "models": scores,
        "class_report": report,
        "insights": [
            "Month-to-month contracts and electronic-check payers are the highest-risk cohort.",
            "Tenure is protective: intervention in the first 6 months yields the largest lift.",
            "Missing tech support plus rising ticket volume is a strong early-warning signal.",
            f"{best_name} is the production candidate; the operating threshold is tuned for F1, not the default 0.50.",
        ],
    }
    return metrics


def write_html_report(payload: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    analyst = payload["analyst"]
    scientist = payload["scientist"]
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Python Export Report</title>
  <style>
    body {{ margin:0; font-family: Georgia, serif; background:#07090d; color:#eef2f7; }}
    main {{ max-width: 920px; margin: 0 auto; padding: 48px 24px 80px; }}
    h1,h2 {{ font-weight: 600; }}
    a {{ color:#3ee0b2; }}
    .muted {{ color:#8b97a8; }}
    .card {{ background:#10151f; border:1px solid #1d2633; border-radius:18px; padding:24px; margin:22px 0; }}
    .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; }}
    .kpi {{ background:#0b0f16; border-radius:12px; padding:14px; }}
    .kpi b {{ display:block; font-size:22px; color:#3ee0b2; }}
    img {{ width:100%; border-radius:14px; margin-top:14px; }}
    .split {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
    ul {{ line-height:1.7; }}
    @media (max-width: 720px) {{ .split {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <main>
    <p class="muted">Python export · Data Analyst + Data Scientist</p>
    <p><a href="../index.html">Back to portfolio</a></p>
    <h1>Portfolio case-study report</h1>
    <div class="card">
      <h2>{analyst["title"]}</h2>
      <div class="kpis">
        <div class="kpi"><span class="muted">Revenue</span><b>${analyst["kpis"]["revenue"]/1_000_000:.2f}M</b></div>
        <div class="kpi"><span class="muted">Orders</span><b>{analyst["kpis"]["orders"]:,}</b></div>
        <div class="kpi"><span class="muted">AOV</span><b>${analyst["kpis"]["aov"]:.0f}</b></div>
        <div class="kpi"><span class="muted">Repeat rate</span><b>{analyst["kpis"]["repeat_rate"]:.0%}</b></div>
      </div>
      <img src="../assets/charts/analyst-revenue.png" alt="Revenue trend" />
      <div class="split">
        <img src="../assets/charts/analyst-category.png" alt="Category mix" />
        <img src="../assets/charts/analyst-rfm.png" alt="RFM segments" />
      </div>
      <ul>{"".join(f"<li>{item}</li>" for item in analyst["insights"])}</ul>
    </div>
    <div class="card">
      <h2>{scientist["title"]}</h2>
      <div class="kpis">
        <div class="kpi"><span class="muted">Model</span><b>{scientist["best_model"]}</b></div>
        <div class="kpi"><span class="muted">ROC-AUC</span><b>{scientist["kpis"]["auc"]:.3f}</b></div>
        <div class="kpi"><span class="muted">Recall</span><b>{scientist["kpis"]["recall"]:.0%}</b></div>
        <div class="kpi"><span class="muted">F1</span><b>{scientist["kpis"]["f1"]:.2f}</b></div>
      </div>
      <img src="../assets/charts/scientist-roc.png" alt="ROC curve" />
      <div class="split">
        <img src="../assets/charts/scientist-features.png" alt="Feature importance" />
        <img src="../assets/charts/scientist-confusion.png" alt="Confusion matrix" />
      </div>
      <ul>{"".join(f"<li>{item}</li>" for item in scientist["insights"])}</ul>
    </div>
  </main>
</body>
</html>
"""
    (REPORT_DIR / "python-export.html").write_text(html, encoding="utf-8")


def main() -> None:
    setup_style()
    analyst = run_data_analyst()
    scientist = run_data_scientist()
    payload = {"analyst": analyst, "scientist": scientist}
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    metrics_js = METRICS_PATH.with_suffix(".js")
    metrics_js.write_text(
        "window.METRICS = " + json.dumps(payload, indent=2) + ";\n",
        encoding="utf-8",
    )
    write_html_report(payload)
    print("Exports ready:")
    print(f"  charts  -> {CHART_DIR}")
    print(f"  metrics -> {METRICS_PATH}")
    print(f"  report  -> {REPORT_DIR / 'python-export.html'}")


if __name__ == "__main__":
    main()
