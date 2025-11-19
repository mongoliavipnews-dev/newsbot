import feedparser
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os

TELEGRAM_BOT_TOKEN = "8251030370:AAEO-Mp4k4g-iQCKF3RUqYJqYhCTDHX4dFE"
TELEGRAM_CHAT_ID = "-1003224734560"

BOT_TOKEN = TELEGRAM_BOT_TOKEN
CHAT_ID = TELEGRAM_CHAT_ID

SENT_FILE = "sent_entries.txt"
MAX_SENT_ENTRIES = 10000

def send_telegram_message(text):
    """Telegram руу мессеж илгээх"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram илгээхэд алдаа: {e}")
        return False

def load_sent_entries():
    """Илгээсэн мэдээллийн жагсаалтыг уншина"""
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            entries = f.read().splitlines()

            if len(entries) > MAX_SENT_ENTRIES:
                entries = entries[-MAX_SENT_ENTRIES:]

                with open(SENT_FILE, "w", encoding="utf-8") as fw:
                    fw.write("\n".join(entries))
            return set(entries)
    return set()

def save_sent_entry(entry):
    """Илгээсэн мэдээллийг хадгална"""
    with open(SENT_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def scrape_generic(url, site_name):
    """Ерөнхий scraping функц - олон төрлийн selector-ийг туршина"""
    articles = []
    
    selectors = [

        {'article': 'article', 'title': 'h2, h3, h1, .title, .post-title', 'link': 'a'},
        {'article': 'div.post, div.news-item, div.article-item', 'title': 'h2, h3, .title', 'link': 'a'},

        {'article': 'div.post, article.post', 'title': 'h2.entry-title, h3.entry-title', 'link': 'a'},

        {'article': 'div[class*="news"], div[class*="post"], div[class*="article"]', 'title': 'h2, h3, h4', 'link': 'a'},
        {'article': 'li.post, li.news-item', 'title': 'h2, h3, .title', 'link': 'a'},
    ]
    
    try:
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        for selector_set in selectors:
            items = soup.select(selector_set['article'])
            if items:
                for item in items[:5]:
                    try:
                        title_elem = item.select_one(selector_set['title'])
                        link_elem = item.select_one(selector_set['link'])
                        
                        if title_elem and link_elem:
                            title = title_elem.get_text(strip=True)
                            link = link_elem.get('href', '')
                            
                            if link and not link.startswith('http'):
                                from urllib.parse import urljoin
                                link = urljoin(url, link)
                            
                            if title and link and len(title) > 10:
                                articles.append({
                                    'title': title,
                                    'link': link,
                                    'source': site_name
                                })
                    except Exception:
                        continue
                
                if articles:
                    break
                
    except Exception as e:
        print(f"  ✗ {site_name} scrape хийхэд алдаа: {e}")
    
    return articles

RSS_FEEDS = {
    "📰 OLLOO.MN 📢": "https://olloo.mn/feed/",
    "📰 MongolTur.MN 📢": "https://mongoltur.mn/feed/",
    "📰 Ikon.mn 📢": "https://ikon.mn/rss/",
    "📰 MNB.MN 📢": "https://www.mnb.mn/rss",
    "📰 www.imedee.com 📢": "https://www.imedee.com/feed/",
    "📢 Urlag.mn 📰": "https://urlag.mn/post/feed",
    "📢 Dms.mn 📰": "https://dms.mn/medee/feed/",
    "📢 Mongolia.gov.mn 📰": "https://mongolia.gov.mn/feed",
}

SCRAPE_SITES = {
    "📢 News.mn 📰": "https://news.mn",
    "📢 Ema.gov.mn 📰": "https://ema.gov.mn/",
    
    # Newswire.mn
    "📢 Newswire.mn 📰": "https://newswire.mn/c/42",
    "📢 Newswire.mn 📰": "https://newswire.mn/c/91",
    "📢 Newswire.mn 📰": "https://newswire.mn/c/64",
    "📢 Newswire.mn 📰": "https://newswire.mn/c/83",
    "📢 Newswire.mn 📰": "https://newswire.mn/c/21",
    "📢 Newswire.mn 📰": "https://newswire.mn/c/30",
    "📢 Newswire.mn 📰": "https://newswire.mn/c/47",
    "📢 Newswire.mn 📰": "https://newswire.mn/c/49",
    "📢 Newswire.mn 📰": "https://newswire.mn/c/16",
    
    # Nuuts.mn
    "📢 Nuuts.mn 📰": "https://nuuts.mn/?cat=5",
    "📢 Nuuts.mn 📰": "https://nuuts.mn/?cat=7",
    "📢 Nuuts.mn 📰": "https://nuuts.mn/?cat=6",
    "📢 Nuuts.mn 📰": "https://nuuts.mn/?cat=9",
    "📢 Nuuts.mn 📰": "https://nuuts.mn/?cat=19",
    
    # Mongolcomment.mn
    "📢 Mongolcomment.mn 📰": "https://mongolcomment.mn/c/politics",
    "📢 Mongolcomment.mn 📰": "https://mongolcomment.mn/c/economy",
    "📢 Mongolcomment.mn 📰": "https://mongolcomment.mn/c/art",
    "📢 Mongolcomment.mn 📰": "https://mongolcomment.mn/c/sport",
    "📢 Mongolcomment.mn 📰": "https://mongolcomment.mn/c/advice",
    "📢 Mongolcomment.mn 📰": "https://mongolcomment.mn/c/technology",
    "📢 Mongolcomment.mn 📰": "https://mongolcomment.mn/c/yellow",
    "📢 Mongolcomment.mn 📰": "https://mongolcomment.mn/c/humuus",
    
    # Parliament.mn
    "📢 Parliament.mn 📰": "https://www.parliament.mn/nc/medeelel/",
    "📢 Parliament.mn 📰": "https://www.parliament.mn/nc/480/",
    "📢 Parliament.mn 📰": "https://www.parliament.mn/nc/237/",
    "📢 Parliament.mn 📰": "https://www.parliament.mn/nc/615/",
    
    # Itoim.mn
    "📢 Itoim.mn 📰": "https://itoim.mn/s/politic",
    "📢 Itoim.mn 📰": "https://itoim.mn/s/politic/court",
    "📢 Itoim.mn 📰": "https://itoim.mn/s/politic/government",
    "📢 Itoim.mn 📰": "https://itoim.mn/s/politic/political-parties",
    "📢 Itoim.mn 📰": "https://itoim.mn/s/politic/president",
    
    # Chuhal.mn
    "📢 Chuhal.mn 📰": "http://chuhal.mn/c/1",
    "📢 Chuhal.mn 📰": "http://chuhal.mn/c/4/",
    "📢 Chuhal.mn 📰": "http://chuhal.mn/c/137/",
    "📢 Chuhal.mn 📰": "http://chuhal.mn/c/10/",
    "📢 Chuhal.mn 📰": "http://chuhal.mn/c/12/",
    "📢 Chuhal.mn 📰": "http://chuhal.mn/c/8/",
    "📢 Chuhal.mn 📰": "http://chuhal.mn/c/7/",
    "📢 Chuhal.mn 📰": "http://chuhal.mn/c/131/",
    "📢 Chuhal.mn 📰": "http://chuhal.mn/c/136/",
    "📢 Chuhal.mn 📰": "http://chuhal.mn/c/134/",
    "📢 Chuhal.mn 📰": "http://chuhal.mn/c/138/",

    # Mminfo.mn
    "📢 Mminfo.mn 📰": "http://mminfo.mn/politics/home/",
    "📢 Mminfo.mn 📰": "http://mminfo.mn/categories/view/3/",
    "📢 Mminfo.mn 📰": "http://mminfo.mn/categories/view/7/",
    "📢 Mminfo.mn 📰": "http://mminfo.mn/",
    "📢 Mminfo.mn 📰": "http://mminfo.mn/categories/view/4/",
    "📢 Mminfo.mn 📰": "http://mminfo.mn/categories/view/5/",
    "📢 Mminfo.mn 📰": "http://mminfo.mn/categories/view/9/",
    
    # Zms.mn
    "📢 Zms.mn - politics 📰": "https://www.zms.mn/as/politics/",
    "📢 Zms.mn - niigem 📰": "https://www.zms.mn/as/niigem/",
    "📢 Zms.mn - kids 📰": "https://www.zms.mn/as/kids/",
    "📢 Zms.mn - world 📰": "https://www.zms.mn/as/world/",
    "📢 Zms.mn - bukh 📰": "https://www.zms.mn/as/bukh/",
    "📢 Zms.mn - search 📰": "https://www.zms.mn/as/search/",
    "📢 Zms.mn - sport 📰": "https://www.zms.mn/as/sport/",

    # Montsame.mn
    "📢 Montsame.mn - 8 📰": "https://montsame.mn/mn/more/8",
    "📢 Montsame.mn - 17 📰": "https://montsame.mn/mn/more/17/",
    "📢 Montsame.mn - 909 📰": "https://montsame.mn/mn/more/909/",
    "📢 Montsame.mn - 866 📰": "https://montsame.mn/mn/more/866/",
    "📢 Montsame.mn - 25 📰": "https://montsame.mn/mn/more/25/",
    "📢 Montsame.mn - 10 📰": "https://montsame.mn/mn/more/10/",
    "📢 Montsame.mn - 11 📰": "https://montsame.mn/mn/more/11/",
    "📢 Montsame.mn - 13 📰": "https://montsame.mn/mn/more/13/",

    # Sonin.mn
    "📢 Sonin.mn - 1": "https://sonin.mn/categorized/1/",
    "📢 Sonin.mn - 2": "https://sonin.mn/categorized/2/",   
    "📢 Sonin.mn - 7": "https://sonin.mn/categorized/7/",
    "📢 Sonin.mn - 8": "https://sonin.mn/categorized/8/",
    "📢 Sonin.mn - 9": "https://sonin.mn/categorized/9/",

    # Shuud.mn
    "📢 Shuud.mn - politics": "https://www.shuud.mn/as/politics/",
    "📢 Shuud.mn - laws": "https://www.shuud.mn/as/laws/",
    "📢 Shuud.mn - economics": "https://www.shuud.mn/as/economics/",
    "📢 Shuud.mn - society": "https://www.shuud.mn/as/society/",
    "📢 Shuud.mn - world": "https://www.shuud.mn/as/world/",
    "📢 Shuud.mn - art": "https://www.shuud.mn/as/art/",
    "📢 Shuud.mn - article": "https://www.shuud.mn/as/article/",

    # Dnn.mn
    "📢 Dnn.mn - main": "https://dnn.mn/category/",
    "📢 Dnn.mn - niigem": "https://dnn.mn/category/niigem/",
    "📢 Dnn.mn - soninii-dugaart": "https://dnn.mn/category/soninii-dugaart/",
    "📢 Dnn.mn - uls_tur": "https://dnn.mn/category/uls_tur/",
    "📢 Dnn.mn - gadaad": "https://dnn.mn/category/gadaad/",
    "📢 Dnn.mn - ediin_zasag": "https://dnn.mn/category/ediin_zasag/",
    "📢 Dnn.mn - urlag": "https://dnn.mn/category/urlag/",
    "📢 Dnn.mn - sport": "https://dnn.mn/category/sport/",
    "📢 Dnn.mn - video": "https://dnn.mn/category/video/",
    "📢 Dnn.mn - entertainment": "https://dnn.mn/category/entertainment/",

    # Caak.mn
    "📢 Caak.mn - essay": "https://www.caak.mn/category/essay/",
    "📢 Caak.mn - interesting": "https://www.caak.mn/category/interesting/",
    "📢 Caak.mn - heroes": "https://www.caak.mn/category/heroes/",
    "📢 Caak.mn - crime": "https://www.caak.mn/category/crime/",
    "📢 Caak.mn - knowledge": "https://www.caak.mn/category/knowledge/",
    "📢 Caak.mn - animals": "https://www.caak.mn/category/animals/",
    "📢 Caak.mn - mentor": "https://www.caak.mn/category/mentor/",
    "📢 Caak.mn - ai": "https://www.caak.mn/category/ai/",
    "📢 Caak.mn - space": "https://www.caak.mn/category/space/",
    "📢 Caak.mn - tehnology": "https://www.caak.mn/category/tehnology/",
    "📢 Caak.mn - psychology": "https://www.caak.mn/category/psychology/",
    "📢 Caak.mn - tips": "https://www.caak.mn/category/tips/",
    "📢 Caak.mn - people": "https://www.caak.mn/category/people/",
    "📢 Caak.mn - movie": "https://www.caak.mn/category/movie/",
    "📢 Caak.mn - travel": "https://www.caak.mn/category/travel/",
    "📢 Caak.mn - hobby": "https://www.caak.mn/category/hobby/",
    "📢 Caak.mn - foods": "https://www.caak.mn/category/foods/",
    "📢 Caak.mn - video": "https://www.caak.mn/category/video/",
    "📢 Caak.mn - beauty": "https://www.caak.mn/category/beauty/",
    "📢 Caak.mn - cars": "https://www.caak.mn/category/cars/",
    "📢 Caak.mn - fashion": "https://www.caak.mn/category/fashion/",
    "📢 Caak.mn - creativities": "https://www.caak.mn/category/creativities/",
    "📢 Caak.mn - funny": "https://www.caak.mn/category/funny/",
    "📢 Caak.mn - marketing": "https://www.caak.mn/category/marketing/",
    "📢 Caak.mn - openlist": "https://www.caak.mn/category/openlist/",

    # Gogo.mn
    "📢 Gogo.mn - i2": "https://gogo.mn/i/2/",
    "📢 Gogo.mn - i3": "https://gogo.mn/i/3/",
    "📢 Gogo.mn - i4": "https://gogo.mn/i/4/",
    "📢 Gogo.mn - i5": "https://gogo.mn/i/5/",
    "📢 Gogo.mn - i6": "https://gogo.mn/i/6/",
    "📢 Gogo.mn - i7": "https://gogo.mn/i/7/",
    "📢 Gogo.mn - i8": "https://gogo.mn/i/8/",
    "📢 Gogo.mn - i9": "https://gogo.mn/i/9/",
    "📢 Gogo.mn - i72": "https://gogo.mn/i/72/",
    "📢 Gogo.mn - i6876": "https://gogo.mn/i/6876/",
    "📢 Gogo.mn - i8608": "https://gogo.mn/i/8608/",
    "📢 Gogo.mn - i9676": "https://gogo.mn/i/9676/",
    "📢 Gogo.mn - i9681": "https://gogo.mn/i/9681/",
    "📢 Gogo.mn - i9682": "https://gogo.mn/i/9682/",
    "📢 Gogo.mn - i9683": "https://gogo.mn/i/9683/",
    "📢 Gogo.mn - corner21": "https://gogo.mn/corner/21/",
    "📢 Gogo.mn - corner7568": "https://gogo.mn/corner/7568/",
    "📢 Gogo.mn - corner9606": "https://gogo.mn/corner/9606/",
    "📢 Gogo.mn - corner9625": "https://gogo.mn/corner/9625/",
    "📢 Gogo.mn - corner9651": "https://gogo.mn/corner/9651/",
    "📢 Gogo.mn - corner9669": "https://gogo.mn/corner/9669/",
    "📢 Gogo.mn - corner9678": "https://gogo.mn/corner/9678/",
    "📢 Gogo.mn - corner9679": "https://gogo.mn/corner/9679/",
    "📢 Gogo.mn - lifestyle9612": "https://gogo.mn/lifestyle/4?catId=9612/",
    "📢 Gogo.mn - lifestyle9629": "https://gogo.mn/lifestyle/4?catId=9629/",
    "📢 Gogo.mn - lifestyle9652": "https://gogo.mn/lifestyle/4?catId=9652/",
    "📢 Gogo.mn - lifestyle9671": "https://gogo.mn/lifestyle/4?catId=9671/",
    "📢 Gogo.mn - lifestyle9673": "https://gogo.mn/lifestyle/4?catId=9673/",

    # Tug.mn
    "📺 Tug.mn - 23": "https://tug.mn/p/23/",
    "📺 Tug.mn - 41": "https://tug.mn/p/41/",
    "📺 Tug.mn - 43": "https://tug.mn/p/43/",
    "📺 Tug.mn - 42": "https://tug.mn/p/42/",
    "📺 Tug.mn - 24": "https://tug.mn/p/24/",
    "📺 Tug.mn - 28": "https://tug.mn/p/28/",
    "📺 Tug.mn - 37": "https://tug.mn/p/37/",
    "📺 Tug.mn - 52": "https://tug.mn/p/52/",
    "📺 Tug.mn - 54": "https://tug.mn/p/54/",

    # Lemonpress.mn
    "📺 Lemonpress.mn - economy": "https://lemonpress.mn/category/economy/",
    "📺 Lemonpress.mn - finance": "https://lemonpress.mn/category/finance/",
    "📺 Lemonpress.mn - technology": "https://lemonpress.mn/category/technology/",
    "📺 Lemonpress.mn - news": "http://lemonpress.mn/category/news/",
    "📺 Lemonpress.mn - market": "https://lemonpress.mn/category/market/",
    "📺 Lemonpress.mn - surtalchilgaa": "https://lemonpress.mn/category/surtalchilgaa/",
    "📺 Lemonpress.mn - interview": "https://lemonpress.mn/category/interview/",
    
    # Medee.mn
    "📺 Medee.mn - law": "https://medee.mn/category/law/",
    "📺 Medee.mn - politics": "https://medee.mn/category/politics/",
    "📺 Medee.mn - health": "https://medee.mn/category/health/",
    "📺 Medee.mn - economy": "https://medee.mn/category/economy/",
    "📺 Medee.mn - education": "https://medee.mn/category/education/",
    "📺 Medee.mn - community": "https://medee.mn/category/%D1%81ommunity/",

    # Eguur.mn
    "📺 Eguur.mn - uls-tur": "https://eguur.mn/category/%d1%83%d0%bb%d1%81-%d1%82%d3%a9%d1%80/",
    "📺 Eguur.mn - ediin-zasag": "https://eguur.mn/category/%d1%8d%d0%b4%d0%b8%d0%b9%d0%bd-%d0%b7%d0%b0%d1%81%d0%b0%d0%b3/",
    "📺 Eguur.mn - delhiy": "https://eguur.mn/category/%d0%b4%d1%8d%d0%bb%d1%85%d0%b8%d0%b9/",
    "📺 Eguur.mn - niigem": "https://eguur.mn/category/%d0%bd%d0%b8%d0%b9%d0%b3%d1%8d%d0%bc/",
    "📺 Eguur.mn - datagraphic": "https://eguur.mn/category/%d0%b4%d0%b0%d1%82%d0%b0%d0%b3%d1%80%d0%b0%d1%84%d0%b8%d0%ba/",
    "📺 Eguur.mn - sosial-trend": "https://eguur.mn/category/%d1%81%d0%be%d1%88%d0%b8%d0%b0%d0%bb-%d1%82%d1%80%d1%8d%d0%bd%d0%b4/",
    "📺 Eguur.mn - eguur-brend": "https://eguur.mn/category/%d1%8d%d0%b3%d2%af%d2%af%d1%80-%d0%b1%d1%80%d1%8d%d0%bd%d0%b4/",

    # News.zindaa.mn
    "📺 Zindaa.mn - uls-tur": "https://news.zindaa.mn/%D1%83%D0%BB%D1%81-%D1%82%D3%A9%D1%80/",
    "📺 Zindaa.mn - ediin-zasag": "https://news.zindaa.mn/%D1%8D%D0%B4%D0%B8%D0%B9%D0%BD-%D0%B7%D0%B0%D1%81%D0%B0%D0%B3/",
    "📺 Zindaa.mn - niigem": "https://news.zindaa.mn/%D0%BD%D0%B8%D0%B9%D0%B3%D1%8D%D0%BC/",
    "📺 Zindaa.mn - huul": "https://news.zindaa.mn/%D1%85%D1%83%D1%83%D0%BB%D1%8C/",
    "📺 Zindaa.mn - delhiy": "https://news.zindaa.mn/%D0%B4%D1%8D%D0%BB%D1%85%D0%B8%D0%B9/",
    "📺 Zindaa.mn - naadam2025": "https://news.zindaa.mn/%D0%BD%D0%B0%D0%B0%D0%B4%D0%B0%D0%BC-2025/",
    "📺 Zindaa.mn - urlag": "https://news.zindaa.mn/%D1%83%D1%80%D0%BB%D0%B0%D0%B3/",
    "📺 Zindaa.mn - toym": "https://news.zindaa.mn/%D0%A2%D0%BE%D0%B9%D0%BC/",

    # Leadnews.mn
    "📺 Leadnews.mn - main": "https://leadnews.mn/",

    # Emch.mn
    "📺 Emch.mn - health": "http://emch.mn/health/",
    "📺 Emch.mn - medicines": "http://emch.mn/medicines/",
    "📺 Emch.mn - children": "http://emch.mn/children/",
    "📺 Emch.mn - advice": "http://emch.mn/advice/",
    "📺 Emch.mn - doctors": "http://emch.mn/doctors/",
    "📺 Emch.mn - interview": "http://emch.mn/interview/",
    "📺 Emch.mn - photo": "http://emch.mn/photo/",
    "📺 Emch.mn - video": "http://emch.mn/video/",
    "📺 Emch.mn - pharmacy": "http://emch.mn/pharmacy/",
    "📺 Emch.mn - pain": "http://emch.mn/pain/",

    # Mongoljingoo.mn
    "📺 Mongoljingoo.mn - main": "https://www.mongoljingoo.mn/a?caterogyId=1/",

    # Ergelt.mn
    "📺 Ergelt.mn - news1": "https://ergelt.mn/news/1/",
    "📺 Ergelt.mn - news22": "https://ergelt.mn/news/22/",
    "📺 Ergelt.mn - news21": "https://ergelt.mn/news/21/",
    "📺 Ergelt.mn - news20": "https://ergelt.mn/news/20/",
    "📺 Ergelt.mn - news24": "https://ergelt.mn/news/24/",
    "📺 Ergelt.mn - news23": "https://ergelt.mn/news/23/",
    "📺 Ergelt.mn - news_full2": "https://ergelt.mn/news_full/2/",
    "📺 Ergelt.mn - news33": "https://ergelt.mn/news/33/",
    "📺 Ergelt.mn - news_full152": "https://ergelt.mn/news_full/152/",

    # 24tsag.mn
    "📺 24tsag.mn - politics": "https://www.24tsag.mn/as/politics/",
    "📺 24tsag.mn - economy": "https://www.24tsag.mn/as/economy/",
    "📺 24tsag.mn - social": "https://www.24tsag.mn/as/social/",
    "📺 24tsag.mn - world": "https://www.24tsag.mn/as/world/",
    "📺 24tsag.mn - travel": "https://www.24tsag.mn/as/travel/",
    "📺 24tsag.mn - photo": "https://www.24tsag.mn/as/24photo/",
    "📺 24tsag.mn - elchinsaid": "https://www.24tsag.mn/as/elchinsaid/",
    "📺 24tsag.mn - sport": "https://www.24tsag.mn/as/sport/",
    "📺 24tsag.mn - video": "https://www.24tsag.mn/as/video/",
    "📺 24tsag.mn - entertainment": "https://www.24tsag.mn/as/entertainment/",
    
    # Zarig.mn
    "📺 Zarig.mn - politics": "https://zarig.mn/politics/",
    "📺 Zarig.mn - society": "https://zarig.mn/society/",
    "📺 Zarig.mn - ta-zavtai-juu": "https://zarig.mn/%D1%82%D0%B0-%D0%B7%D0%B0%D0%B2%D1%82%D0%B0%D0%B9-%D1%8E%D1%83/",
    "📺 Zarig.mn - behind-the-scenes": "https://zarig.mn/behind-the-scenes/",
    "📺 Zarig.mn - ontsloh-surwaljilga": "https://zarig.mn/ontsloh-surwaljilga/",
    "📺 Zarig.mn - songuuli-2024": "https://zarig.mn/songuuli-2024/",
    "📺 Zarig.mn - busad": "https://zarig.mn/busad/",

    # Focus.mn
    "📺 Focus.mn - politics": "https://focus.mn/politics/",
    "📺 Focus.mn - tanyg-fokuslaya": "https://focus.mn/%D0%A2%D0%90%D0%9D%D0%AB%D0%93_%D0%A4%D0%9E%D0%9A%D0%A3%D0%A1%D0%9B%D0%90%D0%AF/",
    "📺 Focus.mn - fokuslav": "https://focus.mn/%D1%84%D0%BE%D0%BA%D1%83%D1%81%D0%BB%D0%B0%D0%B2/",
    "📺 Focus.mn - speak_out": "https://focus.mn/speak_out/",
    "📺 Focus.mn - people": "https://focus.mn/people/",
    "📺 Focus.mn - society": "https://focus.mn/society/",
    "📺 Focus.mn - live": "https://focus.mn/Live/",
    "📺 Focus.mn - foreign-news": "https://focus.mn/foreign-news/",
    "📺 Focus.mn - busad": "https://focus.mn/busad/",

    # Mass.mn
    "📺 Mass.mn - category4": "https://mass.mn/category/4/",
    "📺 Mass.mn - category5": "https://mass.mn/category/5/",
    "📺 Mass.mn - category6": "https://mass.mn/category/6/",
    "📺 Mass.mn - category30": "https://mass.mn/category/30/",
    "📺 Mass.mn - category12": "https://mass.mn/category/12/",
    "📺 Mass.mn - category17": "https://mass.mn/category/17/",
    "📺 Mass.mn - category23": "https://mass.mn/category/23/",
    "📺 Mass.mn - category33": "https://mass.mn/category/33/",

    # Mongolnews24.com
    "📺 Mongolnews24 - uls-tor": "https://mongolnews24.com/uls-tor/",
    "📺 Mongolnews24 - olon-ulsyn-medee": "https://mongolnews24.com/olon-ulsyn-medee/",
    "📺 Mongolnews24 - edijn-zasag": "https://mongolnews24.com/edijn-zasag/",
    "📺 Mongolnews24 - sport": "https://mongolnews24.com/sport/",
    "📺 Mongolnews24 - shinzhleh-uhaan-tehnologi": "https://mongolnews24.com/shinzhleh-uhaan-ba-tehnologi/",
    "📺 Mongolnews24 - nijgem": "https://mongolnews24.com/nijgem/",
    "📺 Mongolnews24 - eruul-mend": "https://mongolnews24.com/er%d2%af%d2%afl-mend/",
    "📺 Mongolnews24 - bolovsrol": "https://mongolnews24.com/bolovsrol/",
    "📺 Mongolnews24 - osol-hereg": "https://mongolnews24.com/osol-hereg/",
    "📺 Mongolnews24 - soyl-urlag": "https://mongolnews24.com/soyol-urlag/",
    "📺 Mongolnews24 - shou-biznes": "https://mongolnews24.com/shou-biznes/",

    # Sorgog.mn
    "📺 Sorgog.mn - category40": "http://sorgog.mn/news.php?category=40/",
    "📺 Sorgog.mn - category39": "http://sorgog.mn/news.php?category=39/",
    "📺 Sorgog.mn - category37": "http://sorgog.mn/news.php?category=37/",
    "📺 Sorgog.mn - category55": "http://sorgog.mn/news.php?category=55/",
    "📺 Sorgog.mn - category53": "http://sorgog.mn/news.php?category=53/",
    "📺 Sorgog.mn - category44": "http://sorgog.mn/news.php?category=44/",
    "📺 Sorgog.mn - category41": "http://sorgog.mn/news.php?category=41/",
    "📺 Sorgog.mn - category57": "http://sorgog.mn/news.php?category=57/",
    "📺 Sorgog.mn - category46": "http://sorgog.mn/news.php?category=46/",
    
    
    #Paparazzi.mn
    "📺 Paparazzi.mn - medeelel": "https://paparazzi.mn/news",
    "📺 Paparazzi.mn - video-medee": "https://paparazzi.mn/video",
    "📺 Paparazzi.mn - dotood": "https://paparazzi.mn/papin",
    "📺 Paparazzi.mn - gadaad": "https://paparazzi.mn/papout",
    "📺 Paparazzi.mn - content": "https://paparazzi.mn/photo",
    
    #Gereg.mn
    "📺 Gereg.mn - uls-tur": "https://gereg.mn/category/%d1%83%d0%bb%d1%81%d1%82%d3%a9%d1%80",
    "📺 Gereg.mn - soyl": "https://gereg.mn/category/%d1%81%d0%be%d1%91%d0%bb",
    "📺 Gereg.mn - ediin-zasag": "https://gereg.mn/category/%d1%8d%d0%b4%d0%b8%d0%b9%d0%bd-%d0%b7%d0%b0%d1%81%d0%b0%d0%b3",
    "📺 Gereg.mn - niigem": "https://gereg.mn/category/%d0%bd%d0%b8%d0%b9%d0%b3%d1%8d%d0%bc",
    "📺 Gereg.mn - baigali-orchin": "https://gereg.mn/category/%d0%b1%d0%b0%d0%b9%d0%b3%d0%b0%d0%bb%d1%8c-%d0%be%d1%80%d1%87%d0%b8%d0%bd",
    
    #Eagle.mn
    "📺 Eagle.mn - uls-tur": "https://eagle.mn/c/2",
    "📺 Eagle.mn - ediin-zasag": "https://eagle.mn/c/3",
    "📺 Eagle.mn - Niigem": "https://eagle.mn/c/4",
    "📺 Eagle.mn - Delhii-dahin": "https://eagle.mn/c/6",
    "📺 Eagle.mn - Urlag": "https://eagle.mn/c/7",
    "📺 Eagle.mn - Sport": "https://eagle.mn/c/8",
    
    #Dorgio.mn
    "📺 Dorgio.mn - uls-tur": "https://dorgio.mn/c/1",
    "📺 Dorgio.mn - ediin-zasag": "https://dorgio.mn/c/3",
    "📺 Dorgio.mn - Niigem": "https://dorgio.mn/c/2",
    "📺 Dorgio.mn - Technology": "https://dorgio.mn/c/5",
    "📺 Dorgio.mn - Business": "https://dorgio.mn/c/6",
    "📺 Dorgio.mn - Sport": "https://dorgio.mn/c/8",
    "📺 Dorgio.mn - soyl-urlag": "https://dorgio.mn/c/9",
    "📺 Dorgio.mn - zuvluguu": "https://dorgio.mn/c/10",
    "📺 Dorgio.mn - Chuluut": "https://dorgio.mn/c/11",
    "📺 Dorgio.mn - Char-medee": "https://dorgio.mn/c/12",
    "📺 Dorgio.mn - Yriltslaga": "https://dorgio.mn/c/20",
    
    #Erennews.mn
    "📺 Erennews.mn - Eren-survaljlah": "https://erennews.mn/c/7",
    "📺 Erennews.mn - uls-tur": "https://erennews.mn/c/1",
    "📺 Erennews.mn - Erengiin-tusgal": "https://erennews.mn/c/4",
    "📺 Erennews.mn - Niigem": "https://erennews.mn/c/3",
    "📺 Erennews.mn - Entertainment": "https://erennews.mn/c/22",
    "📺 Erennews.mn - Delhii": "https://erennews.mn/c/9",
    
    #Uchral.mn
    "📺 Uchral.mn - UIH-dahi-ajil": "https://uchral.mn/?menu=2",
    
    #Polit.mn
    "📺 Polit.mn - Zaluus-Uls-tur": "https://www.polit.mn/as/politics",
    "📺 Polit.mn - Social": "https://www.polit.mn/as/social",
    "📺 Polit.mn - Delhiin-uls-tur": "https://www.polit.mn/as/world",
    "📺 Polit.mn - Emegteichuudiin-manlailal": "https://www.polit.mn/as/emegteichuud",
    "📺 Polit.mn - Niigem": "https://www.polit.mn/as/niigem",
    
    #Peak.mn
    "📺 Peak.mn - Uurlakh-uu-Uchirlakh-uu": "https://peak.mn/category/uurlakh-uu-uchirlakh-uu?menu=19",
    "📺 Peak.mn - Bidnii-17-zorilt": "https://peak.mn/my17",
    "📺 Peak.mn - Sanhvvgiin-bolovsrol": "https://peak.mn/category/economics?menu=2",
    "📺 Peak.mn - Bi-neg-udaa": "https://peak.mn/category/bi-neg-udaa?menu=25",
    "📺 Peak.mn - Khunii-bagsh": "https://peak.mn/category/khunii-bagsh?menu=26",
    "📺 Peak.mn - Technology": "https://peak.mn/category/technology?menu=11",
    
    #Niitlelch.mn
    "📺 Niitlelch.mn - Uls-tur": "https://niitlelch.mn/%D0%B0%D0%BD%D0%B3%D0%B8%D0%BB%D0%B0%D0%BB/%d1%83%d0%bb%d1%81-%d1%82%d3%a9%d1%80/",
    "📺 Niitlelch.mn - Niigem": "https://niitlelch.mn/%D0%B0%D0%BD%D0%B3%D0%B8%D0%BB%D0%B0%D0%BB/%d0%bd%d0%b8%d0%b9%d0%b3%d1%8d%d0%bc/",
    "📺 Niitlelch.mn - Ediin-zasag": "https://niitlelch.mn/%D0%B0%D0%BD%D0%B3%D0%B8%D0%BB%D0%B0%D0%BB/%d1%8d%d0%b4%d0%b8%d0%b9%d0%bd-%d0%b7%d0%b0%d1%81%d0%b0%d0%b3/",
    "📺 Niitlelch.mn - Soyl-urlag": "https://niitlelch.mn/%D0%B0%D0%BD%D0%B3%D0%B8%D0%BB%D0%B0%D0%BB/%d1%81%d0%be%d1%91%d0%bb-%d1%83%d1%80%d0%bb%d0%b0%d0%b3/",
    "📺 Niitlelch.mn - Sport": "https://niitlelch.mn/%D0%B0%D0%BD%D0%B3%D0%B8%D0%BB%D0%B0%D0%BB/%d1%81%d0%bf%d0%be%d1%80%d1%82/",
    "📺 Niitlelch.mn - Eruul-mend": "https://niitlelch.mn/%D0%B0%D0%BD%D0%B3%D0%B8%D0%BB%D0%B0%D0%BB/%d1%8d%d1%80%d2%af%d2%af%d0%bb-%d0%bc%d1%8d%d0%bd%d0%b4/",
    "📺 Niitlelch.mn - Shinjleh-uhaan": "https://niitlelch.mn/%D0%B0%D0%BD%D0%B3%D0%B8%D0%BB%D0%B0%D0%BB/%d1%88%d0%b8%d0%bd%d0%b6%d0%bb%d1%8d%d1%85-%d1%83%d1%85%d0%b0%d0%b0%d0%bd/",
    
    #Fact.mn
    "📺 Fact.mn - Uls-tur": "https://www.fact.mn/category/%d1%83%d0%bb%d1%81-%d1%82%d3%a9%d1%80-2",
    "📺 Fact.mn - Ulaanbaatar-sonin": "https://www.fact.mn/category/%d0%bc%d1%8d%d0%b4%d1%8d%d1%8d%d0%bb%d1%8d%d0%bb-2/%d1%83%d0%bb%d0%b0%d0%b0%d0%bd%d0%b1%d0%b0%d0%b0%d1%82%d0%b0%d1%80",
    "📺 Fact.mn - Uul-uurhai": "https://www.fact.mn/category/%d1%83%d1%83%d0%bb-%d1%83%d1%83%d1%80%d1%85%d0%b0%d0%b9",
    "📺 Fact.mn - Delhii-dahind": "https://www.fact.mn/category/%d0%bc%d1%8d%d0%b4%d1%8d%d1%8d%d0%bb%d1%8d%d0%bb-2/%d0%b4%d1%8d%d0%bb%d1%85%d0%b8%d0%b9",
    "📺 Fact.mn - Medeelel": "https://www.fact.mn/category/%d0%bc%d1%8d%d0%b4%d1%8d%d1%8d%d0%bb%d1%8d%d0%bb-2",
    "📺 Fact.mn - Khumuus": "https://www.fact.mn/category/%d1%85%d2%af%d0%bc%d2%af%d2%af%d1%81-%d0%bd%d0%b8%d0%b9%d0%b3%d1%8d%d0%bc",
    "📺 Fact.mn - Bank-sankhuu": "https://www.fact.mn/category/%d0%b1%d0%b0%d0%bd%d0%ba-3",
    "📺 Fact.mn - Sonin-hachin": "https://www.fact.mn/category/%d1%81%d0%be%d0%bd%d0%b8%d0%bd-%d1%85%d0%b0%d1%87%d0%b8%d0%bd",
    
    #Ugluu.mn
    "📺 Ugluu.mn - Medee-medeelel": "https://ugluu.mn/category/info",
    "📺 Ugluu.mn - Bolovsrol": "https://ugluu.mn/category/edu",
    "📺 Ugluu.mn - Entertainment": "https://ugluu.mn/category/entertainment",
    "📺 Ugluu.mn - Zuvluguu": "https://ugluu.mn/category/%d0%b7%d3%a9%d0%b2%d0%bb%d3%a9%d0%b3%d3%a9%d3%a9-%d0%b7%d3%a9%d0%b2%d0%bb%d3%a9%d0%bc%d0%b6",
    "📺 Ugluu.mn - Shar-Medee": "https://ugluu.mn/category/yellow-page",
    "📺 Ugluu.mn - Oron-nutag": "https://ugluu.mn/category/country",
    "📺 Ugluu.mn - Irgenii-medeelel": "https://ugluu.mn/category/user-info",
}

def check_feeds():
    """RSS feeds болон вэб сайтуудыг шалгана"""
    sent_entries = load_sent_entries()
    new_count = 0
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] RSS feeds шалгаж байна...")
    for feed_name, feed_url in RSS_FEEDS.items():
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries[:3]:  # Feed бүрээс 3 мэдээ
                entry_id = entry.get('link', entry.get('id', ''))
                if entry_id and entry_id not in sent_entries:
                    title = entry.get('title', 'Гарчиггүй')
                    link = entry.get('link', '')
                    
                    message = f"<b>{feed_name}</b>\n\n{title}\n\n{link}"
                    
                    if send_telegram_message(message):
                        save_sent_entry(entry_id)
                        sent_entries.add(entry_id)
                        new_count += 1
                        print(f"  ✓ {feed_name}: {title[:50]}...")
                        time.sleep(2)
        except Exception as e:
            print(f"  ✗ RSS ({feed_name}) уншихад алдаа: {e}")
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Вэб сайтуудыг scrape хийж байна...")
    for site_name, site_url in SCRAPE_SITES.items():
        try:
            articles = scrape_generic(site_url, site_name)
            
            for article in articles[:2]:
                entry_id = article['link']
                if entry_id not in sent_entries:
                    message = f"<b>{article['source']}</b>\n\n{article['title']}\n\n{article['link']}"
                    
                    if send_telegram_message(message):
                        save_sent_entry(entry_id)
                        sent_entries.add(entry_id)
                        new_count += 1
                        print(f"  ✓ {site_name}: {article['title'][:50]}...")
                        time.sleep(2)
        except Exception as e:
            print(f"  ✗ {site_name} scrape хийхэд алдаа: {e}")
    
    print(f"\n{'='*50}")
    print(f"Нийт {new_count} шинэ мэдээ илгээгдлээ")
    print(f"{'='*50}\n")

def main():
    """Үндсэн функц"""
    print("="*50)
    print("Telegram мэдээний бот эхэллээ")
    print("="*50)
    
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE' or CHAT_ID == 'YOUR_CHAT_ID_HERE':
        print("\n⚠️  АНХААРУУЛГА: TELEGRAM_BOT_TOKEN болон TELEGRAM_CHAT_ID environment variables тохируулна уу!")
        print("Жишээ нь:")
        print("  export TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("  export TELEGRAM_CHAT_ID='your_chat_id'\n")
    
    while True:
        try:
            check_feeds()
            print(f"Дараагийн шалгалт: 180 секундын дараа...")
            time.sleep(180)  # 3 минут
        except KeyboardInterrupt:
            print("\n\nБот зогслоо.")
            break
        except Exception as e:
            print(f"Алдаа гарлаа: {e}")
            print("10 секундын дараа дахин оролдоно...")
            time.sleep(10)

if __name__ == "__main__":
    main()
