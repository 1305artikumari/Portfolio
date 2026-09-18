"""
Customer Churn Prediction
Data Scientist case study

Stack: Python, pandas, scikit-learn
Question: Which customers are likely to leave, and which signals should trigger intervention?
"""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from generate_exports import run_data_scientist, setup_style


if __name__ == "__main__":
    setup_style()
    result = run_data_scientist()
    print(result["title"])
    print(f"Best model: {result['best_model']}")
    for key, value in result["kpis"].items():
        print(f"  {key}: {value}")
    print("\nModel comparison")
    for name, scores in result["models"].items():
        print(f"  {name}: AUC={scores['auc']:.3f}  F1={scores['f1']:.3f}")
    print("\nInsights")
    for insight in result["insights"]:
        print(f"  - {insight}")
