import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime

TRIMBLE_IR_URL = "https://investor.trimble.com/events-and-presentations/default.aspx"

def build_rss_feed():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    res = requests.get(TRIMBLE_IR_URL, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch IR page: status code {res.status_code}")
        
    soup = BeautifulSoup(res.text, "html.parser")
    
    # Initialize RSS Structure
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "Phil Sawarynski (Trimble CFO) - Public Content Feed"
    ET.SubElement(channel, "link").text = TRIMBLE_IR_URL
    ET.SubElement(channel, "description").text = "Auto-updated feed for webcasts, conferences, and earnings transcripts featuring Trimble CFO Phil Sawarynski."
    
    # Scrape Q4 IR event containers
    events = soup.find_all("div", class_="module_item") or soup.find_all("tr", class_="module_row")
    
    count = 0
    for event in events:
        text = event.get_text()
        
        # Filter for Phil Sawarynski or Earnings Calls
        if "Sawarynski" in text or "Phil" in text or "Earnings" in text:
            link_tag = event.find("a", href=True)
            if not link_tag:
                continue
                
            title = link_tag.get_text(strip=True) or "Trimble IR Event"
            event_url = link_tag['href']
            if not event_url.startswith("http"):
                event_url = f"https://investor.trimble.com{event_url}"
                
            date_tag = event.find("div", class_="module_date-time") or event.find("span", class_="module_date-text")
            pub_date = date_tag.get_text(strip=True) if date_tag else datetime.utcnow().strftime("%a, %d %b %Y 00:00:00 GMT")
            
            # Create RSS item
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "link").text = event_url
            ET.SubElement(item, "description").text = f"Public appearance / webcast: {title}"
            ET.SubElement(item, "pubDate").text = pub_date
            count += 1
            
    tree = ET.ElementTree(rss)
    if hasattr(ET, 'indent'):
        ET.indent(tree, space="\t", level=0)
        
    tree.write("feed.xml", encoding="utf-8", xml_declaration=True)
    print(f"Successfully generated feed.xml with {count} items.")

if __name__ == "__main__":
    build_rss_feed()