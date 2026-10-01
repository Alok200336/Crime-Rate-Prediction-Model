import re
from dataclasses import dataclass
from datetime import date
from app.services.location_extractor import extract_location


@dataclass
class ExtractedCrime:
    crime_subtype: str | None = None
    incident_date: date | None = None
    state: str | None = None
    district: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    victim_count: int | None = None
    suspect_count: int | None = None
    case_status: str | None = None
    allegation_status: str = "Reported"


def _count_before(pattern: str, text: str) -> int | None:
    match = re.search(rf"\b(\d{{1,3}})\s+(?:{pattern})\b", text, re.I)
    return int(match.group(1)) if match else None


def extract_crime_details(title: str, text: str | None = None) -> ExtractedCrime:
    combined = f"{title}. {text or ''}"
    lower = combined.lower()
    location = extract_location(combined)

    status = None
    for needle, value in [
        ("acquitted", "Acquitted"), ("convicted", "Convicted"), ("arrested", "Arrested"), ("detained", "Detained"),
        ("fir registered", "FIR Registered"), ("booked", "Booked"),
        ("investigation", "Under Investigation"), ("probe", "Under Investigation")
    ]:
        if needle in lower:
            status = value
            break

    allegation = "Alleged" if any(x in lower for x in ("alleged", "accused of", "claims", "complaint")) else "Reported"
    return ExtractedCrime(
        state=location.state, district=location.district, city=location.city,
        latitude=location.latitude, longitude=location.longitude,
        victim_count=_count_before("victims?", combined),
        suspect_count=_count_before("suspects?|accused", combined),
        case_status=status, allegation_status=allegation,
    )
