import re

VAGUE_WORDS = [
    "easy", "fast", "quick", "simple", "seamless", "user-friendly",
    "intuitive", "efficient", "robust", "scalable", "secure", "optimize"
]

REQUIRED_AREAS = {
    "User roles / actors": ["user", "admin", "customer"],
    "Acceptance criteria": ["acceptance criteria"],
    "Success metrics / KPIs": ["kpi", "metric"],
    "Edge cases / failures": ["error", "fail"],
    "Dependencies / assumptions": ["dependency", "integration"],
    "Security / privacy": ["security", "privacy"]
}

def analyze_prd(text):
    findings = []
    lower = text.lower()

    for cat, keys in REQUIRED_AREAS.items():
        if not any(k in lower for k in keys):
            findings.append({
                "category": "Missing Requirement",
                "problem": f"{cat} not defined",
                "why_it_matters": "Can cause incomplete implementation",
                "suggestion": f"Add section for {cat}",
                "severity": "High"
            })

    for word in VAGUE_WORDS:
        if word in lower:
            findings.append({
                "category": "Ambiguity",
                "problem": f'Uses vague term "{word}"',
                "why_it_matters": "Not measurable",
                "suggestion": "Replace with measurable criteria",
                "severity": "Medium"
            })

    return findings