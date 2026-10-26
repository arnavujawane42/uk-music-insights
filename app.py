from pathlib import Path
from itertools import combinations

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "uk_top50_clean.csv"

st.set_page_config(
    page_title="UK Music Insights",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. CUSTOM DASHBOARD THEME
# ============================================================

st.markdown(
    r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #0b0d14;
    --panel: #151a27;
    --line: #2b3144;
    --purple: #a78bfa;
    --blue: #67c7f5;
    --muted: #a0a8bd;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            ellipse at 75% -10%,
            rgba(103, 91, 210, .18),
            transparent 38%
        ),
        #0b0d14;
    color: #f2f4fb;
}

[data-testid="stHeader"] {
    background: rgba(11, 13, 20, .75);
}

[data-testid="stSidebar"] {
    background: #0e111a;
    border-right: 1px solid var(--line);
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -.035em;
}

h1 {
    font-size: 2.4rem !important;
}

p, label {
    color: var(--muted);
}

.hero {
    padding: 1.45rem 1.6rem;
    border: 1px solid #30334a;
    border-radius: 22px;
    background: linear-gradient(
        115deg,
        rgba(119, 92, 246, .18),
        rgba(32, 128, 175, .09) 62%,
        rgba(19, 23, 34, .9)
    );
    margin-bottom: 1.1rem;
}

.eyebrow {
    text-transform: uppercase;
    letter-spacing: .16em;
    font-size: .72rem;
    font-weight: 700;
    color: #a78bfa;
    margin-bottom: .45rem;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.35rem;
    line-height: 1.1;
    font-weight: 700;
    color: #f7f7ff;
    margin: 0;
}

.hero-copy {
    color: #b8bfd2;
    max-width: 780px;
    font-size: 1rem;
    margin-top: .7rem;
    margin-bottom: 0;
}

.pill {
    display: inline-block;
    padding: .3rem .65rem;
    border: 1px solid #41425d;
    border-radius: 999px;
    color: #d8d1ff;
    font-size: .76rem;
    margin-right: .35rem;
    margin-top: .9rem;
}

.metric-card {
    background: linear-gradient(145deg, #171c2a, #111520);
    border: 1px solid #2b3144;
    border-radius: 17px;
    padding: 1rem 1.05rem;
    min-height: 119px;
}

.metric-label {
    font-size: .76rem;
    color: #aab2c8;
    font-weight: 700;
    letter-spacing: .04em;
}

.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    color: #f5f6ff;
    font-weight: 700;
    margin: .35rem 0 .1rem;
    overflow-wrap: anywhere;
}

.metric-note {
    font-size: .73rem;
    color: #8d97b0;
}

.section-head {
    display: flex;
    align-items: center;
    gap: .65rem;
    margin: .6rem 0 .25rem;
}

.section-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #a78bfa;
    display: inline-block;
    box-shadow: 0 0 14px rgba(167, 139, 250, .7);
}

.insight {
    padding: .9rem 1rem;
    background: #141a27;
    border: 1px solid #2b3245;
    border-left: 3px solid #a78bfa;
    border-radius: 10px;
    color: #dce1f2;
}

.small-muted {
    font-size: .82rem;
    color: #9da7bd;
}

.footer {
    border-top: 1px solid #282e40;
    margin-top: 2rem;
    padding-top: 1rem;
    color: #7f899f;
    font-size: .78rem;
}

div[data-testid="stMetric"] {
    background: #151a27;
    border: 1px solid #2b3144;
    padding: .8rem 1rem;
    border-radius: 14px;
}

