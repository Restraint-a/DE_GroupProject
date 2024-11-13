import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import json
import re
from word_cloud import get_word_counts,get_wordcloud
import os

# 确保nltk的停用词被下载（如果没下载过）
import nltk
nltk.download("punkt")
nltk.download("stopwords")

def get_search_links(query):
    """
    根据查询字符串获取Google搜索结果中的链接。

    参数:
    query (str): 要搜索的查询字符串。

    返回:
    list: 一个包含搜索结果中URL的列表。
    """
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    urls = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and ("/url?q=" in href or href.startswith("http")) and "translate.google.com/translate" not in href:
            if "/url?q=" in href:
                href = href.split("/url?q=")[1].split("&")[0]
            urls.append(href)
    print("url length:", len(urls))
    return urls[10:40]

def fetch_article_text(url):
    """
    根据给定的URL获取文章的文本内容，并过滤出只包含英文字符的内容。

    参数:
    url (str): 文章的URL。

    返回:
    str: 过滤后的英文文本内容。
    """
    try:
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = " ".join([p.get_text() for p in soup.find_all("p")])
        english_text = re.sub(r"[^a-zA-Z\s]", "", text)
        return english_text
    except requests.RequestException as e:
        print(f"请求失败: {url} 错误: {e}")
        return ""

def count_words_in_articles(urls):
    """
    统计一组文章中每个单词的出现次数，排除停用词。

    参数:
    urls (list of str): 文章的URL列表。

    返回:
    Counter: 包含每个单词及其出现次数的Counter对象。
    """
    all_words = Counter()
    stop_words = set(stopwords.words("english"))
    for url in urls:
        print(f"正在处理: {url}")
        article_text = fetch_article_text(url)
        words = word_tokenize(article_text.lower())
        filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
        all_words.update(filtered_words)
    return all_words

def save_to_json(word_counts, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(word_counts, f, indent=4)
    print(f"结果已保存到 {filename}")

def dynamic_crawl(query):
    """
    动态爬取数据并保存结果。

    参数:
    query (str): 查询关键词。
    """
    urls = get_search_links(query)
    print("urls length: ", len(urls))
    print("urls :", urls)
    word_counts = count_words_in_articles(urls)
    save_to_json(word_counts, filename=f"{query}_word_counts.json")

def main():
    while True:
        query = input("Please input query key word：")
        dynamic_crawl(query)
        get_wordcloud(get_word_counts(query),query)

if __name__ == "__main__":
    main()
