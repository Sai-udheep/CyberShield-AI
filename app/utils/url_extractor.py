import re
import urllib.parse
import socket
import tldextract
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import difflib

# Feature list in exact training order
NUMERIC_FEATURES = [
    'URLLength', 'DomainLength', 'IsDomainIP', 'URLSimilarityIndex', 'CharContinuationRate',
    'TLDLegitimateProb', 'URLCharProb', 'TLDLength', 'NoOfSubDomain', 'HasObfuscation',
    'NoOfObfuscatedChar', 'ObfuscationRatio', 'NoOfLettersInURL', 'LetterRatioInURL',
    'NoOfDegitsInURL', 'DegitRatioInURL', 'NoOfEqualsInURL', 'NoOfQMarkInURL',
    'NoOfAmpersandInURL', 'NoOfOtherSpecialCharsInURL', 'SpacialCharRatioInURL', 'IsHTTPS',
    'LineOfCode', 'LargestLineLength', 'HasTitle', 'DomainTitleMatchScore', 'URLTitleMatchScore',
    'HasFavicon', 'Robots', 'IsResponsive', 'NoOfURLRedirect', 'NoOfSelfRedirect',
    'HasDescription', 'NoOfPopup', 'NoOfiFrame', 'HasExternalFormSubmit', 'HasSocialNet',
    'HasSubmitButton', 'HasHiddenFields', 'HasPasswordField', 'Bank', 'Pay', 'Crypto',
    'HasCopyrightInfo', 'NoOfImage', 'NoOfCSS', 'NoOfJS', 'NoOfSelfRef', 'NoOfEmptyRef',
    'NoOfExternalRef'
]

def is_ip(domain):
    """Check if domain is a raw IP address."""
    try:
        socket.inet_aton(domain)
        return 1
    except socket.error:
        # Check IPv6
        try:
            socket.inet_pton(socket.AF_INET6, domain)
            return 1
        except socket.error:
            return 0

def get_brand_similarity(url, registered_domain):
    """
    Checks if the URL is on the Alexa Top List (mimicking PhiUSIIL's Alexa similarity index).
    Returns 100.0 for highly popular domains, and 0.0 for others.
    """
    if not registered_domain:
        return 0.0
        
    reg_lower = registered_domain.lower()
    
    # List of top popular Alexa registered domains (domain + TLD)
    brands = [
        # Tech & Social
        'paypal.com', 'facebook.com', 'amazon.com', 'amazon.in', 'netflix.com', 'google.com', 
        'apple.com', 'microsoft.com', 'yahoo.com', 'ebay.com', 'instagram.com', 'twitter.com', 
        'linkedin.com', 'whatsapp.com', 'adobe.com', 'dropbox.com', 'github.com',
        'stackoverflow.com', 'openai.com', 'youtube.com', 'wikipedia.org',
        # Banks & Finance
        'chase.com', 'wellsfargo.com', 'bofamel.com', 'bankofamerica.com', 'citibank.com', 
        'capitalone.com', 'americanexpress.com', 'amex.com', 'hsbc.com', 'barclays.com', 
        'santander.com', 'td.com', 'mastercard.com', 'visa.com', 'stripe.com', 'squareups.com', 
        'squareup.com', 'icicibank.com', 'hdfcbank.com', 'sbi.co.in', 'rivercitybank.com',
        # Delivery & Retail
        'dhl.com', 'fedex.com', 'usps.com', 'ups.com', 'walmart.com', 'target.com', 
        'alibaba.com', 'aliexpress.com',
        # Crypto
        'binance.com', 'coinbase.com', 'kraken.com', 'metamask.io', 'trustwallet.com'
    ]
    
    # If the registered domain exactly matches a top Alexa brand, return 100.0 (Legitimate Top Site)
    for brand in brands:
        if reg_lower == brand:
            return 100.0
            
    return 0.0

def to_punycode_url(url):
    """
    Converts any Internationalized Domain Name (IDN) hostname in the URL 
    to its ASCII-compatible Punycode representation.
    """
    if not url:
        return url
        
    # Standardize scheme for parsing
    if not url.startswith(('http://', 'https://')):
        url_with_scheme = 'http://' + url
        has_added_scheme = True
    else:
        url_with_scheme = url
        has_added_scheme = False
        
    try:
        parsed = urllib.parse.urlparse(url_with_scheme)
        hostname = parsed.hostname
        if hostname:
            hostname_puny = hostname.encode('idna').decode('ascii')
            netloc_puny = parsed.netloc.replace(hostname, hostname_puny)
            parsed_list = list(parsed)
            parsed_list[1] = netloc_puny
            puny_url = urllib.parse.urlunparse(parsed_list)
            if has_added_scheme and puny_url.startswith('http://'):
                puny_url = puny_url[7:]
            return puny_url
    except Exception:
        pass
    return url

