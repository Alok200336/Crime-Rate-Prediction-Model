from dataclasses import dataclass
import re


@dataclass
class LocationResult:
    state: str | None = None
    district: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None


LOCATIONS = {
    "delhi": ("Delhi", "Delhi", "Delhi", 28.6139, 77.2090),
    "new delhi": ("Delhi", "New Delhi", "New Delhi", 28.6139, 77.2090),
    "noida": ("Uttar Pradesh", "Gautam Buddha Nagar", "Noida", 28.5355, 77.3910),
    "greater noida": ("Uttar Pradesh", "Gautam Buddha Nagar", "Greater Noida", 28.4744, 77.5040),
    "lucknow": ("Uttar Pradesh", "Lucknow", "Lucknow", 26.8467, 80.9462),
    "kanpur": ("Uttar Pradesh", "Kanpur Nagar", "Kanpur", 26.4499, 80.3319),
    "ghaziabad": ("Uttar Pradesh", "Ghaziabad", "Ghaziabad", 28.6692, 77.4538),
    "mumbai": ("Maharashtra", "Mumbai", "Mumbai", 19.0760, 72.8777),
    "pune": ("Maharashtra", "Pune", "Pune", 18.5204, 73.8567),
    "nagpur": ("Maharashtra", "Nagpur", "Nagpur", 21.1458, 79.0882),
    "bengaluru": ("Karnataka", "Bengaluru Urban", "Bengaluru", 12.9716, 77.5946),
    "bangalore": ("Karnataka", "Bengaluru Urban", "Bengaluru", 12.9716, 77.5946),
    "hyderabad": ("Telangana", "Hyderabad", "Hyderabad", 17.3850, 78.4867),
    "chennai": ("Tamil Nadu", "Chennai", "Chennai", 13.0827, 80.2707),
    "kolkata": ("West Bengal", "Kolkata", "Kolkata", 22.5726, 88.3639),
    "jaipur": ("Rajasthan", "Jaipur", "Jaipur", 26.9124, 75.7873),
    "ahmedabad": ("Gujarat", "Ahmedabad", "Ahmedabad", 23.0225, 72.5714),
    "surat": ("Gujarat", "Surat", "Surat", 21.1702, 72.8311),
    "bhopal": ("Madhya Pradesh", "Bhopal", "Bhopal", 23.2599, 77.4126),
    "indore": ("Madhya Pradesh", "Indore", "Indore", 22.7196, 75.8577),
    "patna": ("Bihar", "Patna", "Patna", 25.5941, 85.1376),
    "ranchi": ("Jharkhand", "Ranchi", "Ranchi", 23.3441, 85.3096),
    "chandigarh": ("Chandigarh", "Chandigarh", "Chandigarh", 30.7333, 76.7794),
    "gurugram": ("Haryana", "Gurugram", "Gurugram", 28.4595, 77.0266),
    "gurgaon": ("Haryana", "Gurugram", "Gurugram", 28.4595, 77.0266),
    "kochi": ("Kerala", "Ernakulam", "Kochi", 9.9312, 76.2673),
    "thiruvananthapuram": ("Kerala", "Thiruvananthapuram", "Thiruvananthapuram", 8.5241, 76.9366),
    "guwahati": ("Assam", "Kamrup Metropolitan", "Guwahati", 26.1445, 91.7362),
    "bhubaneswar": ("Odisha", "Khordha", "Bhubaneswar", 20.2961, 85.8245),
}


def extract_location(text: str) -> LocationResult:
    lower = text.lower()
    found = []
    for key in sorted(LOCATIONS, key=len, reverse=True):
        if re.search(r"(?<!\w)" + re.escape(key) + r"(?!\w)", lower):
            state, district, city, lat, lon = LOCATIONS[key]
            if not any(key in longer for longer, _ in found):
                found.append((key, LocationResult(state, district, city, lat, lon)))
    if len(found) == 1:
        return found[0][1]
    return LocationResult()
