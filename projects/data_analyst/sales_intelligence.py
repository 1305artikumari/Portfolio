"""
Retail Revenue Intelligence
Data Analyst case study

Stack: Python, pandas, seaborn, matplotlib
Question: Where is revenue coming from, who is at risk, and what should we do next?
"""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from generate_exports import run_data_analyst, setup_style


if __name__ == "__main__":
    setup_style()
    result = run_data_analyst()
    print(result["title"])
    for key, value in result["kpis"].items():
        print(f"  {key}: {value}")
    print("\nInsights")
    for insight in result["insights"]:
        print(f"  - {insight}")
