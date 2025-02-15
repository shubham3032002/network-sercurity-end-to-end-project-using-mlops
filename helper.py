from dotenv import load_dotenv, find_dotenv
import os
import streamlit as st
import datetime

# Load environment variables
load_dotenv(find_dotenv())
GROQ_API = os.getenv('GROQ_API_KEY')

@st.cache_data
def cached_extract_features(url):
    """Cache the results of the feature extraction for a URL."""
    from application import extract_features  # Lazy import to avoid circular import
    return extract_features(url)

def generate_report(features):
    """
    Generates a detailed phishing detection report based on the extracted features,
    categorizing them into safe, unsafe, and ambiguous factors.

    Parameters:
    features (dict): A dictionary of extracted features with their respective values.

    Returns:
    tuple: Markdown report as a string and the phishing score.
    """
    feature_details = {
        "having_IP_Address": (
            "IP Address Usage",
            {
                "safe": "The URL uses a domain name instead of an IP address, which is safe.",
                "unsafe": "The URL uses an IP address instead of a domain name, which is suspicious."
            }
        ),
        "URL_Length": (
            "URL Length",
            {
                "safe": "The URL length is within the safe threshold.",
                "unsafe": "The URL length exceeds the safe threshold, which is suspicious."
            }
        ),
        "Shortining_Service": (
            "URL Shortening Service",
            {
                "safe": "No URL shortening service is detected, which is safe.",
                "unsafe": "The URL uses a shortening service like bit.ly or tinyurl, which is suspicious."
            }
        ),
        "having_At_Symbol": (
            "Presence of '@' Symbol",
            {
                "safe": "The URL does not contain an '@' symbol, which is safe.",
                "unsafe": "The URL contains an '@' symbol, which is suspicious."
            }
        ),
        "double_slash_redirecting": (
            "Double Slash Redirection",
            {
                "safe": "The URL does not contain excessive '//' redirects, which is safe.",
                "unsafe": "The URL contains multiple '//' redirects, which is suspicious."
            }
        ),
        "Prefix_Suffix": (
            "Prefix/Suffix in Domain",
            {
                "safe": "The domain does not contain a hyphen, which is safe.",
                "unsafe": "The domain contains a hyphen, which is suspicious."
            }
        ),
        "having_Sub_Domain": (
            "Subdomain Count",
            {
                "safe": "The URL does not contain excessive subdomains, which is safe.",
                "unsafe": "The URL contains excessive subdomains, which is suspicious."
            }
        ),
        "SSLfinal_State": (
            "SSL State",
            {
                "safe": "The URL uses HTTPS with a valid SSL certificate, which is safe.",
                "unsafe": "The URL uses HTTP or has an invalid SSL certificate, which is suspicious."
            }
        ),
        "Domain_registeration_length": (
            "Domain Registration Length",
            {
                "safe": "The domain registration duration is longer than a year, which is safe.",
                "unsafe": "The domain registration duration is one year or less, which is suspicious."
            }
        ),
        "Favicon": (
            "Favicon",
            {
                "safe": "The favicon is loaded from the same domain, which is safe.",
                "unsafe": "The favicon is loaded from an external domain, which is suspicious."
            }
        ),
        "port": (
            "Port",
            {
                "safe": "The URL uses common ports like 80 or 443, which is safe.",
                "unsafe": "The URL uses uncommon ports, which is suspicious."
            }
        ),
        "HTTPS_token": (
            "HTTPS Token in Domain",
            {
                "safe": "The domain name does not contain the 'https' token, which is safe.",
                "unsafe": "The domain name contains the 'https' token, which is suspicious."
            }
        ),
        "Request_URL": (
            "External Resources in HTML",
            {
                "safe": "Less than 50% of the resources are loaded from external domains, which is safe.",
                "unsafe": "More than 50% of the resources are loaded from external domains, which is suspicious."
            }
        ),
        "URL_of_Anchor": (
            "Anchor Tags",
            {
                "safe": "Less than 30% of anchor links are to external domains, which is safe.",
                "unsafe": "More than 30% of anchor links are to external domains, which is suspicious."
            }
        ),
        "Links_in_tags": (
            "Links in Meta/Script/Link Tags",
            {
                "safe": "Less than 30% of links in tags are external, which is safe.",
                "unsafe": "More than 30% of links in tags are external, which is suspicious."
            }
        ),
        "SFH": (
            "Server Form Handler (SFH)",
            {
                "safe": "The form handler points to a valid domain, which is safe.",
                "unsafe": "The form handler is empty or points to an external domain, which is suspicious."
            }
        ),
        "Submitting_to_email": (
            "Submitting to Email",
            {
                "safe": "The form does not send data to an email address, which is safe.",
                "unsafe": "The form sends data to an email address, which is suspicious."
            }
        ),
        "Abnormal_URL": (
            "Abnormal URL",
            {
                "safe": "The domain appears normal, which is safe.",
                "unsafe": "The domain appears abnormal, which is suspicious."
            }
        ),
        "Redirect": (
            "Redirection",
            {
                "safe": "The URL does not contain excessive redirections, which is safe.",
                "unsafe": "The URL contains more than one redirection, which is suspicious."
            }
        ),
        "on_mouseover": (
            "OnMouseOver Events",
            {
                "safe": "No onmouseover events are detected, which is safe.",
                "unsafe": "Onmouseover events are detected, which is suspicious."
            }
        ),
        "RightClick": (
            "Right-Click Disabled",
            {
                "safe": "Right-click functionality is enabled, which is safe.",
                "unsafe": "Right-click functionality is disabled, which is suspicious."
            }
        ),
        "popUpWidnow": (
            "Popup Windows",
            {
                "safe": "No popup windows are detected, which is safe.",
                "unsafe": "Popup windows are detected, which is suspicious."
            }
        ),
        "Iframe": (
            "Iframes",
            {
                "safe": "No iframe tags are detected, which is safe.",
                "unsafe": "Iframe tags are detected, which is suspicious."
            }
        ),
        "age_of_domain": (
            "Domain Age",
            {
                "safe": "The domain age is older than six months, which is safe.",
                "unsafe": "The domain age is less than six months, which is suspicious."
            }
        ),
        "DNSRecord": (
            "DNS Record",
            {
                "safe": "The domain has valid DNS records, which is safe.",
                "unsafe": "The domain has invalid or missing DNS records, which is suspicious."
            }
        ),
        "web_traffic": (
            "Web Traffic",
            {
                "safe": "The website traffic is normal, which is safe.",
                "unsafe": "The website traffic is abnormally low, which is suspicious."
            }
        ),
        "Page_Rank": (
            "Page Rank",
            {
                "safe": "The page rank is normal, which is safe.",
                "unsafe": "The page rank is abnormally low, which is suspicious."
            }
        ),
        "Google_Index": (
            "Google Index",
            {
                "safe": "The URL is indexed in Google, which is safe.",
                "unsafe": "The URL is not indexed in Google, which is suspicious."
            }
        ),
        "Links_pointing_to_page": (
            "Links Pointing to Page",
            {
                "safe": "There are sufficient links pointing to the page, which is safe.",
                "unsafe": "There are no links pointing to the page, which is suspicious."
            }
        ),
        "Statistical_report": (
            "Statistical Report",
            {
                "safe": "The URL does not match any known malicious patterns, which is safe.",
                "unsafe": "The URL matches a known malicious pattern, which is suspicious."
            }
        ),
    }

    safe_factors, unsafe_factors, ambiguous_factors = [], [], []
    score = 0  # Initialize the phishing score

    for feature, (title, descriptions) in feature_details.items():
        value = features.get(feature, "Unknown")
        if value == 1 or value == "Safe" or value is False:
            safe_factors.append(f"- 🟢 **{title}**: {descriptions['safe']}")
            score += 1
        elif value == -1 or value == "Unsafe" or value is True:
            unsafe_factors.append(f"- 🔴 **{title}**: {descriptions['unsafe']}")
            score -= 2
        else:
            ambiguous_factors.append(f"- 🟡 **{title}**: The feature value is ambiguous or unknown.")
            score -= 1

    report = "### Phishing Detection Report\n\n"
    report += "#### Unsafe Factors:\n"
    report += "\n".join(unsafe_factors) + "\n\n" if unsafe_factors else "No unsafe factors detected.\n\n"
    report += "#### Safe Factors:\n"
    report += "\n".join(safe_factors) + "\n\n" if safe_factors else "No safe factors detected.\n\n"
    report += "#### Ambiguous Factors:\n"
    report += "\n".join(ambiguous_factors) + "\n\n" if ambiguous_factors else "No ambiguous factors detected.\n\n"
    report += "#### Summary:\n"
    if score > 0:
        report += "The URL is categorized as **safe** due to a higher number of safe factors.\n"
    elif score == 0:
        report += "The URL is categorized as **suspicious** due to the presence of some ambiguous factors.\n"
    else:
        report += "The URL is categorized as **phishing** due to the presence of multiple unsafe factors.\n"

    return report, score
