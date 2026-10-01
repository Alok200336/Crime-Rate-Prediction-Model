from app.services.crime_classifier import classify_crime

def test_crime():
    r = classify_crime("Police arrest man in murder case in Noida")
    assert r.is_crime and r.crime_type == "Murder"

def test_non_crime():
    assert classify_crime("India wins cricket match").is_crime is False
