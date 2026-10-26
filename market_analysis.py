import pandas as pd

# Market structure metrics
df = pd.read_csv("data/uk_top50_clean.csv")

# Split artist credits using the assignment's '&' delimiter
artist_rows = []
for _, row in df.iterrows():
    for artist in str(row["artist"]).split("&"):
        artist = artist.strip()
        if artist:
            artist_rows.append(artist)

artist_counts = pd.Series(artist_rows).value_counts()
artist_shares = artist_counts / artist_counts.sum()

# HHI is a concentration measure. Higher values mean more concentration.
hhi = (artist_shares ** 2).sum()

# Top 5 concentration uses playlist entries as the denominator.
top5_share = artist_counts.head(5).sum() / len(df)

# Diversity score used here: average unique artists per day divided by 50 entries.
unique_per_day = df.groupby("date")["artist"].nunique().mean()
diversity_score = unique_per_day / 50

# Content variety index: unique raw artist labels per 100 playlist entries.
content_variety = df["artist"].nunique() / len(df) * 100

results = {
    "Artist Concentration Index (HHI)": hhi,
    "Top 5 Artist Share": top5_share,
    "Average Unique Artists per Day": unique_per_day,
    "Diversity Score": diversity_score,
    "Collaboration Ratio": df["is_collaboration"].mean(),
    "Explicit Content Share": df["is_explicit"].mean(),
    "Single Ratio": (df["album_type"] == "single").mean(),
    "Album Ratio": (df["album_type"] == "album").mean(),
    "Content Variety Index": content_variety
}

for name, value in results.items():
    print(f"{name}: {value:.4f}")
