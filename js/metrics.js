window.METRICS = {
  "analyst": {
    "title": "Retail Revenue Intelligence",
    "track": "Data Analyst",
    "kpis": {
      "revenue": 3848505.3600000003,
      "orders": 35962,
      "customers": 19829,
      "aov": 107.01588788165286,
      "mom_growth": -0.08373201480451267,
      "repeat_rate": 0.5212063139845681,
      "return_rate": 0.045881764084311216,
      "top_category": "Electronics"
    },
    "insights": [
      "Electronics leads revenue mix and should stay the hero assortment.",
      "Repeat purchase rate is 52%; loyalty offers can lift mid-tier RFM segments.",
      "Weekend demand is structurally higher \u2014 shift paid media and staffing toward Friday-Sunday.",
      "At-risk customers are recoverable with win-back campaigns triggered at 45+ days of inactivity."
    ]
  },
  "scientist": {
    "title": "Customer Churn Prediction",
    "track": "Data Scientist",
    "best_model": "Logistic Regression",
    "kpis": {
      "rows": 4200,
      "churn_rate": 0.3130952380952381,
      "auc": 0.8200321235703536,
      "precision": 0.6151761517615176,
      "recall": 0.6899696048632219,
      "f1": 0.6504297994269341,
      "accuracy": 0.7676190476190476,
      "threshold": 0.35
    },
    "models": {
      "Logistic Regression": {
        "auc": 0.8200321235703536,
        "accuracy": 0.7676190476190476,
        "precision": 0.6151761517615176,
        "recall": 0.6899696048632219,
        "f1": 0.6504297994269341,
        "threshold": 0.35
      },
      "Random Forest": {
        "auc": 0.8016432766041761,
        "accuracy": 0.7657142857142857,
        "precision": 0.7128205128205128,
        "recall": 0.42249240121580545,
        "f1": 0.5305343511450382
      }
    },
    "class_report": {
      "Retained": {
        "precision": 0.8502202643171806,
        "recall": 0.8030513176144244,
        "f1-score": 0.8259629101283881,
        "support": 721.0
      },
      "Churned": {
        "precision": 0.6151761517615176,
        "recall": 0.6899696048632219,
        "f1-score": 0.6504297994269341,
        "support": 329.0
      },
      "accuracy": 0.7676190476190476,
      "macro avg": {
        "precision": 0.7326982080393492,
        "recall": 0.7465104612388231,
        "f1-score": 0.7381963547776611,
        "support": 1050.0
      },
      "weighted avg": {
        "precision": 0.7765731090497395,
        "recall": 0.7676190476190476,
        "f1-score": 0.7709625354419325,
        "support": 1050.0
      }
    },
    "insights": [
      "Month-to-month contracts and electronic-check payers are the highest-risk cohort.",
      "Tenure is protective: intervention in the first 6 months yields the largest lift.",
      "Missing tech support plus rising ticket volume is a strong early-warning signal.",
      "Logistic Regression is the production candidate; the operating threshold is tuned for F1, not the default 0.50."
    ]
  }
};
