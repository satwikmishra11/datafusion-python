import argparse
import pandas as pd
from scipy import stats

def detect_regressions(current: str, baseline: str = "main"):
    """Compare benchmark results against a baseline branch"""
    df_current = pd.read_json(current)
    df_baseline = pd.read_json(baseline)
    
    merged = df_current.merge(
        df_baseline, 
        on="query", 
        suffixes=("_current", "_baseline")
    )
    
    # Calculate performance delta
    merged["delta"] = merged["duration_ms_current"] / merged["duration_ms_baseline"]
    
    # Identify significant regressions (t-test p < 0.05)
    regressions = []
    for query in merged["query"].unique():
        current_times = merged[merged["query"] == query]["duration_ms_current"]
        baseline_times = merged[merged["query"] == query]["duration_ms_baseline"]
        _, p_value = stats.ttest_ind(current_times, baseline_times)
        
        if p_value < 0.05 and current_times.mean() > baseline_times.mean():
            regressions.append(query)
    
    return regressions

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", required=True)
    parser.add_argument("--baseline", default="main-results.json")
    args = parser.parse_args()
    
    regressed_queries = detect_regressions(args.current, args.baseline)
    print(f"Detected regressions in queries: {', '.join(regressed_queries)}")
