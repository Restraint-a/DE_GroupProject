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
import random

# 确保nltk的停用词被下载（如果没下载过）
import nltk
nltk.download("punkt")
nltk.download("stopwords")

def get_search_links(query, engine="google"):
    """
    根据查询字符串获取不同搜索引擎的搜索结果中的链接。

    参数:
    query (str): 要搜索的查询字符串。
    engine (str): 搜索引擎名称，支持 "google", "yahoo", "duckduckgo"。

    返回:
    list: 一个包含搜索结果中URL的列表。
    """
    if engine == "google":
        url = f"https://www.google.com/search?q={query}"
    elif engine == "yahoo":
        url = f"https://search.yahoo.com/search?p={query}"
    elif engine == "duckduckgo":
        url = f"https://duckduckgo.com/html/?q={query}"
    else:
        raise ValueError("不支持的搜索引擎")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"请求失败: {url} 错误: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    urls = []

    if engine == "google":
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and ("/url?q=" in href or href.startswith("http")) and "translate.google.com/translate" not in href:
                if "/url?q=" in href:
                    href = href.split("/url?q=")[1].split("&")[0]
                urls.append(href)
    # elif engine == "yahoo":
    #     for result in soup.find_all("div"):
    #         link = result.find("a")
    #         if link and link.get("href"):
    #             urls.append(link.get("href"))
    elif engine == "yahoo":
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and ("/url?q=" in href or href.startswith("http")) and "translate.yahoo.com/translate" not in href:
                if "/url?q=" in href:
                    href = href.split("/url?q=")[1].split("&")[0]
                urls.append(href)
        if len(urls) < 10:
            print(f"警告: Yahoo 返回的URL数量少于10个，检查HTML结构：")
            with open(f"{engine}_search_result.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            print(f"已保存 {engine} 的搜索结果HTML到 {engine}_search_result.html")
    # elif engine == "duckduckgo":
    #     for result in soup.find_all("a"):
    #         href = result.get("href")
    #         if href:
    #             urls.append(href)
                
    elif engine == "duckduckgo":
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and ("/url?q=" in href or href.startswith("http")) and "translate.duckduckgo.com/translate" not in href:
                if "/url?q=" in href:
                    href = href.split("/url?q=")[1].split("&")[0]
                urls.append(href)

    print(f"{engine} URL数量:", len(urls))
    return urls

def fetch_article_text(url, max_retries=3, retry_delay=2):
    """
    根据给定的URL获取文章的文本内容，并过滤出只包含英文字符的内容。

    参数:
    url (str): 文章的URL。
    max_retries (int): 最大重试次数。
    retry_delay (int): 重试间隔时间（秒）。

    返回:
    str: 过滤后的英文文本内容。
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = " ".join([p.get_text() for p in soup.find_all("p")])
            english_text = re.sub(r"[^a-zA-Z\s]", "", text)
            if not english_text:  # 增加检查，确保文本不为空
                print(f"未找到文章内容: {url}")
            return english_text
        except requests.RequestException as e:
            print(f"请求失败: {url} 错误: {e}")
            if attempt < max_retries:
                print(f"重试 {attempt + 1}/{max_retries}，等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay * (2 ** attempt))  # 指数退避
            else:
                print(f"达到最大重试次数: {max_retries}")
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
        if article_text:
            words = word_tokenize(article_text.lower())
            filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
            all_words.update(filtered_words)
            time.sleep(random.uniform(1, 3))  # 增加随机请求间隔，避免被封IP

    if not all_words:
        print("警告: 没有获取到任何文章内容，检查URL列表和内容提取逻辑。")
    return all_words

def save_to_json(word_counts, filename="calc.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(word_counts, f, indent=4)
    print(f"结果已保存到 {filename}")

def load_and_print_json(filename="calc.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"{filename} 文件内容：")
            print(json.dumps(data, indent=4, ensure_ascii=False))
    except FileNotFoundError:
        print(f"文件 {filename} 未找到。")
    except json.JSONDecodeError:
        print(f"文件 {filename} 不是一个有效的JSON文件。")

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
        plt.xlabel('单词')
        plt.ylabel('出现次数')
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    else:
        print(f"没有足够的数据生成 {title} 图表")

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
        print(f"没有足够的数据生成 {title} 词云")

def main():
    query = "financial"
    engines = ["google", "yahoo", "duckduckgo"]
    all_word_counts = {}

    for engine in engines:
        urls = get_search_links(query, engine)
        if urls:
            word_counts = count_words_in_articles(urls)
            all_word_counts[engine] = word_counts
            save_to_json(word_counts, f"{engine}_word_counts.json")
        else:
            print(f"警告: {engine} 没有返回有效的URL。")

    # 生成对比图表
    for engine, word_counts in all_word_counts.items():
        plot_word_frequency(word_counts, f"{engine} Word Frequency Analysis")

    # 生成对比词云
    for engine, word_counts in all_word_counts.items():
        generate_word_cloud(word_counts, f"{engine} Word Cloud")

if __name__ == "__main__":
    main()
    # load_and_print_json("google_word_counts.json")
    # load_and_print_json("yahoo_word_counts.json")
    # load_and_print_json("duckduckgo_word_counts.json")