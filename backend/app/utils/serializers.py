def incident_to_dict(incident):
    return {
        "id": incident.id, "article_id": incident.article_id, "crime_type": incident.crime_type,
        "crime_subtype": incident.crime_subtype, "title": incident.title, "summary": incident.summary,
        "incident_date": incident.incident_date, "state": incident.state, "district": incident.district,
        "city": incident.city, "latitude": incident.latitude, "longitude": incident.longitude,
        "victim_count": incident.victim_count, "suspect_count": incident.suspect_count,
        "case_status": incident.case_status, "allegation_status": incident.allegation_status,
        "confidence_score": incident.confidence_score, "severity_score": incident.severity_score,
        "created_at": incident.created_at,
        "source_name": incident.article.source_name if incident.article else None,
        "article_url": incident.article.url if incident.article else None,
        "published_at": incident.article.published_at if incident.article else None,
    }
