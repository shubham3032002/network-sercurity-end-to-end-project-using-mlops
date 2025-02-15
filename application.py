import streamlit as st
import dns.resolver
import requests
import re
from urllib.parse import urlparse
from datetime import datetime
import pickle
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
load_dotenv(find_dotenv())
GROQ_API = os.getenv('GROQ_API_KEY')

# Load pre-trained model and preprocessing pipeline
with open("final_model/preprocessor.pkl", "rb") as f:
    preprocess_pipeline = pickle.load(f)

with open("final_model/model.pkl", "rb") as f:
    model = pickle.load(f)

# Feature extraction functions
def having_IP_Address(url):
    try:
        hostname = urlparse(url).hostname
        if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', hostname):
            return -1
        return 1
    except:
        return -1

def URL_Length(url):
    return -1 if len(url) >= 54 else 1

def Shortining_Service(url):
    return -1 if re.search(r"bit\.ly|tinyurl\.com", url) else 1

def having_At_Symbol(url):
    return -1 if "@" in url else 1

def double_slash_redirecting(url):
    return -1 if url.count("//") > 1 else 1

def Prefix_Suffix(url):
    hostname = urlparse(url).hostname
    return -1 if "-" in hostname else 1

def having_Sub_Domain(url):
    hostname = urlparse(url).hostname
    return -1 if hostname.count(".") > 2 else 1

def SSLfinal_State(url):
    return 1 if url.startswith("https") else -1

def get_dns_records(domain):
    try:
        dns.resolver.resolve(domain, 'A')
        return 1
    except:
        return -1

def Domain_registeration_length(domain):
    try:
        response = requests.get(f"https://input.payapi.io/v1/api/fraud/domain/{domain}")
        if response.status_code == 200:
            data = response.json()
            creation_date = data.get("created")
            if creation_date:
                creation_date = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                registration_length = (datetime.now() - creation_date).days
                return 1 if registration_length > 365 else -1
        return -1
    except:
        return -1

def age_of_domain(domain):
    try:
        response = requests.get(f"https://input.payapi.io/v1/api/fraud/domain/{domain}")
        if response.status_code == 200:
            data = response.json()
            creation_date = data.get("created")
            if creation_date:
                creation_date = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                domain_age = (datetime.now() - creation_date).days
                return 1 if domain_age > 180 else -1
        return -1
    except:
        return -1

def Favicon(url):
    try:
        response = requests.get(url)
        if response.status_code == 200 and ('<link rel="icon"' in response.text or '<link rel="shortcut icon"' in response.text):
            return 1
        return -1
    except:
        return -1

def port(url):
    parsed_url = urlparse(url)
    return -1 if ":" in parsed_url.netloc else 1

def HTTPS_token(url):
    hostname = urlparse(url).hostname
    return -1 if "https" in hostname else 1

def Request_URL(url):
    try:
        # Extract the domain of the given URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Fetch the HTML content of the webpage
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return -1
        
        html_content = response.text
        
        # Find all external resource URLs in the HTML
        external_resources = []
        for link in re.findall(r'<(img|script|link).*?(src|href)="([^"]+)"', html_content):
            resource_url = link[2]
            resource_domain = urlparse(resource_url).netloc
            if resource_domain and resource_domain != domain:
                external_resources.append(resource_url)
        
        # Calculate the percentage of external resources
        total_resources = len(re.findall(r'<(img|script|link).*?(src|href)="([^"]+)"', html_content))
        if total_resources == 0:
            return 1  # No external resources, likely safe
        
        external_percentage = (len(external_resources) / total_resources) * 100
        return 1 if external_percentage < 50 else -1
    except Exception as e:
        return -1  # Return -1 if any exception occ

def URL_of_Anchor(url):
    try:
        domain = urlparse(url).netloc
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        anchors = soup.find_all("a", href=True)

        if not anchors:
            return 1  # No anchors, considered safe

        external_count = sum(1 for anchor in anchors if urlparse(anchor["href"]).netloc and urlparse(anchor["href"]).netloc != domain)
        total_count = len(anchors)
        external_percentage = (external_count / total_count) * 100

        return -1 if external_percentage >= 67 else 1
    except:
        return -1

