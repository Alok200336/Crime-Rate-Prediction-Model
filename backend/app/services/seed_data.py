from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.crime_incident import CrimeIncident
from app.models.news_article import NewsArticle
from app.services.deduplication import make_dedupe_key

SAMPLES = [
    ("Murder", "Man arrested in connection with murder case in Noida", "Noida", "Uttar Pradesh", "Gautam Buddha Nagar", 28.5355, 77.3910, 5),
    ("Cybercrime", "Cyber fraud complaint filed after online scam in Bengaluru", "Bengaluru", "Karnataka", "Bengaluru Urban", 12.9716, 77.5946, 3),
    ("Robbery", "Police investigate robbery reported in Delhi", "Delhi", "Delhi", "Delhi", 28.6139, 77.2090, 3),
    ("Fraud", "Financial fraud case registered in Mumbai", "Mumbai", "Maharashtra", "Mumbai", 19.0760, 72.8777, 3),
    ("Kidnapping", "Kidnapping case under investigation in Jaipur", "Jaipur", "Rajasthan", "Jaipur", 26.9124, 75.7873, 4),
    ("Theft", "Vehicle theft reported in Hyderabad", "Hyderabad", "Telangana", "Hyderabad", 17.3850, 78.4867, 2),
]


def seed_demo(db: Session) -> int:
    count = 0
    for i, (ctype, title, city, state, district, lat, lon, severity) in enumerate(SAMPLES):
        url = f"https://example.invalid/demo-crime-{i}"
        if db.query(NewsArticle).filter(NewsArticle.url == url).first():
            continue
        article = NewsArticle(title=title, summary="Demo record for local development only.", source_name="Demo News", source_domain="example.invalid", url=url, published_at=datetime.now(timezone.utc)-timedelta(hours=i*3), processed=True)
        db.add(article); db.flush()
        db.add(CrimeIncident(article_id=article.id, crime_type=ctype, title=title, summary=article.summary, city=city, state=state, district=district, latitude=lat, longitude=lon, case_status="Under Investigation", allegation_status="Reported", confidence_score=0.9, severity_score=severity, dedupe_key=make_dedupe_key(title)))
        count += 1
    db.commit(); return count
