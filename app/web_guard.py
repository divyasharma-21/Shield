"""
WebGuard: URL and website safety analysis for SentryMesh.

WebGuard supports two complementary analysis paths:

1. URL-level analysis
   - URL structure
   - HTTPS
   - DNS resolution
   - IP-address hosts
   - suspicious ports
   - URL shorteners
   - punycode / Unicode indicators
   - lookalike brand/domain patterns
   - suspicious subdomains
   - credential/payment language
   - redirect parameters
   - supplied reputation signals

2. Optional trained ML analysis
   - Uses the trained PhiUSIIL WebGuard model when compatible
     webpage features are supplied.
   - Automatically derives features that can truthfully be obtained
     from the URL itself.
   - Never invents webpage-dependent features.
   - Never visits or executes the destination.

Important:
- A signal is evidence, not proof of malicious intent.
- WebGuard does not automatically block or visit a website.
- DNS information provides infrastructure context, not a malware verdict.
- ML predictions are probabilistic and should be interpreted together
  with observable evidence.
"""

import ipaddress
import os
import re
import socket
from typing import Any, Dict, List
from urllib.parse import parse_qs, unquote, urlparse


SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "is.gd",
    "cutt.ly",
    "rb.gy",
    "shorturl.at",
    "ow.ly",
}

SUSPICIOUS_TLDS = {
    ".zip",
    ".mov",
    ".click",
    ".top",
    ".xyz",
    ".work",
    ".download",
    ".buzz",
}

BRAND_DOMAINS = {
    "google": {
        "google.com",
        "google.co.in",
    },
    "microsoft": {
        "microsoft.com",
        "microsoftonline.com",
    },
    "apple": {
        "apple.com",
        "icloud.com",
    },
    "amazon": {
        "amazon.com",
        "amazon.in",
    },
    "paypal": {
        "paypal.com",
    },
    "facebook": {
        "facebook.com",
        "meta.com",
    },
    "instagram": {
        "instagram.com",
    },
    "whatsapp": {
        "whatsapp.com",
    },
    "sbi": {
        "sbi.co.in",
        "onlinesbi.sbi",
    },
    "hdfc": {
        "hdfcbank.com",
    },
    "icici": {
        "icicibank.com",
    },
}

SUSPICIOUS_URL_TERMS = {
    "login",
    "signin",
    "verify",
    "verification",
    "account",
    "kyc",
    "password",
    "credential",
    "otp",
    "payment",
    "pay",
    "refund",
    "claim",
    "wallet",
    "bank",
    "secure",
    "update",
    "suspend",
    "unlock",
}


WEBGUARD_MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "models",
    "webguard_phiusiil_logreg.joblib",
)


def _normalize_url(url: str) -> str:
    """Normalize a URL without changing its semantic destination."""

    if not isinstance(url, str):
        return ""

    value = url.strip()

    if not value:
        return ""

    if not re.match(
        r"^[a-zA-Z][a-zA-Z0-9+.-]*://",
        value,
    ):
        value = "https://" + value

    return value


def _is_ip_address(hostname: str) -> bool:
    """Return True when hostname is a literal IPv4 or IPv6 address."""

    if not hostname:
        return False

    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


def _registrable_domain(hostname: str) -> str:
    """
    Return a practical domain representation for brand comparison.

    This intentionally avoids requiring an external public-suffix dependency.
    """

    if not hostname:
        return ""

    hostname = hostname.lower().strip(".")
    parts = hostname.split(".")
    multi_suffixes = {"co.in","com.au","co.uk","co.jp","co.nz","com.br","co.za"}
    if len(parts) >= 3 and ".".join(parts[-2:]) in multi_suffixes:
        return ".".join(parts[-3:])
    if len(parts) >= 2:
        return ".".join(parts[-2:])

    return hostname


def _looks_like_brand_domain(hostname: str) -> List[str]:
    """
    Detect domains that contain a known brand name but are not that brand's
    known domain.

    This is an explainable lookalike signal, not a definitive phishing verdict.
    """

    if not hostname:
        return []

    hostname = hostname.lower().strip(".")
    registrable = _registrable_domain(hostname)

    matches = []

    for brand, official_domains in BRAND_DOMAINS.items():
        if brand in hostname and registrable not in official_domains:
            matches.append(brand)

    return matches