div[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif;
}
</style>
""",
    unsafe_allow_html=True,
)


PURPLE = "#a78bfa"
BLUE = "#67c7f5"
GREEN = "#6ee7b7"
PINK = "#fb91bd"
GOLD = "#f4c77b"

LAYOUT = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {
        "family": "DM Sans, sans-serif",
        "color": "#d9deee",
    },
    "margin": {
        "l": 15,
        "r": 15,
        "t": 40,
        "b": 15,
    },
}


# ============================================================
# 3. LOAD AND PREPARE DATA
# ============================================================

@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Cleaned dataset not found. "
            "Run `python feature_engineering.py` "
            "from the project folder first."
        )

    d = pd.read_csv(DATA_PATH)

    required_columns = [
        "date",
        "position",
        "artist",
        "song",
        "album_type",
        "is_explicit",
        "is_collaboration",
        "popularity",
        "duration_minutes",
        "total_tracks",
        "artist_count",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in d.columns
    ]

    if missing_columns:
        raise ValueError(
            "The cleaned dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    d["date"] = pd.to_datetime(
        d["date"],
        errors="coerce",
    )

    for col in ["artist", "album_type", "song"]:
        d[col] = (
            d[col]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

    d["album_type"] = d["album_type"].str.lower()

    for col in ["is_explicit", "is_collaboration"]:
        d[col] = (
            d[col]
            .astype(str)
            .str.lower()
            .map({
                "true": True,
                "false": False,
                "1": True,
                "0": False,
            })
            .fillna(False)
            .astype(bool)
        )

    for col in [
        "position",
        "popularity",
        "duration_minutes",
        "total_tracks",
        "artist_count",
    ]:
        d[col] = pd.to_numeric(
            d[col],
            errors="coerce",
        )

    d = d.dropna(
        subset=["date", "position"]
    )

    d["artist_credits"] = d["artist"].apply(
        lambda value: [
            artist.strip()
            for artist in value.split("&")
            if artist.strip()
        ]
    )

    return d


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title, subtitle=None):
    st.markdown(
        f"""
        <div class="section-head">
            <span class="section-dot"></span>
            <h2 style="margin:0">{title}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if subtitle:
        st.markdown(
            f'<p class="small-muted" style="margin-top:.15rem">'
            f'{subtitle}</p>',
            unsafe_allow_html=True,
        )


def explode_artists(data):
    rows = []

    for _, row in data.iterrows():
        for artist in row["artist_credits"]:
            rows.append({
                "Artist": artist,
                "Song": row["song"],
                "Date": row["date"],
                "Position": row["position"],
            })

    return pd.DataFrame(
        rows,
        columns=[
            "Artist",
            "Song",
            "Date",
            "Position",
        ],
    )


try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load project data: {exc}")
    st.stop()


# ============================================================
# 4. SIDEBAR AND FILTERS
# ============================================================

min_date = df["date"].min().date()
max_date = df["date"].max().date()

with st.sidebar:
    st.markdown("## 🎧 UK Music Insights")
    st.caption("Playlist market research")
    st.markdown("---")

    page = st.radio(
        "Explore",
        [
            "Overview",
            "Artist Analytics",
            "Collaboration Studio",
            "Content & Releases",
            "Data Quality & Method",
        ],
    )

    st.markdown("---")
    st.markdown("### Refine the data")

    date_range = st.date_input(
        "Chart date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    artist_options = sorted(
        df["artist"].unique().tolist()
    )

    selected_artist = st.selectbox(
        "Artist credit",
        ["All artists"] + artist_options,
    )

    track_type = st.selectbox(
        "Track type",
        [
            "All tracks",
            "Solo credits",
            "Collaborations",
        ],
    )

    selected_album = st.selectbox(
        "Release type",
        ["All release types"]
        + sorted(df["album_type"].unique().tolist()),
    )

    st.markdown("---")

    st.markdown(
        '<p class="small-muted">'
        'Python · pandas · Plotly · NetworkX · Streamlit'
        '</p>',
        unsafe_allow_html=True,
    )


if (
    isinstance(date_range, (tuple, list))
    and len(date_range) == 2
):
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date


f = df[
    (df["date"].dt.date >= start_date)
    & (df["date"].dt.date <= end_date)
].copy()

if selected_artist != "All artists":
    f = f[
        f["artist"].str.contains(
            selected_artist,
            regex=False,
            na=False,
        )
    ]

if track_type == "Solo credits":
    f = f[~f["is_collaboration"]]
elif track_type == "Collaborations":
    f = f[f["is_collaboration"]]

if selected_album != "All release types":
    f = f[f["album_type"] == selected_album]


# ============================================================
# 5. DASHBOARD HEADER
# ============================================================

