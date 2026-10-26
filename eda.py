import pandas as pd

# Load the UK Top 50 data
df = pd.read_csv("data/Atlantic_United_Kingdom.csv")

print("Dataset loaded successfully!")
print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nExact duplicate rows:")
print(df.duplicated().sum())

# Convert date into a real date
df["date"] = pd.to_datetime(df["date"], dayfirst=True)

# Remove exact duplicate rows
df = df.drop_duplicates()

# A daily Top 50 should have one row for each position.
# If the same date-position occurs twice, keep the first record.
df = df.sort_values(["date", "position"])
df = df.drop_duplicates(["date", "position"], keep="first")

# Simple standardization
df["artist"] = df["artist"].astype(str).str.strip()
df["song"] = df["song"].astype(str).str.strip()
df["album_type"] = df["album_type"].astype(str).str.strip().str.lower()

# Useful analysis columns
df["duration_minutes"] = df["duration_ms"] / 60000
df["is_collaboration"] = df["artist"].str.contains("&", regex=False)
df["artist_count"] = df["artist"].str.split("&").apply(len)

print("\nCleaned shape:", df.shape)
print("Unique dates:", df["date"].nunique())
print("Date range:", df["date"].min().date(), "to", df["date"].max().date())
print("\nAlbum types:")
print(df["album_type"].value_counts())
print("\nExplicit content:")
print(df["is_explicit"].value_counts())

print("\nEDA checking completed!")