def _extract_url_language(parsed_url) -> List[str]:
    """Find credential/payment-oriented language in URL components."""

    searchable = " ".join(
        [
            parsed_url.path or "",
            parsed_url.params or "",
            parsed_url.query or "",
            parsed_url.fragment or "",
        ]
    ).lower()

    decoded = unquote(searchable)

    found = []

    for term in SUSPICIOUS_URL_TERMS:
        if re.search(
            r"\b" + re.escape(term) + r"\b",
            decoded,
        ):
            found.append(term)

    return sorted(found)


def _resolve_dns(hostname: str) -> Dict[str, Any]:
    """
    Resolve DNS information for a hostname.

    This function only performs DNS resolution. It does not connect to the
    website or execute anything.
    """

    if not hostname or _is_ip_address(hostname):
        return {
            "resolved": False,
            "addresses": [],
            "error": None,
        }

    try:
        address_info = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )

        addresses = sorted(
            {
                result[4][0]
                for result in address_info
                if result[4]
            }
        )

        return {
            "resolved": bool(addresses),
            "addresses": addresses,
            "error": None,
        }

    except socket.gaierror as exc:
        return {
            "resolved": False,
            "addresses": [],
            "error": str(exc),
        }

    except Exception as exc:
        return {
            "resolved": False,
            "addresses": [],
            "error": str(exc),
        }


def extract_url_features(url: str) -> Dict[str, Any]:
    """
    Extract PhiUSIIL features that can truthfully be derived from the URL.

    This function intentionally does not fabricate webpage-dependent
    features such as HTML line count, favicon presence, JavaScript count,
    forms, buttons, or iframe information.
    """

    normalized_url = _normalize_url(url)

    if not normalized_url:
        return {}

    parsed = urlparse(normalized_url)

    hostname = (parsed.hostname or "").lower().strip(".")
    full_url = normalized_url

    url_length = len(full_url)
    domain_length = len(hostname)

    letters = sum(
        char.isalpha()
        for char in full_url
    )

    digits = sum(
        char.isdigit()
        for char in full_url
    )

    equals_count = full_url.count("=")
    question_count = full_url.count("?")
    ampersand_count = full_url.count("&")

    special_chars = sum(
        not char.isalnum()
        for char in full_url
    )

    other_special_chars = sum(
        char in "@#$%^*()[]{}|\\;:'\"<>"
        for char in full_url
    )

    subdomain_count = max(
        0,
        len(hostname.split(".")) - 2,
    )

    return {
        "URLLength": url_length,
        "DomainLength": domain_length,
        "IsDomainIP": int(
            _is_ip_address(hostname)
        ),
        "NoOfSubDomain": subdomain_count,
        "NoOfLettersInURL": letters,
        "LetterRatioInURL": (
            letters / url_length
            if url_length
            else 0.0
        ),
        "NoOfDegitsInURL": digits,
        "DegitRatioInURL": (
            digits / url_length
            if url_length
            else 0.0
        ),
        "NoOfEqualsInURL": equals_count,
        "NoOfQMarkInURL": question_count,
        "NoOfAmpersandInURL": ampersand_count,
        "NoOfOtherSpecialCharsInURL": other_special_chars,
        "SpacialCharRatioInURL": (
            special_chars / url_length
            if url_length
            else 0.0
        ),
        "IsHTTPS": int(
            parsed.scheme.lower() == "https"
        ),
    }


def _load_webguard_model():
    """
    Load the trained PhiUSIIL model lazily.

    Lazy loading keeps URL-only analysis lightweight and avoids loading
    the model unless ML-compatible webpage features are actually supplied.
    """

    if not os.path.exists(WEBGUARD_MODEL_PATH):
        return None

    try:
        import joblib

        artifact = joblib.load(
            WEBGUARD_MODEL_PATH
        )

        if not isinstance(artifact, dict):
            return None

        model = artifact.get("model")
        features = artifact.get("features")

        if model is None or not features:
            return None

        if not hasattr(model, "predict_proba"):
            return None

        return artifact

    except Exception:
        return None


