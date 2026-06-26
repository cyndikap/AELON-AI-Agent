import pandas as pd

class AnalyticsAgent:

    def compute_metrics(self, df: pd.DataFrame):

        results = {}

        # ✅ Distribution severity
        if "risk_level" in df.columns:
            results["severity_dist"] = df["risk_level"].value_counts().to_dict()

        # ✅ Error rate
        if "is_fraud" in df.columns:
            results["error_rate"] = float(df["is_fraud"].mean() * 100)

        # ✅ Top agents/service
        if "agent" in df.columns:
            top_services = (
                df["agent"].value_counts().head(3).to_dict()
            )
            results["top_services"] = top_services

        # ✅ Categories
        if "category" in df.columns:
            results["category_dist"] = df["category"].value_counts().to_dict()

        return results