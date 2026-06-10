import pandas as pd
import numpy as np


def generate_insights(df: pd.DataFrame):
    """
    Generate smart insights from query results.

    Parameters:
        df (pd.DataFrame)

    Returns:
        list[str]
    """

    insights = []

    if df is None or df.empty:
        return insights

    # Numeric columns
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    # Non-numeric columns
    categorical_cols = [
        col for col in df.columns
        if col not in numeric_cols
    ]

    if not numeric_cols:
        insights.append(
            "No numeric columns found for insight generation."
        )
        return insights

    value_col = numeric_cols[0]

    # ------------------------------------
    # Average
    # ------------------------------------

    avg_value = df[value_col].mean()

    insights.append(
        f"Average {value_col.replace('_', ' ')} is {avg_value:,.2f}"
    )

    # ------------------------------------
    # Top Performer
    # ------------------------------------

    if categorical_cols and len(df) > 1:

        category_col = categorical_cols[0]

        top_row = df.loc[
            df[value_col].idxmax()
        ]

        insights.append(
            f"Top performer is "
            f"{top_row[category_col]} "
            f"with {top_row[value_col]:,.2f}"
        )

    # ------------------------------------
    # Lowest Performer
    # ------------------------------------

    if categorical_cols and len(df) > 1:

        category_col = categorical_cols[0]

        low_row = df.loc[
            df[value_col].idxmin()
        ]

        insights.append(
            f"Lowest performer is "
            f"{low_row[category_col]} "
            f"with {low_row[value_col]:,.2f}"
        )

    # ------------------------------------
    # Contribution %
    # ------------------------------------

    total = df[value_col].sum()

    if (
        total > 0
        and categorical_cols
        and len(df) > 1
    ):

        category_col = categorical_cols[0]

        top_row = df.loc[
            df[value_col].idxmax()
        ]

        contribution = (
            top_row[value_col] / total
        ) * 100

        insights.append(
            f"{top_row[category_col]} contributes "
            f"{contribution:.1f}% of the total."
        )

    # ------------------------------------
    # Outlier Detection
    # ------------------------------------

    if len(df) >= 5:

        mean_val = df[value_col].mean()
        std_val = df[value_col].std()

        if std_val > 0:

            outliers = df[
                abs(
                    df[value_col] - mean_val
                ) > (2 * std_val)
            ]

            if not outliers.empty:

                insights.append(
                    f"{len(outliers)} potential outlier(s) detected."
                )

    # ------------------------------------
    # Trend Detection
    # ------------------------------------

    if len(df) >= 3:

        try:

            first_value = df[value_col].iloc[0]
            last_value = df[value_col].iloc[-1]

            if first_value != 0:

                if last_value > first_value:

                    growth = (
                        (last_value - first_value)
                        / first_value
                    ) * 100

                    insights.append(
                        f"Overall trend increased by "
                        f"{growth:.1f}%."
                    )

                elif last_value < first_value:

                    decline = (
                        (first_value - last_value)
                        / first_value
                    ) * 100

                    insights.append(
                        f"Overall trend decreased by "
                        f"{decline:.1f}%."
                    )

        except Exception:
            pass

    # ------------------------------------
    # Maximum
    # ------------------------------------

    max_value = df[value_col].max()

    insights.append(
        f"Maximum observed {value_col.replace('_', ' ')} "
        f"is {max_value:,.2f}"
    )

    # ------------------------------------
    # Minimum
    # ------------------------------------

    min_value = df[value_col].min()

    insights.append(
        f"Minimum observed {value_col.replace('_', ' ')} "
        f"is {min_value:,.2f}"
    )

    return insights


if __name__ == "__main__":

    sample_df = pd.DataFrame(
        {
            "Department": [
                "IT",
                "HR",
                "Sales",
                "Finance"
            ],
            "Salary": [
                50000,
                45000,
                70000,
                55000
            ]
        }
    )

    results = generate_insights(sample_df)

    for item in results:
        print("•", item)