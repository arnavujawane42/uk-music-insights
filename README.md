# UK Music Insights
### UK Top 50 Playlist Market Structure, Artist Diversity & Content Localization Analysis

**Tagline:** Discover the Data Behind the Music.

## Project overview
UK Music Insights is a student data analytics project that explores daily UK Top 50 playlist snapshots. It studies artist presence, artist-credit diversity, collaborations, explicit-content flags, release formats and track duration. The dashboard has a polished dark interface while keeping the analysis transparent and explainable.

## Dashboard sections
- **Overview** — key indicators, artist presence, release formats and daily popularity patterns.
- **Artist Analytics** — individual artist-credit leaderboard and duration/popularity relationship.
- **Collaboration Studio** — solo vs collaboration share, chart-position comparison and interactive artist network.
- **Content & Releases** — explicit vs clean content, release categories, duration groups and release summaries.
- **Data Quality & Method** — cleaning steps, dataset preview, limitations and CSV export.

## Dataset
The project uses `data/Atlantic_United_Kingdom.csv` with fields including `date`, `position`, `song`, `artist`, `popularity`, `duration_ms`, `album_type`, `total_tracks`, `is_explicit` and `album_cover_url`.

## Methodology
1. Inspect columns, row counts, missing values and exact duplicate rows.
2. Convert dates and standardise text fields.
3. Retain one record per date-position after data-quality checking.
4. Split artist credits using `&` for individual artist-credit analysis.
5. Calculate artist presence, concentration/diversity indicators and collaboration metrics.
6. Compare solo and collaborative tracks, explicit flags, release types and track durations.
7. Present findings in a filterable Streamlit dashboard.

## Important data-quality note
The raw file contains 27,800 rows and 12 exact duplicate rows. One date (1 March 2025) has repeated date-position records, so the cleaning workflow keeps the first record for each date-position after sorting. This produces a consistent daily Top 50 structure.

## Domestic vs international artists
The provided dataset does not include nationality or country of origin. Therefore, the project does **not** label artists as domestic/UK or international without a verified artist-origin dataset. `data/artist_origin_template.csv` is included as a starting template if a verified mapping becomes available.

## Run locally
Open a terminal in the `UK_Top50_Market_Analysis` folder:

```bash
pip install -r requirements.txt
python eda.py
python feature_engineering.py
python market_analysis.py
python collaboration.py
streamlit run app.py
```

Streamlit will print a local address (usually `http://localhost:8501`). Open it in your browser.

## Project files
- `eda.py` — initial data checks and cleaning review
- `feature_engineering.py` — creates analysis features and cleaned data
- `market_analysis.py` — calculates market metrics
- `collaboration.py` — collaboration statistics and network logic
- `app.py` — interactive UK Music Insights dashboard
- `data/` — source data, cleaned data and derived tables
- `charts/` — exported analysis charts
- `docs/` — research paper, executive summary, key results and video script

## Student-level explanation
This is an exploratory data analysis project. It does not use machine learning because the brief focuses on describing market structure, diversity, collaborations, content and release format rather than predicting future chart position. Conclusions should be presented as patterns in the supplied dataset, not proof of cause and effect.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create a new app and select this repository.
3. Set the branch to `main` and the main file path to `app.py`.
4. Deploy and confirm the app opens successfully.

The dashboard reads its cleaned dataset from `data/uk_top50_clean.csv`, which is included in this repository. If you update the data pipeline, run the scripts in the order shown under **Run locally** and check the dashboard before publishing the changes.

## Submission deliverables

- `docs/UK_Top50_Research_Paper.pdf` — research paper.
- `docs/UK_Top50_Executive_Summary.pdf` — executive summary.
- `app.py` — interactive Streamlit dashboard.
- `data/` and `charts/` — datasets and exported analysis visuals.

## Scope and limitations

The dataset does not provide verified artist nationality or country-of-origin data. As a result, this project does not classify artists as domestic/UK or international. Findings are descriptive patterns in the supplied dataset and should not be interpreted as proof of causation.
