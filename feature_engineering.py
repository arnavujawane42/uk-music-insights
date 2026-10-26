import pandas as pd

# Feature engineering for the UK Top 50 analysis
df = pd.read_csv("data/Atlantic_United_Kingdom.csv")
df["date"] = pd.to_datetime(df["date"], dayfirst=True)
df = df.drop_duplicates()
df = df.sort_values(["date", "position"]).drop_duplicates(["date", "position"], keep="first")

df["duration_minutes"] = df["duration_ms"] / 60000
df["is_collaboration"] = df["artist"].str.contains("&", regex=False)
df["artist_count"] = df["artist"].str.split("&").apply(len)

df["duration_group"] = pd.cut(
    df["duration_minutes"],
    bins=[0, 3, 4, 100],
    labels=["Short (<3 min)", "Medium (3-4 min)", "Long (>4 min)"]
)

# Save the cleaned analysis dataset
df.to_csv("data/uk_top50_clean.csv", index=False)
print("Clean dataset saved to data/uk_top50_clean.csv")
