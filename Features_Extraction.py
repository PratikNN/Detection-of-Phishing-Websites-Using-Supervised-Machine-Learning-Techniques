#!/usr/bin/env python
# coding: utf-8




# # Dynamic Features Extraction

# In[633]:


import ipaddress
import re
import urllib.request
from bs4 import BeautifulSoup
import socket
import requests
from googlesearch import search
import whois
from datetime import datetime
import time
from dateutil.parser import parse as date_parse
import sys
from patterns import *


# In[634]:


def prepare_url(url):
    if not re.match(r"^https?", url):
        url = "http://" + url
    return url


# In[635]:


def get_soup(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
    except:
        response = ""
        soup = -999
    return soup


# In[636]:


def find_domain(url):
    domain = re.findall(r"://([^/]+)/?", url)[0]
    if re.match(r"^.",domain):
        domain = domain.replace("www.","")
    return domain


# In[637]:


def whois_response(domain):
    response = whois.whois(domain)
    return response


# In[638]:


def find_global_rank(domain):
    rank_checker_response = requests.post("https://checkpagerank.net/", {
        "name": domain })
    try:
        global_rank = int(re.findall(r"Global Rank: ([0-9]+)", rank_checker_response.text)[0])
    except:
        global_rank = -1
    return  global_rank
   


# In[639]:


def having_ip_address(url):
    try:
        ipaddress.ip_address(url)
        return -1
    except:
        return 1


# In[640]:


def url_length(url):
    if len(url) < 54:
        return 1
    if 54 <= len(url) <= 75:
        return 0
    return -1


# In[641]:


def shortening_services(url):
    match=re.search('bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                    'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                    'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                    'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                    'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                    'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                    'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net',url)
    if match:
        return -1
    else:
        return 1


# In[642]:


def having_at_symbol(url):
    if re.findall("@", url):
        return -1
    else:
        return 1


# In[643]:


def double_slash_redirecting(url):
    last_double_slash = url.rfind('//')
    return -1 if last_double_slash > 6 else 1


# In[644]:


def prefix_suffix(url):
    if re.findall(r"https?://[^\-]+-[^\-]+/", url):
            return -1
    else:
        return 1


# In[645]:


def having_sub_domain(url):
    if having_ip_address(url) == -1:
        match = re.search(
            '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
            '([01]?\\d\\d?|2[0-4]\\d|25[0-5]))|(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}',
            url)
        pos = match.end()
        url = url[pos:]
    num_dots = [x.start() for x in re.finditer(r'\.', url)]
    if len(num_dots) <= 3:
        return 1
    elif len(num_dots) == 4:
        return 0
    else:
        return -1


# In[646]:


def ssl_final_state(response):
    if len(response)>50:
        return 1
    else:
        return -1


# In[647]:


def domain_reg_length(whois_response):
    expiration_date = whois_response.expiration_date
  
    try:
        expiration_date=str(expiration_date)
        today = time.strftime('%Y-%m-%d')
        exp_date=expiration_date.split()[0]
        val=(int(exp_date.split('-')[0])-int(today.split('-')[0]))*365
        
        if val / 365 <1:
            return -1
        else:
            return 1
    except:
        return -1


# In[648]:


def favicon(soup,url,domain):
    if soup==-999:
        return -1
    else:
        for head in soup.find_all('head'):
            for head.link in soup.find_all('link', href=True):
                dots = [x.start() for x in re.finditer(r'\.', head.link['href'])]
                return 1 if url in head.link['href'] or len(dots) == 1 or domain in head.link['href'] else -1
    return 1

        


# In[649]:


def port(domain):
    try:
        port = domain.split(":")[1]
        if port:
            return -1
        else:
            return 1
    except:
        return 1


# In[650]:


def https_token(url):
    if re.findall(r"^https://", url):
        return 1
    else:
        return -1


# In[651]:


def request_url(url, soup, domain):
    i = 0
    success = 0
    if soup==-999:
        return -1
    else:
        for img in soup.find_all('img', src=True):
            dots = [x.start() for x in re.finditer(r'\.', img['src'])]
            if url in img['src'] or domain in img['src'] or len(dots) == 1:
                success = success + 1
            i = i + 1

        for audio in soup.find_all('audio', src=True):
            dots = [x.start() for x in re.finditer(r'\.', audio['src'])]
            if url in audio['src'] or domain in audio['src'] or len(dots) == 1:
                success = success + 1
            i = i + 1

        for embed in soup.find_all('embed', src=True):
            dots = [x.start() for x in re.finditer(r'\.', embed['src'])]
            if url in embed['src'] or domain in embed['src'] or len(dots) == 1:
                success = success + 1
            i = i + 1

        for i_frame in soup.find_all('i_frame', src=True):
            dots = [x.start() for x in re.finditer(r'\.', i_frame['src'])]
            if url in i_frame['src'] or domain in i_frame['src'] or len(dots) == 1:
                success = success + 1
            i = i + 1

        try:
            percentage = success / float(i) * 100
        except:
            return 1

        if percentage < 22.0:
            return 1
        elif 22.0 <= percentage < 61.0:
            return 0
        else:
            return -1


# In[652]:


def url_of_anchor(url,soup,domain):
    percentage = 0
    i = 0
    unsafe=0
    if soup == -999:
        return -1
    else:
        for a in soup.find_all('a', href=True):
        
            if "#" in a['href'] or "javascript" in a['href'].lower() or "mailto" in a['href'].lower() or not (url in a['href'] or domain in a['href']):
                unsafe = unsafe + 1
            i = i + 1
        try:
            percentage = unsafe / float(i) * 100
        except:
            return 1
        if percentage < 31.0:
            return 1
        elif ((percentage >= 31.0) and (percentage < 67.0)):
            return 0
        else:
            return -1


# In[653]:


def links_in_tags(url, soup, domain):
    i=0
    success =0
    if soup == -999:
        return -1
    else:
        for link in soup.find_all('link', href=True):
            dots = [x.start() for x in re.finditer(r'\.', link['href'])]
            if url in link['href'] or domain in link['href'] or len(dots) == 1:
                success = success + 1
            i = i + 1

        for script in soup.find_all('script', src=True):
            dots = [x.start() for x in re.finditer(r'\.', script['src'])]
            if url in script['src'] or domain in script['src'] or len(dots) == 1:
                success = success + 1
            i = i + 1
        try:
            percentage = success / float(i) * 100
        except:
            return 1

        if percentage < 17.0:
            return 1
        elif 17.0 <= percentage < 81.0:
            return 0
        else:
            return -1


# In[654]:


def sfh(url,soup,domain):
    if soup==-999:
        return -1
    else:
        for form in soup.find_all('form', action=True):
            if form['action'] == "" or form['action'] == "about:blank":
                return -1
            elif url not in form['action'] and domain not in form['action']:
                return 0
            else:
                return 1
    return 1


# In[655]:


def submitting_to_email(soup):
    if soup==-999:
        return -1
    else:
        for form in soup.find_all('form', action=True):
            return -1 if "mailto:" in form['action'] else 1
    return 1


# In[656]:


def abnormal_url(domain, url):
    match = re.search(domain, url)
    return 1 if match else -1


# In[657]:


def redirect(url):
    try:
        response=requests.get(url)
        if response == "":
            return -1
        else:
            if len(response.history) <= 1:
                return -1
            elif len(response.history) <= 4:
                return 0
            else:
                return 1
    except:
        return -1


# In[658]:


def on_mouse_over(url):
    try:
        response=requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if response == "" :
            return -1
        else:
            if re.findall("<script>.+onmouseover.+</script>", response.text):
                return -1
            else:
                return 1
    except:
        return -1


# In[659]:


def right_click(url):
    try:
        response=requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if response == "":
            return -1
        else:
            if re.findall(r"event.button == 2", response.text):
                return -1
            else:
                return 1
    except:
        return -1


# In[660]:


def popup_window(url):
    try:
        response=requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if response == "":
            return -1
        else:
            if re.findall(r"prompt\(", response.text):
                return -1
            else:
                return 1
    except:
        return -1


# In[661]:


def iframe(url):
    try:
        response=requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if response == "":
            return -1
        else:
            if re.findall(r"[<iframe>|<frameBorder>]", response.text):
                return 1
            else:
                return -1
    except:
        return -1


# In[662]:


def age_of_domain(whois_response):
    registration_date = whois_response.creation_date

    try:
        registration_date=str(registration_date)
        today = time.strftime('%Y-%m-%d')
        reg_date=registration_date.split()[0]
        val=(int(today.split('-')[0])-int(reg_date.split('-')[0]))*365
        
        if val / 365 <= 1:
            return -1
        else:
            return 1
    except:
        return -1


# In[663]:


def dns_record(domain):
    dns = -1
    try:
        d = whois.whois(domain)
        dns=1
    except:
        dns=-1
    if dns == -1:
        return -1
    else:
        return 1
    


# In[664]:


def web_traffic(url):
    try:
        rank = BeautifulSoup(urllib.request.urlopen("http://data.alexa.com/data?cli=10&dat=s&url=" + url).read(), "xml").find("REACH")['RANK']
        rank= int(rank)
        if (rank<100000):
            return 1
        else:
            return 0
    except TypeError:
        return -1


# In[665]:


def page_rank(global_rank):
    try:
        if global_rank > 0 and global_rank < 10000:
            return 1
        else:
            return -1
    except:
        return -1


# In[666]:


def google_index(url):
    site = search(url, 5)
    return 1 if site else -1


# In[667]:


def links_pointing_to_page(url):
    try:
        response=requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        number_of_links = len(re.findall(r"<a href=", response.text))
        if number_of_links <= 45:
            return 1
        elif number_of_links <= 60:
            return 0
        else:
            return -1
    except:
        return -1


# In[668]:


def statistical_report(url,domain):
    url_match=re.search('at\.ua|usa\.cc|baltazarpresentes\.com\.br|pe\.hu|esy\.es|hol\.es|sweddy\.com|myjino\.ru|96\.lt|ow\.ly',url)
    try:
        ip_address=socket.gethostbyname(domain)
        ip_match=re.search('146\.112\.61\.108|213\.174\.157\.151|121\.50\.168\.88|192\.185\.217\.116|78\.46\.211\.158|181\.174\.165\.13|46\.242\.145\.103|121\.50\.168\.40|83\.125\.22\.219|46\.242\.145\.98|'
                           '107\.151\.148\.44|107\.151\.148\.107|64\.70\.19\.203|199\.184\.144\.27|107\.151\.148\.108|107\.151\.148\.109|119\.28\.52\.61|54\.83\.43\.69|52\.69\.166\.231|216\.58\.192\.225|'
                           '118\.184\.25\.86|67\.208\.74\.71|23\.253\.126\.58|104\.239\.157\.210|175\.126\.123\.219|141\.8\.224\.221|10\.10\.10\.10|43\.229\.108\.32|103\.232\.215\.140|69\.172\.201\.153|'
                           '216\.218\.185\.162|54\.225\.104\.146|103\.243\.24\.98|199\.59\.243\.120|31\.170\.160\.61|213\.19\.128\.77|62\.113\.226\.131|208\.100\.26\.234|195\.16\.127\.102|195\.16\.127\.157|'
                           '34\.196\.13\.28|103\.224\.212\.222|172\.217\.4\.225|54\.72\.9\.51|192\.64\.147\.141|198\.200\.56\.183|23\.253\.164\.103|52\.48\.191\.26|52\.214\.197\.72|87\.98\.255\.18|209\.99\.17\.27|'
                           '216\.38\.62\.18|104\.130\.124\.96|47\.89\.58\.141|78\.46\.211\.158|54\.86\.225\.156|54\.82\.156\.19|37\.157\.192\.102|204\.11\.56\.48|110\.34\.231\.42',ip_address)
        if url_match:
            return -1
        elif ip_match:
            return -1
        else:
            return 1
    except:
        return -1


    


# In[669]:


def generate_dataset(url):
    url=prepare_url(url)
    soup=get_soup(url)
    domain=find_domain(url)
    response=whois_response(domain)
    global_rank=find_global_rank(domain)
    data_set=[]
    data_set.append(having_ip_address(url))
    data_set.append(url_length(url))
    data_set.append(shortening_services(url))
    data_set.append(having_at_symbol(url))
    data_set.append(double_slash_redirecting(url))
    data_set.append(prefix_suffix(url))
    data_set.append(having_sub_domain(url))
    data_set.append(ssl_final_state(response.text))
    data_set.append(domain_reg_length(response))
    data_set.append(favicon(soup,url,domain))
    data_set.append(port(domain))
    data_set.append(https_token(url))
    data_set.append(request_url(url,soup,domain))
    data_set.append(url_of_anchor(url,soup,domain))
    data_set.append(links_in_tags(url,soup,domain))
    data_set.append(sfh(url,soup,domain))
    data_set.append(submitting_to_email(soup))
    data_set.append(abnormal_url(domain,url))
    data_set.append(redirect(url))
    data_set.append(on_mouse_over(url))
    data_set.append(right_click(url))
    data_set.append(popup_window(url))
    data_set.append(iframe(url))
    data_set.append(age_of_domain(response))
    data_set.append(dns_record(domain))
    data_set.append(web_traffic(url))
    data_set.append(page_rank(global_rank))
    data_set.append(google_index(url))
    data_set.append(links_pointing_to_page(url))
    data_set.append(statistical_report(url,domain))
    return data_set,global_rank
	






