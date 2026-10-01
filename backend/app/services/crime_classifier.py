from dataclasses import dataclass, field
import re


@dataclass
class ClassificationResult:
    is_crime: bool
    crime_type: str | None
    confidence: float
    severity_score: int
    categories: list[str] = field(default_factory=list)
    disposition: str = "review"
    reason: str = ""


CRIME_KEYWORDS: dict[str, tuple[tuple[str, ...], int]] = {
    "Murder": (("murder", "murdered", "homicide", "killed", "stabbed to death", "shot dead"), 5),
    "Attempted Murder": (("attempted murder", "attempt to murder"), 5),
    "Rape": (("rape", "raped", "gang rape", "gangrape"), 5),
    "Sexual Assault": (("sexual assault", "molestation", "molested", "sexual harassment"), 4),
    "Kidnapping": (("kidnap", "kidnapped", "kidnapping", "abduct", "abducted", "abduction"), 4),
    "Human Trafficking": (("human trafficking", "trafficking racket"), 5),
    "Robbery": (("robbery", "robbed", "dacoity", "loot"), 3),
    "Burglary": (("burglary", "house break", "break-in"), 3),
    "Theft": (("theft", "stolen", "stealing", "vehicle theft"), 2),
    "Cybercrime": (("cyber fraud", "cybercrime", "online scam", "phishing", "digital arrest"), 3),
    "Fraud": (("fraud", "scam", "cheating case", "embezzlement"), 3),
    "Domestic Violence": (("domestic violence", "dowry harassment", "dowry death"), 4),
    "Child Abuse": (("child abuse", "minor assaulted", "pocso"), 5),
    "Drug Crime": (("narcotics", "drug trafficking", "drug peddling", "ndps", "heroin seized", "ganja seized"), 3),
    "Arms Crime": (("illegal arms", "arms act", "firearm seized", "weapon seized"), 3),
    "Extortion": (("extortion", "ransom demand"), 4),
    "Assault": (("assault", "attacked", "beaten", "brutally thrashed"), 3),
    "Rioting": (("riot", "rioting", "mob violence"), 4),
    "Organized Crime": (("gangster", "organized crime", "crime syndicate"), 4),
}

EXCLUSION_HINTS = ("movie review", "web series", "crime thriller", "fiction", "novel", "trailer", "box office")


CRIME_KEYWORDS.update({
    "Dowry Death": (("dowry death", "dowry killing"), 5),
    "Hate Crime": (("hate crime", "caste attack", "religiously motivated attack"), 4),
    "Vehicle Theft": (("vehicle theft", "car stolen", "bike stolen", "stolen vehicle"), 2),
    "Financial Crime": (("money laundering", "financial fraud", "tax evasion", "embezzlement"), 3),
    "Other": (("criminal offence", "criminal offense", "criminal case"), 2),
})

def matches(needle, text):
    return bool(re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", text))

def classify_crime(title: str, text: str | None = None) -> ClassificationResult:
    haystack = f"{title} {text or ''}".lower()
    if any(matches(x, haystack) for x in EXCLUSION_HINTS):
        return ClassificationResult(False, None, 0.05, 0, [], "excluded", "Entertainment or fiction context")
    hits = [name for name, (words, _) in CRIME_KEYWORDS.items() if any(matches(w, haystack) for w in words)]
    if "Attempted Murder" in hits:
        hits = [x for x in hits if x != "Murder"]
    if "Vehicle Theft" in hits: hits = [x for x in hits if x != "Theft"]
    if "Dowry Death" in hits: hits = [x for x in hits if x != "Domestic Violence"]
    if "Sexual Assault" in hits: hits = [x for x in hits if x != "Assault"]
    if not hits:
        return ClassificationResult(False, None, .1, 0, [], "excluded", "No supported crime evidence")
    hits.sort(key=lambda x: -CRIME_KEYWORDS[x][1])
    if any(matches(x, haystack) for x in ("accident", "earthquake", "flood", "no evidence", "no crime", "false report")):
        return ClassificationResult(True, hits[0], .3, CRIME_KEYWORDS[hits[0]][1], hits, "review", "Non-criminal cause or negated claim needs review")
    # Scores measure rule evidence, NOT truth or a calibrated probability.
    if any(matches(x, haystack) for x in ("acquitted", "acquittal", "convicted", "sentenced", "bail", "trial", "court", "anniversary", "years ago", "opinion", "crime rate", "statistics")):
        return ClassificationResult(True, hits[0], .45, CRIME_KEYWORDS[hits[0]][1], hits, "review", "Court, historical or aggregate context; not a new incident")
    evidence = any(matches(x, haystack) for x in ("police", "reported", "arrested", "fir", "complaint", "investigation", "booked", "alleged"))
    return ClassificationResult(True, hits[0], .75 if evidence else .45, CRIME_KEYWORDS[hits[0]][1], hits, "candidate" if evidence else "review", "Reported event cues" if evidence else "Insufficient event context")