def Links_in_tags(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Count the total links in `<meta>`, `<script>`, and `<link>` tags
        meta_links = soup.find_all("meta", content=True)
        script_links = soup.find_all("script", src=True)
        link_tags = soup.find_all("link", href=True)

        total_links = len(meta_links) + len(script_links) + len(link_tags)

        # If the percentage of these tags containing links is high, return -1
        return -1 if total_links > 20 else 1
    except:
        return -1

def SFH(url):
    try:
        domain = urlparse(url).netloc
        forms = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser").find_all("form")
        for form in forms:
            action = form.get("action", "").lower()
            if not action or "about:blank" in action:
                return -1
            elif domain not in urlparse(action).netloc:
                return 0
        return 1
    except:
        return -1

def Submitting_to_email(url):
    try:
        page_content = requests.get(url, timeout=10).text
        return -1 if "mailto:" in page_content else 1
    except:
        return -1
def Abnormal_URL(url):
    try:
        hostname = urlparse(url).hostname
        return -1 if hostname not in url else 1
    except:
        return -1
def Redirect(url):
    try:
        response = requests.get(url, timeout=5)
        # Check if the final URL after redirection is different from the input URL
        return -1 if response.url != url else 1
    except:
        return -1

def on_mouseover(url):
    try:
        # Check if "onmouseover" JavaScript event exists in the HTML content of the page
        response = requests.get(url, timeout=5)
        if "onmouseover" in response.text:
            return -1  # Indicates phishing behavior
        return 1
    except:
        return -1 

def RightClick(url):
    try:
        # Check if "event.button==2" (disabling right-click) exists in the HTML content
        response = requests.get(url, timeout=5)
        if "event.button==2" in response.text or "contextmenu" in response.text:
            return -1  # Indicates right-click is disabled
        return 1
    except:
        return -1  

def popUpWidnow(url):
    try:
        # Check for popup-related scripts in the HTML content
        response = requests.get(url, timeout=5)
        if "window.open" in response.text or "popup" in response.text:
            return -1  # Popup window detected
        return 1
    except:
        return -1

def Iframe(url):
    try:
        # Check for iframe tags in the HTML content
        response = requests.get(url, timeout=5)
        if "<iframe" in response.text:
            return -1  # Iframe detected
        return 1
    except:
        return -1 

def web_traffic(domain):
    try:
        response = requests.get(f"https://data.similarweb.com/api/v1/data?domain={domain}")
        if response.status_code == 200:
            traffic = response.json().get("visits", 0)
            return 1 if traffic > 1000 else -1
        return -1
    except:
        return -1

def Page_Rank(url):
    try:
        # Example functionality: Check for Alexa Rank using a dummy threshold
        domain = urlparse(url).netloc
        response = requests.get(f"https://www.alexa.com/minisiteinfo/{domain}")
        if response.status_code == 200 and "global rank" in response.text.lower():
            return 1  # Page Rank exists (above threshold)
        return -1  # Low or no Page Rank
    except:
        return -1  # Return -1 if the request fails

def Google_Index(url):
    try:
        response = requests.get(f"https://www.google.com/search?q=site:{url}")
        return 1 if "did not match any documents" not in response.text else -1
    except:
        return -1

def Links_pointing_to_page(url):
    try:
        # Simulated functionality using a dummy threshold
        domain = urlparse(url).netloc
        # Replace this with an actual API or web scraping to get the number of backlinks
        response = requests.get(f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}",
                                headers={"API-OPR": "YOUR_API_KEY"})
        if response.status_code == 200:
            data = response.json()
            backlinks = data.get("response", [{}])[0].get("rank", 0)
            return 1 if backlinks > 0 else -1  # Assume positive rank means links exist
        return -1  # Default if no data or error
    except:
        return -1  # Return -1 in case of error

def Statistical_report(url):
    return -1 if re.search(r"malicious|phishing|blacklist", url) else 1

