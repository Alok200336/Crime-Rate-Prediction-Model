from app.services.location_extractor import extract_location

def test_noida():
    r = extract_location("Incident reported in Noida")
    assert r.state == "Uttar Pradesh" and r.city == "Noida"
