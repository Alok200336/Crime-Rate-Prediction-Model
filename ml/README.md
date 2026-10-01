# ML integration boundary
The v2 API exposes news-derived incident records and source links through `/api/v1/crimes`.
Use this data to study news coverage, not to estimate official population crime rates.
The uploaded project contained no trained prediction model; none is fabricated here.
Before integration: retain source lineage, deduplicate across time splits, distinguish
first-observed dates from incident dates, evaluate location/category extraction on a
human-labelled holdout set, and keep official NCRB observations in a separate dataset.
No predictive policing or individual risk scores are implemented.