# Feature extraction pipeline
def extract_features(url):
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        features = {
            "having_IP_Address": having_IP_Address(url),
            "URL_Length": URL_Length(url),
            "Shortining_Service": Shortining_Service(url),
            "having_At_Symbol": having_At_Symbol(url),
            "double_slash_redirecting": double_slash_redirecting(url),
            "Prefix_Suffix": Prefix_Suffix(url),
            "having_Sub_Domain": having_Sub_Domain(url),
            "SSLfinal_State": SSLfinal_State(url),
            "Domain_registeration_length": Domain_registeration_length(domain),
            "Favicon": Favicon(url),
            "port": port(url),
            "HTTPS_token": HTTPS_token(url),
            "Request_URL": Request_URL(url),
            "URL_of_Anchor": URL_of_Anchor(url),
            "Links_in_tags": Links_in_tags(url),
            "SFH": SFH(url),
            "Submitting_to_email": Submitting_to_email(url),
            "Abnormal_URL": Abnormal_URL(url),
            "Redirect": Redirect(url),
            "on_mouseover": on_mouseover(url),
            "RightClick": RightClick(url),
            "popUpWidnow": popUpWidnow(url),
            "Iframe": Iframe(url),
            "age_of_domain": age_of_domain(domain),
            "DNSRecord": get_dns_records(domain),
            "web_traffic": web_traffic(domain),
            "Page_Rank": Page_Rank(url),
            "Google_Index": Google_Index(url),
            "Links_pointing_to_page": Links_pointing_to_page(url),
            "Statistical_report": Statistical_report(url),
        }
        return features
    except Exception as e:
        st.error(f"Error extracting features: {e}")
        return None

def generate_report(having_IP_Address, URL_Length, Shortining_Service, having_At_Symbol, double_slash_redirecting, Prefix_Suffix, having_Sub_Domain, SSLfinal_State, Domain_registeration_length, Favicon, port, HTTPS_token, Request_URL, URL_of_Anchor, Links_in_tags, SFH, Submitting_to_email, Abnormal_URL, Redirect, on_mouseover, RightClick, popUpWidnow, Iframe, age_of_domain, DNSRecord, web_traffic, Page_Rank, Google_Index, Links_pointing_to_page, Statistical_report):
    """
    Generates a detailed report on the features extracted from a given URL for phishing detection.

    Parameters:
    All the extracted features as individual inputs.

    Returns:
    A dictionary containing the feature analysis and a summary of the URL's safety status.
    """
    # Mapping feature scores to their meanings
    feature_analysis = {
        "having_IP_Address": ("IP Address Usage", "The URL uses an IP address instead of a domain name."),
        "URL_Length": ("URL Length", "The length of the URL exceeds the safe threshold."),
        "Shortining_Service": ("URL Shortening Service", "The URL uses a shortening service like bit.ly or tinyurl."),
        "having_At_Symbol": ("Presence of '@' Symbol", "The URL contains an '@' symbol, indicating phishing behavior."),
        "double_slash_redirecting": ("Double Slash Redirection", "The URL contains multiple '//' redirects."),
        "Prefix_Suffix": ("Prefix/Suffix in Domain", "The domain contains a hyphen ('-'), common in phishing URLs."),
        "having_Sub_Domain": ("Subdomain Count", "The URL contains excessive subdomains."),
        "SSLfinal_State": ("SSL State", "The URL is either HTTP or has an invalid SSL certificate."),
        "Domain_registeration_length": ("Domain Registration Length", "The domain registration duration is too short."),
        "Favicon": ("Favicon", "The URL uses an abnormal or phishing favicon."),
        "port": ("Port", "The URL uses unusual ports."),
        "HTTPS_token": ("HTTPS Token in Domain", "The domain name contains 'https', which is suspicious."),
        "Request_URL": ("External Resources in HTML", "The page loads excessive external resources."),
        "URL_of_Anchor": ("Anchor Tags", "Anchor tags redirect to external or suspicious domains."),
        "Links_in_tags": ("Links in Meta/Script/Link Tags", "Excessive links in meta, script, or link tags."),
        "SFH": ("Server Form Handler (SFH)", "The form handler points to unknown or blank domains."),
        "Submitting_to_email": ("Submitting to Email", "The URL allows form submission via email."),
        "Abnormal_URL": ("Abnormal URL", "The URL does not match the actual domain."),
        "Redirect": ("Redirection", "The URL redirects to another page."),
        "on_mouseover": ("OnMouseOver Events", "The page uses onmouseover JavaScript events."),
        "RightClick": ("Right-Click Disabled", "The page disables right-click functionality."),
        "popUpWidnow": ("Popup Windows", "The page uses popup windows."),
        "Iframe": ("Iframes", "The page contains iframe tags."),
        "age_of_domain": ("Domain Age", "The domain age is less than six months."),
        "DNSRecord": ("DNS Record", "The domain has invalid or missing DNS records."),
        "web_traffic": ("Web Traffic", "The web traffic is abnormally low."),
        "Page_Rank": ("Page Rank", "The page rank is too low."),
        "Google_Index": ("Google Index", "The URL is not indexed in Google."),
        "Links_pointing_to_page": ("Links Pointing to Page", "There are no links pointing to the page."),
        "Statistical_report": ("Statistical Report", "The URL matches a known phishing or malicious pattern."),
    }

    
    prompt = PromptTemplate.from_template(feature_analysis) 

    try:
        chat = ChatGroq(api_key=GROQ_API, model="llama3-70b-8192", temperature=0.5)
        chain = LLMChain(llm=chat, prompt=prompt)
        diet_plan = chain.run(features)
        return diet_plan
    except Exception as e:
        raise Exception(f"An error occurred while generating the diet plan: {e}") 
    