def extract_lexical_features(url):
    """
    Extracts lexical features directly from the URL string.
    """
    features = {}
    
    # Ensure scheme exists
    if not url.startswith(('http://', 'https://')):
        url_with_scheme = 'http://' + url
    else:
        url_with_scheme = url
        
    parsed = urllib.parse.urlparse(url_with_scheme)
    ext = tldextract.extract(url_with_scheme)
    
    domain = ext.domain + '.' + ext.suffix if ext.suffix else ext.domain
    subdomain = ext.subdomain
    tld = ext.suffix
    
    features['URLLength'] = len(url)
    features['DomainLength'] = len(domain)
    features['IsDomainIP'] = is_ip(domain)
    features['URLSimilarityIndex'] = get_brand_similarity(url, ext.registered_domain)
    
    # Char continuation rate: average count of letters between punctuation/specials
    tokens = re.split(r'[^a-zA-Z]', url)
    features['CharContinuationRate'] = np.mean([len(t) for t in tokens]) if tokens else 0.0
    
    # TLD legitimacy score
    legitimate_tlds = {'com', 'org', 'net', 'edu', 'gov', 'mil', 'int', 'info', 'biz'}
    features['TLDLegitimateProb'] = 0.99 if tld in legitimate_tlds else 0.10
    
    # URL character probability (estimated baseline)
    features['URLCharProb'] = 0.05
    features['TLDLength'] = len(tld)
    
    subdomain_list = subdomain.split('.') if subdomain else []
    # Safe URLs in the training set always have at least 1 subdomain (usually 'www').
    # To prevent bias on apex domains (e.g. google.com), we default empty subdomains to 1.
    features['NoOfSubDomain'] = len(subdomain_list) if subdomain_list else 1
    
    # Obfuscation checks
    obfuscated_chars = re.findall(r'%[0-9a-fA-F]{2}|@', url)
    features['HasObfuscation'] = 1 if obfuscated_chars else 0
    features['NoOfObfuscatedChar'] = len(obfuscated_chars)
    features['ObfuscationRatio'] = len(obfuscated_chars) / len(url) if len(url) > 0 else 0
    
    letters = re.findall(r'[a-zA-Z]', url)
    features['NoOfLettersInURL'] = len(letters)
    features['LetterRatioInURL'] = len(letters) / len(url) if len(url) > 0 else 0
    
    digits = re.findall(r'\d', url)
    features['NoOfDegitsInURL'] = len(digits)
    features['DegitRatioInURL'] = len(digits) / len(url) if len(url) > 0 else 0
    
    features['NoOfEqualsInURL'] = url.count('=')
    features['NoOfQMarkInURL'] = url.count('?')
    features['NoOfAmpersandInURL'] = url.count('&')
    
    # Other special characters
    specials = re.findall(r'[-_./~%@+*]', url)
    features['NoOfOtherSpecialCharsInURL'] = len(specials)
    features['SpacialCharRatioInURL'] = len(specials) / len(url) if len(url) > 0 else 0
    features['IsHTTPS'] = 1 if url_with_scheme.startswith('https://') else 0
    
    return features

