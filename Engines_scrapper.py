import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import json
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import time

# 确保nltk的停用词被下载（如果没下载过）
import nltk
nltk.download("punkt")
nltk.download("stopwords")

def get_search_links(query, engine="yahoo", max_pages=3):
    if engine == "google":
        base_url = f"https://www.google.com/search?q={query}&start="
    elif engine == "yahoo":
        base_url = f"https://search.yahoo.com/search?p={query}&b="
    else:
        raise ValueError("不支持的搜索引擎")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    urls = []
    for page in range(max_pages):
        if engine == "google":
            url = base_url + str(page * 10)
        elif engine == "yahoo":
            url = base_url + str(page * 7 + 1)

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        if engine == "google":
            for link in soup.find_all("a", href=True, jsname="UWckNb"):
                href = link.get("href")
                if href and ("/url?q=" in href or href.startswith("http")) and "translate.google.com/translate" not in href:
                    if "/url?q=" in href:
                        href = href.split("/url?q=")[1].split("&")[0]
                    urls.append(href)
        elif engine == "yahoo":
            for link in soup.find_all("a", href=True):
                href = link.get("href")
                if href and ("/url?q=" in href or href.startswith("http")) and ".search.yahoo.com" not in href:
                    if "/url?q=" in href:
                        href = href.split("/url?q=")[1].split("&")[0]
                    urls.append(href)

        time.sleep(1)  # 增加请求间隔，避免被封IP

    print(f"{engine} URL count:", len(urls))
    return urls[:10*max_pages]

def fetch_article_text(url):
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
        print(f"Request failed: {url} Error: {e}")
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
        print(f"Processing: {url}")
        article_text = fetch_article_text(url)
        if article_text:
            words = word_tokenize(article_text.lower())
            filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
            all_words.update(filtered_words)
            time.sleep(1)  # 增加请求间隔，避免被封IP

    return all_words

def save_to_json(word_counts, filename="engine_word_counts.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(word_counts, f, indent=4)
    print(f"Results saved to {filename}")

def plot_word_frequency(word_counts, title):
    """
    生成词频统计的柱状图。

    参数:
    word_counts (Counter): 词频统计的Counter对象。
    title (str): 图表标题。
    """
    if word_counts:
        words, counts = zip(*word_counts.most_common(20))
        plt.figure(figsize=(12, 6))
        plt.bar(words, counts, color='blue')
        plt.xlabel('Words')
        plt.ylabel('Frequency')
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    else:
        print(f"Not enough data to generate {title} bar chart")

def generate_word_cloud(word_counts, title):
    """
    生成词云。

    参数:
    word_counts (Counter): 词频统计的Counter对象。
    title (str): 词云标题。
    """
    if word_counts:
        wordcloud = WordCloud(width=800, height=800, background_color='white', min_font_size=10).generate_from_frequencies(word_counts)
        plt.figure(figsize=(8, 8), facecolor=None)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.title(title)
        plt.show()
    else:
        print(f"Not enough data to generate {title} word cloud")

def main():
    # 获取用户输入的搜索词汇和爬取页数
    query = input("Please enter the search term: ")
    max_pages = int(input("Please enter the number of pages to crawl: "))

    engines = ["google", "yahoo"]
    all_word_counts = {}

    for engine in engines:
        urls = get_search_links(query, engine, max_pages=max_pages)  # 使用用户输入的页数
        word_counts = count_words_in_articles(urls)
        all_word_counts[engine] = word_counts
        save_to_json(word_counts, f"{engine}_word_counts.json")

    # 生成对比图表
    for engine, word_counts in all_word_counts.items():
        plot_word_frequency(word_counts, f"{engine} Word Frequency")

    # 生成对比词云
    for engine, word_counts in all_word_counts.items():
        generate_word_cloud(word_counts, f"{engine} Word Cloud")

if __name__ == "__main__":
    main()