# Page Configuration
st.set_page_config(
    page_title="Phishing Website Detection",
    page_icon="🔒",
    layout="centered"
)


# App Title
st.title("🔒 Phishing Website Detection App")
st.markdown("Enter a website URL below, and we'll check whether it's legitimate or phishing.")

# Input for Website URL
url = st.text_input("🌐 Enter Website URL", placeholder="e.g., http://example.com")

# Prediction Button
if st.button("🚀 Detect Phishing"):
    if url:
        try:
            # Simulate feature extraction
            features = extract_features(url)  # Assuming this function exists
            if features:
                # Convert features to DataFrame
                features_df = pd.DataFrame([features])
                preprocessed_features = preprocess_pipeline.transform(features_df)  # Assuming preprocess_pipeline exists
                prediction = model.predict(preprocessed_features)[0]  # Assuming model is loaded
                prediction_proba = model.predict_proba(preprocessed_features)[0]  # Assuming model is loaded

                # Display results
                if prediction == 1:
                    st.success("✅ The website is **Legitimate**.")
                    st.metric(label="Confidence", value=f"{max(prediction_proba) * 100:.2f}%", delta="+")
                else:
                    st.error("🚨 The website is **Phishing**.")
                    st.metric(label="Confidence", value=f"{max(prediction_proba) * 100:.2f}%", delta="-")
            else:
                st.warning("Unable to extract features from the URL.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a URL before detecting.")

# Phishing Website Examples Section
with st.expander("📋 **Examples of Phishing Websites**", expanded=False):
    st.markdown("""
    ### ⚠️ **Known Phishing Websites**
    Below are examples of phishing websites. Be cautious of these types of URLs:
    """)

    examples = [
        ("http://login.yourbank-secure.com", "Fake bank login page"),
        ("http://paypal.account-verify.com", "Fake PayPal account verification"),
        ("http://secure-update-payment.com", "Fake payment update page"),
        ("http://facebook-security-alert.com", "Fake Facebook security alert"),
        ("http://amazon-refund-claim.com", "Fake Amazon refund page"),
        ("https://att-108422-105888.square.site/", "Reported phishing site (Fishtank)"),
        ("https://att-new-345689090rt67ue4t3454svdf04b8fsd5a...", "Reported phishing site (Fishtank)"),
    ]

    # Display examples with interactive cards
    for example, description in examples:
        st.markdown(f"""
        <div style="padding: 10px; margin-bottom: 10px; border: 1px solid #FF4B4B; border-radius: 8px; background-color: #FFEDED;">
            <p style="font-size: 16px; margin: 0;">
                <strong>🔗 <a href="{example}" target="_blank" style="text-decoration: none; color: #D92121;">{example}</a></strong>
            </p>
            <p style="margin: 0; font-size: 14px; color: #333;">{description}</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Always verify the legitimacy of a website before entering sensitive information.")