def _predict_with_webguard_model(
    webpage_features: Dict[str, Any],
) -> Dict[str, Any] | None:
    """
    Run the trained WebGuard model when all required features are supplied.

    Missing features are intentionally rejected rather than fabricated.
    """

    artifact = _load_webguard_model()

    if artifact is None:
        return None

    model = artifact["model"]
    feature_names = artifact["features"]

    missing = [
        feature
        for feature in feature_names
        if feature not in webpage_features
    ]

    if missing:
        return {
            "available": False,
            "reason": (
                "Trained WebGuard model requires webpage features "
                "that were not supplied."
            ),
            "missing_features": missing,
            "features_available": len(
                feature_names
            ) - len(missing),
            "features_required": len(
                feature_names
            ),
        }

    try:
        import pandas as pd

        row = {
            feature: webpage_features[feature]
            for feature in feature_names
        }

        feature_frame = pd.DataFrame(
            [row],
            columns=feature_names,
        )

        probabilities = model.predict_proba(
            feature_frame
        )[0]

        classes = model.named_steps[
            "classifier"
        ].classes_

        probability_map = {
            str(label): round(
                float(probability),
                4,
            )
            for label, probability in zip(
                classes,
                probabilities,
            )
        }

        phishing_probability = float(
            probability_map.get(
                "phishing",
                0.0,
            )
        )

        predicted_label = (
            "phishing"
            if phishing_probability >= 0.5
            else "legitimate"
        )

        return {
            "available": True,
            "predicted_label": predicted_label,
            "phishing_probability": round(
                phishing_probability,
                4,
            ),
            "probabilities": probability_map,
            "model": artifact.get(
                "model_type",
                "webguard_ml_model",
            ),
            "dataset": artifact.get(
                "dataset",
                "UCI_PhiUSIIL",
            ),
            "features_used": len(
                feature_names
            ),
        }

    except Exception as exc:
        return {
            "available": False,
            "reason": (
                "WebGuard ML inference could not be completed."
            ),
            "error": str(exc),
        }


