import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv("data/uk_top50_clean.csv")

# Keep only tracks where '&' appears in the artist field
collabs = df[df["is_collaboration"]].copy()

print("Collaboration ratio:", round(len(collabs) / len(df) * 100, 2), "%")
print("Average artists per song:", round(df["artist_count"].mean(), 2))
print("Top 10 collaboration ratio:", round(df.loc[df["position"] <= 10, "is_collaboration"].mean() * 100, 2), "%")

# Build a simple artist-to-artist network
G = nx.Graph()
for text in collabs["artist"]:
    artists = [a.strip() for a in text.split("&") if a.strip()]
    for artist in artists:
        G.add_node(artist)
    for i in range(len(artists)):
        for j in range(i + 1, len(artists)):
            if G.has_edge(artists[i], artists[j]):
                G[artists[i]][artists[j]]["weight"] += 1
            else:
                G.add_edge(artists[i], artists[j], weight=1)

print("Network nodes:", G.number_of_nodes())
print("Network edges:", G.number_of_edges())
