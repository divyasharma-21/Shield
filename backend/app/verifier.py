"""Live reputation verifier and IOC heuristic checker for SentryMesh Guardian.

Performs:
  - PhishTank verified offline/online cache matching
  - Domain structure checks (homoglyph/punycode, suspicious TLDs, IP-as-host)
  - Safe whitelist matching (trusted banks, national portals, universities)
  - UPI handle reputation assessment

Safety Guardrail:
  NEVER opens or initiates connections to untrusted target URLs.
"""

import os
import csv
from typing import Dict, Any, List

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
PHISHTANK_CSV = os.path.join(BASE_DIR, "data", "raw", "phishtank.csv")

# Whitelist of legitimate domains (non-exhaustive reference anchors)
TRUSTED_DOMAINS = {
    "sbi.co.in",
    "onlinesbi.sbi",
    "hdfcbank.com",
    "icicibank.com",
    "axisbank.com",
    "pnbindia.in",
    "bankofbaroda.in",
    "npci.org.in",
    "uidai.gov.in",
    "incometax.gov.in",
    "cybercrime.gov.in",
    "rbi.org.in",
    "google.com",
    "paytm.com",
    "phonepe.com"
}

# TLDs frequently abused in rapid-registration phishing
HIGH_RISK_TLDS = {".xyz", ".top", ".tk", ".ml", ".ga", ".cf", ".gq", ".work", ".click", ".buzz", ".cam"}


class ReputationVerifier:
    def __init__(self, phishtank_path: str = PHISHTANK_CSV):
        self.phishtank_path = phishtank_path
        self.known_phishing_urls = set()
        self.known_phishing_domains = set()
        self._load_phishtank_cache()

    def _load_phishtank_cache(self):
        """Loads cached verified phishing URLs into memory."""
        if not os.path.exists(self.phishtank_path):
            return
        try:
            with open(self.phishtank_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get("url", "").strip().lower()
                    if url:
                        self.known_phishing_urls.add(url)
                        # Extract host
                        try:
                            from urllib.parse import urlparse
                            host = urlparse(url).netloc
                            if host:
                                self.known_phishing_domains.add(host)
                        except Exception:
                            pass
        except Exception:
            pass

    def verify_ioc_signals(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes extracted entities against live verification signals."""
        urls = entities.get("urls", [])
        domains = entities.get("domains", [])
        upi_ids = entities.get("upi_ids", [])

        url_matches = []
        domain_findings = []
        is_known_threat = False
        reputation_score = 0  # 0 is safe/neutral, 100 is confirmed threat

        # 1. URL Checks against PhishTank
        for u in urls:
            u_norm = u.lower().rstrip("/")
            if u_norm in self.known_phishing_urls:
                url_matches.append(u)
                is_known_threat = True
                reputation_score = max(reputation_score, 95)

        # 2. Domain Checks
        for d in domains:
            d_lower = d.lower()
            if d_lower in self.known_phishing_domains:
                domain_findings.append(f"Domain '{d}' matches a known phishing campaign database.")
                is_known_threat = True
                reputation_score = max(reputation_score, 90)

            # High risk TLD
            if any(d_lower.endswith(tld) for tld in HIGH_RISK_TLDS):
                domain_findings.append(f"Domain '{d}' uses a high-risk suspicious top-level domain.")
                reputation_score = max(reputation_score, 70)

            # IP address as host
            import re
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", d_lower):
                domain_findings.append(f"Direct IP address '{d}' used in link instead of a verified domain name.")
                reputation_score = max(reputation_score, 85)

            # Punycode / Homograph spoofing
            if "xn--" in d_lower:
                domain_findings.append(f"Domain '{d}' utilizes internationalized punycode character encoding (potential homoglyph spoofing).")
                reputation_score = max(reputation_score, 85)

            # Trusted domain detection
            if any(d_lower == t or d_lower.endswith("." + t) for t in TRUSTED_DOMAINS):
                domain_findings.append(f"Domain '{d}' matches a verified trusted institutional domain.")
                reputation_score = min(reputation_score, 10)

        # 3. UPI Checks
        upi_findings = []
        for u in upi_ids:
            if "@invalid" in u:
                upi_findings.append(f"UPI ID '{u}' uses an unrouted safety test handle.")
            elif any(prov in u.lower() for prov in ["okhdfcbank", "okaxis", "paytm", "ybl", "sbi"]):
                upi_findings.append(f"UPI ID '{u}' uses standard registered payment provider routing.")

        return {
            "reputation_score": reputation_score,
            "is_known_threat_match": is_known_threat,
            "phishtank_matches": url_matches,
            "domain_findings": domain_findings,
            "upi_findings": upi_findings,
            "reputation_status": "known_threat" if is_known_threat else ("suspicious" if reputation_score >= 60 else "neutral_or_trusted")
        }


# Global singleton instance
_verifier_instance = None

def get_verifier() -> ReputationVerifier:
    global _verifier_instance
    if _verifier_instance is None:
        _verifier_instance = ReputationVerifier()
    return _verifier_instance
