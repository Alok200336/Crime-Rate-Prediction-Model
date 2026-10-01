from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from app.main import app
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.init_db import init_db
from app.models.news_article import NewsArticle
from app.models.crime_incident import CrimeIncident
from app.models.intelligence import ArticleIncidentLink, ArticleAssessment, IncidentCategory
from app.schemas.news import NewsArticleCreate
from app.pipelines.ingestion_pipeline import run_ingestion
from app.services.crime_classifier import classify_crime, CRIME_KEYWORDS
from app.services.location_extractor import extract_location
from app.services.crime_extractor import extract_crime_details

@pytest.fixture
def db():
    Base.metadata.drop_all(engine)
    init_db()
    with SessionLocal() as session:
        yield session

class Collector:
    errors = []
    def __init__(self, articles): self.articles = articles
    def fetch(self): return self.articles

def article(url='https://publisher.example/a', title='Police investigate alleged robbery in Noida', **kw):
    return NewsArticleCreate(title=title, url=url, source_name='Publisher', published_at=datetime(2026,10,4,18,40,tzinfo=timezone.utc), **kw)

def test_taxonomy_specificity_and_boundaries():
    assert len(CRIME_KEYWORDS) == 24
    assert classify_crime('Police investigate attempted murder in Delhi').crime_type == 'Attempted Murder'
    assert classify_crime('Police investigate vehicle theft in Noida').crime_type == 'Vehicle Theft'
    assert not classify_crime('Police attend grape harvest festival').is_crime
    assert classify_crime('Court acquitted suspect in murder trial').disposition == 'review'
    assert not classify_crime('Murder movie review').is_crime
    assert set(classify_crime('Police investigate kidnapping and extortion in Noida').categories) == {'Kidnapping','Extortion'}

def test_location_and_count_ambiguity():
    assert extract_location('Police in Delhi investigate Mumbai robbery').city is None
    assert extract_location('Police investigate robbery in Greater Noida').city == 'Greater Noida'
    assert extract_crime_details('Three people and 3 men arrested').suspect_count is None
    assert extract_crime_details('2 suspects arrested').suspect_count == 2

def test_pipeline_links_duplicates_and_is_idempotent(db):
    first = article()
    second = article('https://second.example/story')
    result = run_ingestion(db, Collector([first, second]))
    assert result['new_incidents'] == 1 and result['duplicate_articles'] == 1
    assert db.scalar(select(func.count()).select_from(ArticleIncidentLink)) == 2
    assert run_ingestion(db, Collector([first, second]))['new_articles'] == 0
    assert db.scalar(select(func.count()).select_from(CrimeIncident)) == 1
    assert db.scalar(select(CrimeIncident)).allegation_status == 'Alleged'

def test_distinct_locations_and_old_reports_are_not_merged(db):
    run_ingestion(db, Collector([article(),article('https://other.example/b', 'Police investigate alleged robbery in Delhi')]))
    assert db.scalar(select(func.count()).select_from(CrimeIncident)) == 2
    old = article('https://third.example/old'); old.published_at -= timedelta(days=10)
    assert run_ingestion(db, Collector([old]))['new_incidents'] == 1

def test_review_and_exclusion(db):
    result = run_ingestion(db, Collector([article(title='Court acquits man in robbery trial in Noida'),article('https://p.example/b', 'Police investigate robbery at unknown place'),article('https://p.example/c','Cricket match won')]))
    assert result['review'] == 2 and result['excluded'] == 1 and result['new_incidents'] == 0

def test_partial_failure_keeps_success(db):
    c = Collector([article()]); c.errors = ['Feed 2: HTTPStatusError']
    result = run_ingestion(db,c)
    assert result['status'] == 'partial' and result['new_incidents'] == 1

def test_additive_migration_preserves_legacy(db):
    a = NewsArticle(title='Legacy', url='https://legacy.example/story', processed=True)
    db.add(a); db.flush()
    i = CrimeIncident(article_id=a.id, title='Legacy', crime_type='Fraud')
    db.add(i); db.commit()
    init_db(); init_db()
    assert db.get(CrimeIncident,i.id).title == 'Legacy'
    assert db.scalar(select(func.count()).select_from(ArticleIncidentLink)) == 1
    assert db.scalar(select(func.count()).select_from(IncidentCategory)) == 1

def test_api_filters_analytics_and_review(db):
    run_ingestion(db,Collector([article(),article('https://second.example/a'),article('https://p.example/c','Court hears robbery trial in Noida')]))
    row = db.scalar(select(CrimeIncident)); row.created_at = datetime(2026,10,4,18,40,tzinfo=timezone.utc); db.commit()
    with TestClient(app) as client:
        result = client.get('/api/v1/crimes?category=Robbery&state=Uttar%20Pradesh&district=Gautam%20Buddha%20Nagar&source=Publisher&start=2026-10-05&end=2026-10-05')
        assert result.status_code == 200, result.text
        assert result.json()['total'] == 1
        assert len(result.json()['items'][0]['sources']) == 2
        assert client.get('/api/v1/crimes?q=notpresent').json()['total'] == 0
        assert client.get('/api/v1/crimes?q=%25').json()['total'] == 0
        stats = client.get('/api/v1/statistics').json()
        assert stats['total_incidents'] == 1 and stats['articles'] == 2
        assert stats['trend'][0]['date'] == '2026-10-05'
        assert client.get('/api/v1/statistics?period=week').status_code == 200
        assert client.get('/api/v1/map').json()['items'][0]['count'] == 1
        assert client.get('/api/v1/crimes?limit=0').status_code == 422
        assert client.get('/api/v1/crimes?start=2026-10-10&end=2026-01-01').status_code == 422
        assert client.get('/api/v1/pipeline').status_code == 401
        assert client.post('/api/v1/ingestion/seed-demo',headers={'X-Admin-Key':'test-key'}).status_code == 403
        headers = {'X-Admin-Key':'test-key'}
        pending = client.get('/api/v1/pipeline',headers=headers).json()['review'][0]['article_id']
        assert client.post(f'/api/v1/review/{pending}',headers=headers,json={'action':'link','incident_id':row.id}).status_code == 200
        assert client.get('/api/v1/statistics').json()['articles'] == 3
        assert client.get('/api/v1/crimes').json()['total'] == 1

def test_human_review_creation(db):
    run_ingestion(db,Collector([article(title='Police investigate robbery at unknown location')]))
    pending = db.scalar(select(ArticleAssessment)).article_id
    with TestClient(app) as client:
        headers={'X-Admin-Key':'test-key'}
        endpoint=f'/api/v1/review/{pending}'
        assert client.post(endpoint,headers=headers,json={'action':'create','categories':['Invalid'],'state':'Delhi'}).status_code == 422
        result=client.post(endpoint,headers=headers,json={'action':'create','categories':['Robbery','Assault'],'state':'Delhi','incident_date':'2026-10-01'})
        assert result.status_code == 200
        row=client.get('/api/v1/crimes').json()['items'][0]
        assert set(row['categories']) == {'Robbery','Assault'}
        assert row['incident_date'] == '2026-10-01'
        assert row['latitude'] is None
        assert client.post(endpoint,headers=headers,json={'action':'exclude'}).status_code == 404
