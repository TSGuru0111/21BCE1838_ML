import requests
from bs4 import BeautifulSoup

def scrape_articles():
    url = 'https://bbc.com/news'  # Replace this with a valid news URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    # Assuming articles are inside <h2> tags with a class 'title'
    for item in soup.find_all('h2', class_='title'):
        title = item.get_text()
        link = item.find('a')['href']
        articles.append({
            "title": title,
            "link": link,
            "content": fetch_article_content(link)  # Fetch the content of the article
        })
    
    return articles

def fetch_article_content(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Assuming the article content is within <div> with class 'article-body'
    article_body = soup.find('div', class_='article-body')
    if article_body:
        return article_body.get_text()
    return ''