def analyze_web_url(
    url: str,
    reputation: Dict[str, Any] | None = None,
    resolve_dns: bool = True,
    webpage_features: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Analyze a URL using observable technical and contextual signals.

    Optional `webpage_features` can contain PhiUSIIL-compatible features.
    When all required features are present, the trained WebGuard model
    is evaluated as an additional evidence source.

    WebGuard does not fetch or execute the destination itself.
    """

    normalized_url = _normalize_url(url)

    if not normalized_url:
        return {
            "url": url,
            "normalized_url": "",
            "valid_url": False,
            "risk_level": "unknown",
            "risk_score": 0.0,
            "signals": [],
            "recommended_actions": [
                "Provide a complete URL for analysis."
            ],
        }

    try:
        parsed = urlparse(
            normalized_url
        )

    except Exception:
        return {
            "url": url,
            "normalized_url": normalized_url,
            "valid_url": False,
            "risk_level": "unknown",
            "risk_score": 0.0,
            "signals": [
                "URL could not be parsed safely."
            ],
            "recommended_actions": [
                "Do not open the link until its destination can be verified."
            ],
        }

    hostname = (
        parsed.hostname or ""
    ).lower().strip(".")

    if (
        not hostname
        or parsed.scheme not in {
            "http",
            "https",
        }
    ):
        return {
            "url": url,
            "normalized_url": normalized_url,
            "valid_url": False,
            "risk_level": "unknown",
            "risk_score": 0.0,
            "signals": [
                "URL has an unsupported or missing web scheme/host."
            ],
            "recommended_actions": [
                "Verify the link before opening it."
            ],
        }

    signals: List[str] = []
    evidence: Dict[str, Any] = {}
    score_components: List[float] = []

    # ---------------------------------------------------------
    # HTTPS
    # ---------------------------------------------------------

    if parsed.scheme == "https":
        evidence["https"] = True

    else:
        signals.append(
            "The URL uses HTTP instead of HTTPS."
        )

        score_components.append(
            0.12
        )

        evidence["https"] = False

    # ---------------------------------------------------------
    # IP host
    # ---------------------------------------------------------

    if _is_ip_address(hostname):
        signals.append(
            "The URL uses a literal IP address as its host."
        )

        score_components.append(
            0.28
        )

        evidence["ip_host"] = True

    else:
        evidence["ip_host"] = False

    # ---------------------------------------------------------
    # DNS intelligence
    # ---------------------------------------------------------

    if (
        resolve_dns
        and not evidence["ip_host"]
    ):
        dns_result = _resolve_dns(
            hostname
        )

        evidence["dns"] = dns_result

        if dns_result["resolved"]:
            signals.append(
                "The domain successfully resolves through DNS."
            )

        else:
            signals.append(
                "The domain did not successfully resolve through DNS at analysis time."
            )

            score_components.append(
                0.10
            )

    else:
        evidence["dns"] = {
            "resolved": False,
            "addresses": [],
            "error": "DNS resolution skipped.",
        }

    # ---------------------------------------------------------
    # Port
    # ---------------------------------------------------------

    try:
        port = parsed.port

    except ValueError:
        port = None

    if (
        port is not None
        and port not in {
            80,
            443,
        }
    ):
        signals.append(
            f"The URL uses a non-standard web port ({port})."
        )

        score_components.append(
            0.12
        )

    # ---------------------------------------------------------
    # Shortener
    # ---------------------------------------------------------

    registrable = _registrable_domain(
        hostname
    )

    if registrable in SHORTENER_DOMAINS:
        signals.append(
            "The URL uses a link-shortening service that hides the final destination."
        )

        score_components.append(
            0.18
        )

        evidence["shortener"] = True

    else:
        evidence["shortener"] = False

    # ---------------------------------------------------------
    # Punycode / Unicode
    # ---------------------------------------------------------

    if "xn--" in hostname:
        signals.append(
            "The domain contains punycode and should be checked for Unicode lookalike characters."
        )

        score_components.append(
            0.18
        )

        evidence["punycode"] = True

    else:
        evidence["punycode"] = False

    try:
        hostname.encode("ascii")
        unicode_hostname = False

    except UnicodeEncodeError:
        unicode_hostname = True

    if unicode_hostname:
        signals.append(
            "The domain contains non-ASCII characters and may require Unicode lookalike verification."
        )

        score_components.append(
            0.18
        )

        evidence["unicode_hostname"] = True

    else:
        evidence["unicode_hostname"] = False

    # ---------------------------------------------------------
    # URL user-info / @ obfuscation
    # ---------------------------------------------------------
    if parsed.username is not None or "@" in (parsed.netloc or ""):
        signals.append("The URL contains user-information syntax before the @ separator; this can obscure the actual destination host.")
        score_components.append(0.22)
        evidence["userinfo_obfuscation"] = True
    else:
        evidence["userinfo_obfuscation"] = False

    # ---------------------------------------------------------
    # Brand impersonation
    # ---------------------------------------------------------

    brand_matches = _looks_like_brand_domain(
        hostname
    )

    if brand_matches:
        brands = ", ".join(
            sorted(brand_matches)
        )

        signals.append(
            "The domain contains a known brand name but does not "
            f"match its known official domain ({brands})."
        )

        score_components.append(
            0.32
        )

        evidence[
            "possible_brand_impersonation"
        ] = brand_matches

    else:
        evidence[
            "possible_brand_impersonation"
        ] = []

    # ---------------------------------------------------------
    # Suspicious TLD
    # ---------------------------------------------------------

    for tld in SUSPICIOUS_TLDS:

        if hostname.endswith(tld):
            signals.append(
                "The domain uses a TLD that can warrant additional "
                f"scrutiny ({tld})."
            )

            score_components.append(
                0.12
            )

            evidence[
                "suspicious_tld"
            ] = tld

            break

    # ---------------------------------------------------------
    # Subdomains
    # ---------------------------------------------------------

    subdomain_depth = max(
        0,
        len(
            hostname.split(".")
        ) - 2,
    )

    if subdomain_depth >= 3:
        signals.append(
            "The URL contains multiple subdomain levels that may obscure the destination."
        )

        score_components.append(
            0.12
        )

    evidence[
        "subdomain_depth"
    ] = subdomain_depth

    # ---------------------------------------------------------
    # Credential/payment language
    # ---------------------------------------------------------

    suspicious_terms = _extract_url_language(
        parsed
    )

    if suspicious_terms:
        signals.append(
            "The URL contains credential, account, payment, "
            "or verification language."
        )

        score_components.append(
            min(
                0.22,
                0.05
                * len(
                    suspicious_terms
                ),
            )
        )

        evidence[
            "suspicious_terms"
        ] = suspicious_terms

    else:
        evidence[
            "suspicious_terms"
        ] = []

    # ---------------------------------------------------------
    # Redirect parameters
    # ---------------------------------------------------------

    query_values = parse_qs(
        parsed.query
    )

    redirect_parameter_names = {
        "url",
        "uri",
        "redirect",
        "redirect_url",
        "return",
        "return_url",
        "next",
        "target",
    }

    redirect_parameters = sorted(
        name
        for name in query_values
        if name.lower()
        in redirect_parameter_names
    )

    if redirect_parameters:
        signals.append(
            "The URL contains parameters commonly used to specify a redirect destination."
        )

        score_components.append(
            0.10
        )

        evidence[
            "redirect_parameters"
        ] = redirect_parameters

    else:
        evidence[
            "redirect_parameters"
        ] = []

    # ---------------------------------------------------------
    # External reputation
    # ---------------------------------------------------------

    reputation = reputation or {}

    if reputation.get(
        "known_malicious"
    ) is True:

        source = reputation.get(
            "source",
            "external reputation source",
        )

        signals.append(
            "An external reputation source reports this destination "
            f"as malicious ({source})."
        )

        score_components.append(
            0.60
        )

    if reputation.get(
        "domain_age_days"
    ) is not None:

        try:
            age_days = float(
                reputation[
                    "domain_age_days"
                ]
            )

            if age_days <= 7:
                signals.append(
                    "The domain was registered very recently according "
                    "to the supplied reputation data."
                )

                score_components.append(
                    0.20
                )

            evidence[
                "domain_age_days"
            ] = age_days

        except (
            TypeError,
            ValueError,
        ):
            pass

    if reputation.get(
        "reputation_signal"
    ):
        signals.append(
            str(
                reputation[
                    "reputation_signal"
                ]
            )
        )

    # ---------------------------------------------------------
    # URL-derived PhiUSIIL features
    # ---------------------------------------------------------

    derived_url_features = extract_url_features(
        normalized_url
    )

    evidence[
        "url_features"
    ] = derived_url_features

    # ---------------------------------------------------------
    # Trained WebGuard ML model
    # ---------------------------------------------------------

    ml_result = None

    if webpage_features is not None:

        combined_webpage_features = {
            **derived_url_features,
            **webpage_features,
        }

        ml_result = _predict_with_webguard_model(
            combined_webpage_features
        )

        evidence[
            "ml_model"
        ] = ml_result

        if (
            ml_result
            and ml_result.get(
                "available"
            )
        ):
            phishing_probability = float(
                ml_result[
                    "phishing_probability"
                ]
            )

            signals.append(
                "The trained WebGuard model evaluated the supplied webpage features."
            )

            score_components.append(
                0.50
                * phishing_probability
            )

            if phishing_probability >= 0.80:
                signals.append(
                    "The trained WebGuard model assigns a high phishing probability "
                    "to the supplied webpage features."
                )

            elif phishing_probability >= 0.50:
                signals.append(
                    "The trained WebGuard model identifies phishing risk in the "
                    "supplied webpage features."
                )

    else:
        evidence[
            "ml_model"
        ] = {
            "available": False,
            "reason": (
                "A complete PhiUSIIL webpage feature vector was not supplied. "
                "URL-observable features were extracted, but webpage-dependent "
                "features were not fabricated."
            ),
            "url_features_extracted": sorted(
                derived_url_features.keys()
            ),
        }

    # ---------------------------------------------------------
    # Risk calculation
    # ---------------------------------------------------------

    risk_score = min(
        1.0,
        sum(
            score_components
        ),
    )

    if reputation.get(
        "known_malicious"
    ) is True:
        risk_level = "high"

    elif risk_score >= 0.60:
        risk_level = "high"

    elif risk_score >= 0.30:
        risk_level = "medium"

    elif risk_score > 0.0:
        risk_level = "low"

    else:
        risk_level = "none"

    # ---------------------------------------------------------
    # Recommended actions
    # ---------------------------------------------------------

    if risk_level == "high":

        recommended_actions = [
            "Do not enter passwords, OTPs, card details, or banking information.",
            "Do not download files or install software from this destination.",
            "Verify the website through the organization's official app or manually entered official domain.",
        ]

    elif risk_level == "medium":

        recommended_actions = [
            "Verify the domain before entering credentials or payment information.",
            "Avoid following unexpected login, KYC, refund, or payment prompts.",
            "Use the organization's official app or manually entered website when possible.",
        ]

    elif risk_level == "low":

        recommended_actions = [
            "Review the destination carefully before entering sensitive information.",
        ]

    else:

        recommended_actions = [
            "No strong risk signal was detected from the supplied URL alone.",
            "Continue to verify the destination before entering sensitive information.",
        ]

    return {
        "url": url,
        "normalized_url": normalized_url,
        "valid_url": True,
        "domain": hostname,
        "risk_level": risk_level,
        "risk_score": round(
            risk_score,
            2,
        ),
        "signals": signals,
        "evidence": evidence,
        "recommended_actions": recommended_actions,
        "explainable_report": {
            "score_components": [round(float(x),4) for x in score_components],
            "summary": f"The {risk_level} assessment is the bounded combination of observable URL/reputation/ML evidence; no single TLD or keyword is treated as proof.",
            "ml_status": evidence.get("ml_model", {}),
        },
        "note": (
            "WebGuard evaluates observable URL, DNS, and supplied "
            "reputation signals. URL-observable PhiUSIIL features are "
            "derived automatically. When a complete webpage feature "
            "vector is available, trained ML evidence is evaluated. "
            "A low-risk result does not guarantee that a website is safe."
        ),
    }