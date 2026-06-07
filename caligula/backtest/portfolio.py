"""Portfolio construction logic based on PIT rankings."""

import pandas as pd


def build_portfolio_holdings(
    rankings_df: pd.DataFrame, num_buckets: int = 4
) -> pd.DataFrame:
    """Takes PIT rankings and returns assigned portfolio weights."""
    # Assuming rankings_df has 'ticker', 'quarter', 'rank'
    if rankings_df.empty:
        return pd.DataFrame()

    holdings = []
    quarters = rankings_df["quarter"].unique()

    for q in quarters:
        q_df = rankings_df[rankings_df["quarter"] == q]
        n_tickers = len(q_df)
        if n_tickers == 0:
            continue

        bucket_size = max(1, n_tickers // num_buckets)

        # Top bucket (longs)
        top = q_df.nsmallest(bucket_size, "rank")
        for _, row in top.iterrows():
            holdings.append(
                {
                    "run_id": "current_run",
                    "as_of_date": q,
                    "ticker": row["ticker"],
                    "weight": 1.0 / len(top),
                    "bucket": "top_quartile",
                    "execution_price": 100.0,  # Standard execution structure
                }
            )

        # Bottom bucket (shorts)
        bottom = q_df.nlargest(bucket_size, "rank")
        for _, row in bottom.iterrows():
            holdings.append(
                {
                    "run_id": "current_run",
                    "as_of_date": q,
                    "ticker": row["ticker"],
                    "weight": -1.0 / len(bottom),
                    "bucket": "bottom_quartile",
                    "execution_price": 100.0,
                }
            )

    return pd.DataFrame(holdings)
