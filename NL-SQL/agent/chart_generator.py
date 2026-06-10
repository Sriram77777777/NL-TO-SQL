import pandas as pd
import plotly.express as px


def detect_chart_type(question: str, df: pd.DataFrame):
    """
    Detect best chart type based on user question
    and dataframe structure.
    """

    q = question.lower()

    # Trend queries
    if any(
        word in q
        for word in [
            "trend",
            "monthly",
            "daily",
            "yearly",
            "over time",
            "growth",
            "timeline"
        ]
    ):
        return "line"

    # Share queries
    if any(
        word in q
        for word in [
            "share",
            "distribution",
            "percentage",
            "contribution",
            "split",
            "ratio"
        ]
    ):
        return "pie"

    # Relationship queries
    if any(
        word in q
        for word in [
            "relationship",
            "correlation",
            "impact",
            "compare two variables"
        ]
    ):
        return "scatter"

    # Ranking queries
    if any(
        word in q
        for word in [
            "top",
            "highest",
            "lowest",
            "best",
            "worst",
            "rank"
        ]
    ):
        return "horizontal_bar"

    return "bar"


def create_chart(df: pd.DataFrame, question: str):
    """
    Generate chart from query results.
    """

    if df is None:
        return None

    if df.empty:
        return None

    if len(df.columns) < 2:
        return None

    chart_type = detect_chart_type(question, df)

    numeric_cols = (
        df.select_dtypes(include="number")
        .columns
        .tolist()
    )

    non_numeric_cols = (
        df.select_dtypes(exclude="number")
        .columns
        .tolist()
    )

    if not numeric_cols:
        return None

    y_col = numeric_cols[0]

    if non_numeric_cols:
        x_col = non_numeric_cols[0]
    else:
        x_col = df.columns[0]

    title = (
        f"{y_col.replace('_', ' ').title()} "
        f"by "
        f"{x_col.replace('_', ' ').title()}"
    )

    # --------------------------
    # LINE CHART
    # --------------------------

    if chart_type == "line":

        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            title=title,
            markers=True,
            template="plotly_white"
        )

        fig.update_traces(line_shape="spline", line=dict(width=3), marker=dict(size=8))

        fig.update_layout(
            hovermode="x unified"
        )

    # --------------------------
    # PIE CHART
    # --------------------------

    elif chart_type == "pie":

        unique_values = df[x_col].nunique()

        # Too many categories -> use bar chart
        if unique_values > 8:

            fig = px.bar(
                df,
                x=x_col,
                y=y_col,
                color=x_col,
                title=title,
                template="plotly_white"
            )

        else:

            fig = px.pie(
                df,
                names=x_col,
                values=y_col,
                title=title,
                hole=0.4,
                template="plotly_white"
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent+label"
            )

    # --------------------------
    # SCATTER CHART
    # --------------------------

    elif chart_type == "scatter":

        if len(numeric_cols) >= 2:

            fig = px.scatter(
                df,
                x=numeric_cols[0],
                y=numeric_cols[1],
                color=x_col,
                title=(
                    f"{numeric_cols[1]} "
                    f"vs "
                    f"{numeric_cols[0]}"
                ),
                template="plotly_white"
            )
            fig.update_traces(marker=dict(size=12, line=dict(width=1, color='White')), opacity=0.8)

        else:

            fig = px.bar(
                df,
                x=x_col,
                y=y_col,
                color=x_col,
                title=title,
                template="plotly_white"
            )

    # --------------------------
    # HORIZONTAL BAR CHART
    # --------------------------

    elif chart_type == "horizontal_bar":

        fig = px.bar(
            df,
            x=y_col,
            y=x_col,
            color=x_col,
            orientation="h",
            title=title,
            template="plotly_white"
        )

    # --------------------------
    # STANDARD BAR CHART
    # --------------------------

    else:

        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=x_col,
            title=title,
            template="plotly_white"
        )

    # --------------------------
    # COMMON STYLING
    # --------------------------

    fig.update_layout(
        font=dict(
            family="Arial",
            size=12
        ),
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        ),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig


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
                60000,
                55000
            ]
        }
    )

    fig = create_chart(
        sample_df,
        "Top departments by salary"
    )

    fig.show()