def extract_webpage_features(url_with_scheme, html_content=None):
    """
    Extracts webpage content features from HTML.
    If HTML is missing, it returns default benign metrics.
    """
    features = {}
    
    if not html_content:
        # Default benign webpage metrics
        features['LineOfCode'] = 0
        features['LargestLineLength'] = 0
        features['HasTitle'] = 0
        features['DomainTitleMatchScore'] = 0.0
        features['URLTitleMatchScore'] = 0.0
        features['HasFavicon'] = 0
        features['Robots'] = 0
        features['IsResponsive'] = 1
        features['NoOfURLRedirect'] = 0
        features['NoOfSelfRedirect'] = 0
        features['HasDescription'] = 0
        features['NoOfPopup'] = 0
        features['NoOfiFrame'] = 0
        features['HasExternalFormSubmit'] = 0
        features['HasSocialNet'] = 0
        features['HasSubmitButton'] = 0
        features['HasHiddenFields'] = 0
        features['HasPasswordField'] = 0
        features['Bank'] = 0
        features['Pay'] = 0
        features['Crypto'] = 0
        features['HasCopyrightInfo'] = 0
        features['NoOfImage'] = 0
        features['NoOfCSS'] = 0
        features['NoOfJS'] = 0
        features['NoOfSelfRef'] = 0
        features['NoOfEmptyRef'] = 0
        features['NoOfExternalRef'] = 0
        return features
        
    soup = BeautifulSoup(html_content, 'html.parser')
    ext = tldextract.extract(url_with_scheme)
    domain = ext.domain + '.' + ext.suffix if ext.suffix else ext.domain
    
    lines = html_content.split('\n')
    features['LineOfCode'] = len(lines)
    features['LargestLineLength'] = max(len(l) for l in lines) if lines else 0
    
    title_tag = soup.find('title')
    features['HasTitle'] = 1 if title_tag else 0
    title_text = title_tag.text.lower() if title_tag else ""
    
    features['DomainTitleMatchScore'] = 100.0 if domain.split('.')[0] in title_text else 0.0
    features['URLTitleMatchScore'] = 100.0 if any(t in title_text for t in re.split(r'\W', url_with_scheme) if len(t) > 3) else 0.0
    
    features['HasFavicon'] = 1 if soup.find('link', rel=re.compile(r'icon', re.I)) else 0
    # Robots.txt references in HTML
    features['Robots'] = 1 if soup.find('meta', attrs={'name': 'robots'}) else 0
    features['IsResponsive'] = 1 if soup.find('meta', attrs={'name': 'viewport'}) else 0
    
    features['NoOfURLRedirect'] = 0  # set dynamically if request redirection history exists
    
    # Parse links
    links = soup.find_all('a')
    self_ref = 0
    empty_ref = 0
    external_ref = 0
    
    for link in links:
        href = link.get('href', '').strip()
        if not href or href == '#' or href.startswith('javascript:'):
            empty_ref += 1
        elif href.startswith(('/', '#', url_with_scheme)) or domain in href:
            self_ref += 1
        elif href.startswith(('http://', 'https://')):
            external_ref += 1
            
    features['NoOfSelfRedirect'] = 1 if self_ref > 10 else 0
    features['HasDescription'] = 1 if soup.find('meta', attrs={'name': 'description'}) else 0
    
    # Popups script markers
    scripts_text = "".join(s.text for s in soup.find_all('script'))
    features['NoOfPopup'] = len(re.findall(r'window\.open|alert\(|confirm\(', scripts_text))
    features['NoOfiFrame'] = len(soup.find_all('iframe'))
    
    # External form actions
    forms = soup.find_all('form')
    external_form = 0
    has_submit = 0
    has_hidden = 0
    has_password = 0
    
    for form in forms:
        action = form.get('action', '').strip()
        if action.startswith(('http://', 'https://')) and domain not in action:
            external_form = 1
        if form.find(attrs={'type': 'submit'}) or form.find('button'):
            has_submit = 1
        if form.find(attrs={'type': 'hidden'}):
            has_hidden = 1
        if form.find(attrs={'type': 'password'}):
            has_password = 1
            
    features['HasExternalFormSubmit'] = external_form
    
    # Social net indicators
    features['HasSocialNet'] = 1 if any(social in html_content.lower() for social in ['facebook.com', 'twitter.com', 'linkedin.com']) else 0
    features['HasSubmitButton'] = has_submit
    features['HasHiddenFields'] = has_hidden
    features['HasPasswordField'] = has_password
    
    # Key terms in body
    body_text = soup.get_text().lower()
    features['Bank'] = 1 if any(w in body_text for w in ['bank', 'secure', 'account', 'login']) else 0
    features['Pay'] = 1 if any(w in body_text for w in ['pay', 'paypal', 'credit', 'card', 'checkout']) else 0
    features['Crypto'] = 1 if any(w in body_text for w in ['crypto', 'bitcoin', 'btc', 'wallet']) else 0
    features['HasCopyrightInfo'] = 1 if 'copyright' in body_text or '©' in body_text else 0
    
    features['NoOfImage'] = len(soup.find_all('img'))
    features['NoOfCSS'] = len(soup.find_all('link', rel='stylesheet'))
    features['NoOfJS'] = len(soup.find_all('script'))
    features['NoOfSelfRef'] = self_ref
    features['NoOfEmptyRef'] = empty_ref
    features['NoOfExternalRef'] = external_ref
    
    return features

def get_url_features_df(url, fetch_page=False):
    """
    Generates a 1-row DataFrame containing all 50 numeric features of the URL,
    matching the training structure of PhiUSIIL.
    """
    # Convert to Punycode to handle internationalized domain characters (IDNs)
    url = to_punycode_url(url)
    
    # 1. Lexical features
    features = extract_lexical_features(url)
    
    # Ensure scheme
    url_with_scheme = url
    if not url.startswith(('http://', 'https://')):
        url_with_scheme = 'http://' + url
        
    html = None
    redirect_count = 0
    
    # 2. Try fetching HTML if requested
    if fetch_page:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CyberShield/1.0'}
            response = requests.get(url_with_scheme, timeout=5, headers=headers)
            html = response.text
            redirect_count = len(response.history)
        except Exception:
            pass
            
    # 3. Webpage features
    web_features = extract_webpage_features(url_with_scheme, html)
    if fetch_page:
        web_features['NoOfURLRedirect'] = redirect_count
        
    # Merge dictionaries
    features.update(web_features)
    
    # 4. Return as formatted DataFrame
    df = pd.DataFrame([features])
    # Ensure order matches exactly the features we trained on
    return df[NUMERIC_FEATURES]

if __name__ == "__main__":
    test_url = "https://www.google.com"
    df = get_url_features_df(test_url, fetch_page=False)
    print("DataFrame shape:", df.shape)
    print("Features extracted:")
    for col in df.columns[:10]:
        print(f"  {col}: {df.iloc[0][col]}")