st.markdown(
    f"""
    <div class="hero">
        <div class="eyebrow">
            Music market research · United Kingdom
        </div>
        <p class="hero-title">UK Music Insights</p>
        <p class="hero-copy">
            A closer look at the artists, collaborations and release
            patterns shaping the daily UK Top 50. Explore chart snapshots
            and turn data into useful findings.
        </p>
        <span class="pill">Artist diversity</span>
        <span class="pill">Collaboration patterns</span>
        <span class="pill">Content & releases</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    f"Selected period: {start_date:%d %b %Y} — "
    f"{end_date:%d %b %Y} · {len(f):,} chart entries"
)

if f.empty:
    st.warning(
        "No entries match these filters. "
        "Try widening the date range or changing a filter."
    )
    st.stop()


# ============================================================
# 6. COMMON METRICS
# ============================================================

credits = explode_artists(f)

unique_artists = (
    credits["Artist"].nunique()
    if not credits.empty
    else 0
)

collab_share = f["is_collaboration"].mean()
explicit_share = f["is_explicit"].mean()
single_share = (f["album_type"] == "single").mean()
avg_duration = f["duration_minutes"].mean()


# ============================================================
# 7. OVERVIEW
# ============================================================

if page == "Overview":

    section(
        "Market snapshot",
        "A quick read of the selected chart period.",
    )

    # Artist concentration based on individual artist-credit
    # appearances in the currently selected records.
    artist_credit_counts = credits["Artist"].value_counts()

    total_artist_credits = max(
        1,
        int(artist_credit_counts.sum()),
    )

    artist_credit_shares = (
        artist_credit_counts / total_artist_credits
    )

    artist_concentration_index = (
        artist_credit_shares.pow(2).sum()
    )

    unique_artist_count = credits["Artist"].nunique()

    content_variety_index = (
        unique_artist_count / max(1, len(f))
    ) * 100

    # KPI row 1
    cols = st.columns(3)

    with cols[0]:
        metric_card(
            "CHART ENTRIES",
            f"{len(f):,}",
            "Daily playlist positions",
        )

    with cols[1]:
        metric_card(
            "UNIQUE ARTISTS",
            f"{unique_artist_count:,}",
            "Distinct individual artist credits",
        )

    with cols[2]:
        metric_card(
            "COLLABORATION RATIO",
            f"{collab_share:.1%}",
            "Entries marked as collaborations",
        )

    st.write("")

    # KPI row 2
    cols = st.columns(3)

    with cols[0]:
        metric_card(
            "ARTIST CONCENTRATION (HHI)",
            f"{artist_concentration_index:.4f}",
            "Concentration of artist-credit appearances",
        )

    with cols[1]:
        metric_card(
            "EXPLICIT CONTENT SHARE",
            f"{explicit_share:.1%}",
            "Entries marked explicit",
        )

    with cols[2]:
        metric_card(
            "SINGLE SHARE",
            f"{single_share:.1%}",
            "Entries classified as singles",
        )

    st.write("")

    # Additional descriptive variety indicator
    metric_card(
        "CONTENT VARIETY INDEX",
        f"{content_variety_index:.2f}",
        "Unique artist credits per 100 chart entries",
    )

    st.write("")

    # --------------------------------------------------------
    # Artist presence and release format
    # --------------------------------------------------------

    left, right = st.columns([1.2, 1])

    with left:
        section(
            "Artist presence",
            "Most frequent individual artist credits in selected records.",
        )

        top = (
            credits["Artist"]
            .value_counts()
            .head(12)
            .sort_values()
            .rename_axis("Artist")
            .reset_index(name="Chart entries")
        )

        fig = px.bar(
            top,
            x="Chart entries",
            y="Artist",
            orientation="h",
            text="Chart entries",
            color="Chart entries",
            color_continuous_scale=[
                [0, "#45406f"],
                [1, PURPLE],
            ],
        )

        fig.update_layout(
            **LAYOUT,
            height=440,
            coloraxis_showscale=False,
            yaxis_title="",
            xaxis_title="Number of chart entries",
        )

        fig.update_traces(
            textposition="outside",
            cliponaxis=False,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:
        section(
            "Release format",
            "Distribution of album, single and compilation entries.",
        )

        rel = (
            f["album_type"]
            .value_counts()
            .rename_axis("Release type")
            .reset_index(name="Entries")
        )

        fig = px.pie(
            rel,
            names="Release type",
            values="Entries",
            hole=0.66,
            color_discrete_sequence=[
                PURPLE,
                BLUE,
                GOLD,
                GREEN,
            ],
        )

        fig.update_layout(
            **LAYOUT,
            height=360,
            legend=dict(
                orientation="h",
                y=-0.12,
            ),
        )

        fig.add_annotation(
            text=f"{len(f):,}<br><sup>entries</sup>",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(
                size=21,
                color="#f2f4fb",
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # --------------------------------------------------------
    # Popularity trend
    # --------------------------------------------------------

    st.write("")

    section(
        "Popularity across the selected period",
        "Daily snapshots can be noisy; use the date filter "
        "to focus on a smaller period.",
    )

    daily = (
        f.groupby("date", as_index=False)
        .agg(
            avg_popularity=("popularity", "mean")
        )
    )

    fig = px.line(
        daily,
        x="date",
        y="avg_popularity",
        markers=False,
    )

    fig.update_traces(
        line=dict(
            color=BLUE,
            width=2.5,
        )
    )

    fig.update_layout(
        **LAYOUT,
        height=320,
        xaxis_title="",
        yaxis_title="Average popularity",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.markdown(
        '<div class="insight">'
        '<b>Reading the dashboard:</b> These are descriptive patterns '
        'in the supplied chart snapshots. They can help guide questions '
        'for a marketing or A&R team, but do not prove why a track '
        'became popular.'
        '</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# 8. ARTIST ANALYTICS
# ============================================================

elif page == "Artist Analytics":

    section(
        "Artist analytics",
        "Measure chart presence and diversity without assuming "
        "frequency equals long-term success.",
    )

    counts = (
        credits["Artist"]
        .value_counts()
        .rename_axis("Artist")
        .reset_index(name="Chart entries")
    )

    counts["Credit share"] = (
        counts["Chart entries"]
        / max(1, len(credits))
    )

    n = st.slider(
        "Artists to display",
        5,
        25,
        12,
    )

    top = counts.head(n).sort_values(
        "Chart entries"
    )

    fig = px.bar(
        top,
        x="Chart entries",
        y="Artist",
        orientation="h",
        color="Chart entries",
        text="Chart entries",
        color_continuous_scale=[
            [0, "#45406f"],
            [1, PURPLE],
        ],
        hover_data={
            "Credit share": ":.1%",
        },
    )

    fig.update_layout(
        **LAYOUT,
        height=max(360, n * 29),
        coloraxis_showscale=False,
        yaxis_title="",
        xaxis_title="Chart entries",
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    a, b, c = st.columns(3)

    with a:
        metric_card(
            "UNIQUE ARTISTS",
            f"{counts['Artist'].nunique():,}",
            "Individual artist credits",
        )

    with b:
        top_five_share = (
            counts.head(5)["Chart entries"].sum()
            / max(1, len(credits))
        )

        metric_card(
            "TOP 5 CREDIT SHARE",
            f"{top_five_share:.1%}",
            "Share of individual credit appearances",
        )

    with c:
        metric_card(
            "AVERAGE DURATION",
            f"{avg_duration:.2f} min",
            "Selected entries",
        )

    section(
        "Duration and popularity",
        "Correlation describes a linear association, not cause and effect.",
    )

    sc = f.dropna(
        subset=[
            "duration_minutes",
            "popularity",
        ]
    )

    corr = (
        sc["duration_minutes"].corr(sc["popularity"])
        if len(sc) > 1
        else float("nan")
    )

    fig = px.scatter(
        sc,
        x="duration_minutes",
        y="popularity",
        color="is_collaboration",
        color_discrete_map={
            False: BLUE,
            True: PURPLE,
        },
        opacity=0.55,
        hover_data=[
            "song",
            "artist",
            "position",
        ],
        labels={
            "duration_minutes": "Duration (minutes)",
            "popularity": "Popularity",
            "is_collaboration": "Collaboration",
        },
    )

    fig.update_layout(
        **LAYOUT,
        height=410,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.markdown(
        f'<div class="insight">'
        f'Duration–popularity Pearson correlation in this selection: '
        f'<b>{corr:.3f}</b>. This does not show that song length '
        f'causes popularity.'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.expander("View artist leaderboard data"):
        st.dataframe(
            counts,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# 9. COLLABORATION STUDIO
# ============================================================

elif page == "Collaboration Studio":

    section(
        "Collaboration studio",
        "Explore how often artists appear together and which "
        "artist pairs share chart entries.",
    )

    a, b, c = st.columns(3)

    with a:
        metric_card(
            "COLLABORATION SHARE",
            f"{collab_share:.1%}",
            "Selected chart entries",
        )

    with b:
        metric_card(
            "AVG. ARTISTS / ENTRY",
            f"{f['artist_count'].mean():.2f}",
            "Based on artist field",
        )

    with c:
        metric_card(
            "COLLAB ENTRIES",
            f"{int(f['is_collaboration'].sum()):,}",
            "Artist field contains '&'",
        )

    left, right = st.columns(2)

    with left:
        section("Solo vs collaboration")

        types = pd.DataFrame({
            "Track type": [
                "Solo credit",
                "Collaboration",
            ],
            "Entries": [
                int((~f["is_collaboration"]).sum()),
                int(f["is_collaboration"].sum()),
            ],
        })

        fig = px.pie(
            types,
            names="Track type",
            values="Entries",
            hole=0.62,
            color="Track type",
            color_discrete_map={
                "Solo credit": BLUE,
                "Collaboration": PURPLE,
            },
        )

        fig.update_layout(
            **LAYOUT,
            height=350,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:
        section("Collaboration by chart position")

        ranked = f.assign(
            rank_group=f["position"].apply(
                lambda value: (
                    "Top 10"
                    if value <= 10
                    else "Positions 11–50"
                )
            )
        )

        stats = (
            ranked.groupby(
                "rank_group",
                as_index=False,
            )["is_collaboration"]
            .mean()
        )

        stats["Share (%)"] = (
            stats["is_collaboration"] * 100
        )

        fig = px.bar(
            stats,
            x="rank_group",
            y="Share (%)",
            text=stats["Share (%)"].map(
                lambda value: f"{value:.1f}%"
            ),
            color="rank_group",
            color_discrete_sequence=[
                PURPLE,
                BLUE,
            ],
        )

        fig.update_layout(
            **LAYOUT,
            height=350,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Collaboration share (%)",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # Collaboration network
    section(
        "Collaboration network",
        "Nodes are artist credits; edges connect artists appearing "
        "together in the same artist field.",
    )

    graph = nx.Graph()

    for artists in f.loc[
        f["is_collaboration"],
        "artist_credits",
    ]:
        for artist in artists:
            graph.add_node(artist)

        for u, v in combinations(artists, 2):
            if graph.has_edge(u, v):
                graph[u][v]["weight"] += 1
            else:
                graph.add_edge(
                    u,
                    v,
                    weight=1,
                )

    if graph.number_of_edges():

        max_nodes = st.slider(
            "Network size",
            8,
            35,
            18,
        )

        nodes = [
            node
            for node, _ in sorted(
                graph.degree(weight="weight"),
                key=lambda item: item[1],
                reverse=True,
            )[:max_nodes]
        ]

        sub = graph.subgraph(nodes).copy()

        pos = nx.spring_layout(
            sub,
            seed=21,
            k=0.8,
        )

        edge_x = []
        edge_y = []

        for u, v in sub.edges():
            edge_x.extend([
                pos[u][0],
                pos[v][0],
                None,
            ])

            edge_y.extend([
                pos[u][1],
                pos[v][1],
                None,
            ])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(
                width=1,
                color="rgba(167,139,250,.35)",
            ),
            hoverinfo="skip",
        )

        degree = dict(
            sub.degree(weight="weight")
        )

        labels = list(sub.nodes())

        node_x = [
            pos[node][0]
            for node in labels
        ]

        node_y = [
            pos[node][1]
            for node in labels
        ]

        sizes = [
            12 + min(degree[node], 22) * 1.6
            for node in labels
        ]

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=labels,
            textposition="top center",
            hovertext=[
                f"{node}<br>Weighted connections: "
                f"{degree[node]}"
                for node in labels
            ],
            hoverinfo="text",
            marker=dict(
                size=sizes,
                color=[
                    degree[node]
                    for node in labels
                ],
                colorscale=[
                    [0, "#4c4778"],
                    [1, PURPLE],
                ],
                line=dict(
                    width=1,
                    color="#e5ddff",
                ),
            ),
        )

        fig = go.Figure(
            data=[
                edge_trace,
                node_trace,
            ]
        )

        fig.update_layout(
            **LAYOUT,
            height=550,
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(
                l=10,
                r=10,
                t=15,
                b=10,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

        pairs = sorted(
            [
                (u, v, data.get("weight", 1))
                for u, v, data in graph.edges(data=True)
            ],
            key=lambda item: item[2],
            reverse=True,
        )

        with st.expander("Most frequent artist pairings"):
            st.dataframe(
                pd.DataFrame(
                    pairs[:15],
                    columns=[
                        "Artist 1",
                        "Artist 2",
                        "Shared entries",
                    ],
                ),
                use_container_width=True,
                hide_index=True,
            )

    else:
        st.info(
            "No collaboration records match the selected filters."
        )

    st.caption(
        "Method note: collaboration is identified from an ampersand "
        "(&) in the artist field, matching the project specification."
    )


# ============================================================
# 10. CONTENT AND RELEASES
# ============================================================

elif page == "Content & Releases":

    section(
        "Content and release structure",
        "Compare explicit-content flags, release categories and track lengths.",
    )

    left, right = st.columns(2)

    with left:
        section("Explicit vs clean")

        exp = (
            f["is_explicit"]
            .map({
                True: "Explicit",
                False: "Clean",
            })
            .value_counts()
            .rename_axis("Content label")
            .reset_index(name="Entries")
        )

        fig = px.pie(
            exp,
            names="Content label",
            values="Entries",
            hole=0.63,
            color="Content label",
            color_discrete_map={
                "Clean": BLUE,
                "Explicit": PINK,
            },
        )

        fig.update_layout(
            **LAYOUT,
            height=360,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:
        section("Release type")

        rel = (
            f["album_type"]
            .value_counts()
            .rename_axis("Release type")
            .reset_index(name="Entries")
        )

        fig = px.bar(
            rel,
            x="Release type",
            y="Entries",
            text="Entries",
            color="Release type",
            color_discrete_sequence=[
                PURPLE,
                BLUE,
                GOLD,
                GREEN,
            ],
        )

        fig.update_layout(
            **LAYOUT,
            height=360,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Chart entries",
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    section(
        "Track duration profile",
        "Groups follow the project definition: under 3 minutes, "
        "3–4 minutes and over 4 minutes.",
    )

    left, right = st.columns(2)

    with left:
        dc = (
            f["duration_group"]
            .value_counts()
            .rename_axis("Duration group")
            .reset_index(name="Entries")
        )

        fig = px.bar(
            dc,
            x="Duration group",
            y="Entries",
            text="Entries",
            color="Duration group",
            color_discrete_sequence=[
                BLUE,
                PURPLE,
                GOLD,
            ],
        )

        fig.update_layout(
            **LAYOUT,
            height=350,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Chart entries",
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:
        dp = (
            f.groupby(
                "duration_group",
                observed=True,
                as_index=False,
            )["popularity"]
            .mean()
        )

        fig = px.bar(
            dp,
            x="duration_group",
            y="popularity",
            text=dp["popularity"].map(
                lambda value: f"{value:.1f}"
            ),
            color="duration_group",
            color_discrete_sequence=[
                BLUE,
                PURPLE,
                GOLD,
            ],
        )

        fig.update_layout(
            **LAYOUT,
            height=350,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Average popularity",
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    a, b, c = st.columns(3)

    with a:
        metric_card(
            "AVERAGE DURATION",
            f"{avg_duration:.2f} min",
            "Selected entries",
        )

    with b:
        metric_card(
            "MEDIAN DURATION",
            f"{f['duration_minutes'].median():.2f} min",
            "Less affected by extremes",
        )

    with c:
        metric_card(
            "AVERAGE ALBUM SIZE",
            f"{f['total_tracks'].mean():.1f}",
            "Tracks listed in associated release",
        )

    with st.expander("Release type summary table"):
        st.dataframe(
            f.groupby("album_type").agg(
                Entries=("song", "count"),
                Mean_track_count=("total_tracks", "mean"),
                Mean_popularity=("popularity", "mean"),
            ).round(2).reset_index(),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# 11. DATA QUALITY AND METHODOLOGY
# ============================================================

else:

    section(
        "Data quality & methodology",
        "A transparent record of what the dataset supports "
        "and how the analysis was prepared.",
    )

    a, b, c = st.columns(3)

    with a:
        metric_card(
            "ROWS IN VIEW",
            f"{len(f):,}",
            "After filters and cleaning",
        )

    with b:
        metric_card(
            "DATE COVERAGE",
            f"{f['date'].nunique():,} days",
            "Unique chart dates in this view",
        )

    with c:
        metric_card(
            "MISSING CELLS",
            f"{int(f.isna().sum().sum()):,}",
            "In the filtered table",
        )

    section("Analysis steps")

    steps = [
        (
            "01",
            "Validate",
            "Inspect row counts, columns, missing values and duplicate rows.",
        ),
        (
            "02",
            "Clean",
            "Convert dates, standardise text fields and retain "
            "one entry per date-position.",
        ),
        (
            "03",
            "Create features",
            "Calculate duration in minutes, collaboration flags, "
            "artist counts and duration groups.",
        ),
        (
            "04",
            "Analyse",
            "Compare artist presence, collaborations, explicit flags, "
            "release types and duration.",
        ),
        (
            "05",
            "Communicate",
            "Present findings in an interactive dashboard with filters "
            "and explanations.",
        ),
    ]

    for number, title, copy in steps:
        st.markdown(
            f"""
            <div class="metric-card"
                 style="min-height:auto;margin:.45rem 0;
                        display:flex;gap:1rem;align-items:flex-start">
                <div style="color:{PURPLE};
                            font-family:Space Grotesk;
                            font-size:1.2rem;font-weight:700">
                    {number}
                </div>
                <div>
                    <b style="color:#f2f4fb">{title}</b>
                    <div class="small-muted">{copy}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section("Important limitations")

    st.markdown("""
    - **Artist origin:** The dataset has no nationality or
      country-of-origin field, so artists are not labelled as UK/domestic
      or international.

    - **Collaboration definition:** A track is marked collaborative
      when the artist field contains `&`. Other credit styles may not
      be detected.

    - **Repeated date-position rows:** The source file had repeated
      entries for a chart date and position. Cleaning keeps the first
      record for each date-position.

    - **Interpretation:** Popularity, chart position and content
      attributes are descriptive. Correlation does not establish causation.

    - **Scope:** This is exploratory data analysis, not a predictive
      machine-learning model, because the brief focuses on market
      structure and content patterns.

    - **HHI interpretation:** The Artist Concentration Index shown
      on the Overview page is calculated from artist-credit appearances.
      It is not a measure of streaming revenue, sales or the full UK music
      industry's market share.

    - **Content Variety Index:** This is a custom descriptive indicator
      calculated as distinct artist credits per 100 selected chart entries.
      It is not a standard industry metric.
    """)

    with st.expander("Preview the filtered dataset"):
        preview_columns = [
            column
            for column in [
                "date",
                "position",
                "song",
                "artist",
                "popularity",
                "duration_minutes",
                "album_type",
                "total_tracks",
                "is_explicit",
            ]
            if column in f.columns
        ]

        st.dataframe(
            f[preview_columns].sort_values(
                ["date", "position"],
                ascending=[False, True],
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.download_button(
        "⬇ Download filtered data (CSV)",
        data=f.to_csv(index=False).encode("utf-8"),
        file_name="uk_music_insights_filtered.csv",
        mime="text/csv",
    )


# ============================================================
# 12. FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    'UK Music Insights · Student exploratory data analysis project '
    '· Source: supplied Atlantic United Kingdom CSV. '
    'Designed to support interpretation, not causal claims.'
    '</div>',
    unsafe_allow_html=True,
)