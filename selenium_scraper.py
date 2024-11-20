from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import time
import json
import nltk
import re

# 确保 nltk 的停用词被下载（如果没下载过）
# nltk.download("punkt")
# nltk.download("stopwords")

# 配置 Chrome Driver
def init_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式（不显示浏览器窗口）
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    chrome_options.add_argument("--no-sandbox")  # 禁用沙盒模式
    chrome_options.add_argument("--disable-dev-shm-usage")  # 禁用/dev/shm 使用
    service = Service("D:\Anaconda/chromedriver.exe")  # 替换为你的 ChromeDriver 路径
    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser

def remove_chinese(text):
    """
    移除文本中的中文字符。
    """
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

def get_search_links(query, browser, engine="google", start_index=0, link_count=30):
    """
    使用 Selenium 从指定搜索引擎获取链接，默认使用英文搜索。

    参数:
    query (str): 搜索关键词。
    browser: Selenium WebDriver 实例。
    engine (str): 搜索引擎名称，支持 'google', 'bing', 'duckduckgo', 'yandex'。
    start_index (int): 要跳过的链接数量。
    link_count (int): 要获取的链接数量。

    返回:
    list: 搜索结果的 URL 列表。
    """
    engine_urls = {
        # "google": f"https://www.google.com/search?q={query}&hl=en&lr=lang_en",
        # "bing": f"https://www.bing.com/search?q={query}&setlang=en",
        # "duckduckgo": f"https://duckduckgo.com/?q={query}&kl=en-us",
        "google": f"https://www.google.com/search?q={query}",
        "bing": f"https://www.bing.com/search?q={query}",
        "duckduckgo": f"https://duckduckgo.com/?t=h_&q={query}&ia=web",
    }

    if engine not in engine_urls:
        raise ValueError(f"Unsupported engine '{engine}'. Supported engines are: {list(engine_urls.keys())}")

    search_url = engine_urls[engine]
    browser.get(search_url)
    time.sleep(3)  # 等待页面加载

    # 通用的结果解析逻辑
    soup = BeautifulSoup(browser.page_source, "html.parser")
    urls = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and "http" in href:  # 简单过滤 URL
            urls.append(href)

    # 跳过前面的 start_index 个链接，返回后续的 link_count 个
    return urls[start_index:start_index + link_count]

def fetch_article_text(url, browser):
    """
    使用 Selenium 获取动态生成的网页内容，并提取文章文本。

    参数:
    url (str): 要访问的文章链接。
    browser: Selenium WebDriver 实例。

    返回:
    str: 提取的文章内容，仅保留英文字符。
    """
    try:
        browser.get(url)
        time.sleep(5)  # 等待页面加载
        soup = BeautifulSoup(browser.page_source, "html.parser")
        text = " ".join([p.get_text() for p in soup.find_all("p")])
        english_text = re.sub(r"[^a-zA-Z\s]", "", text)
        return english_text
    except Exception as e:
        print(f"请求失败: {url} 错误: {e}")
        return ""

def count_words_in_articles(urls, browser):
    """
    统计一组文章中每个单词的出现次数，排除停用词。

    参数:
    urls (list of str): 文章的 URL 列表。
    browser: Selenium WebDriver 实例。

    返回:
    Counter: 包含每个单词及其出现次数的 Counter 对象。
    """
    all_words = Counter()
    stop_words = set(stopwords.words("english"))

    domain_specific_stopwords = {"google", "scholar", "nature", "www", "https", "com", "article", "bbc", "office", "said"}

    # 定义名词、动词和形容词的词性标签
    allowed_pos = {"NN", "NNS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "JJ", "JJR", "JJS"}

    for url in urls:
        print(f"正在处理: {url}")
        article_text = fetch_article_text(url, browser)
        words = word_tokenize(article_text.lower())

        # 词性标注
        tagged_words = nltk.pos_tag(words)

        # 过滤停用词、领域停用词以及非名词/动词
        filtered_words = [
            word for word, pos in tagged_words
            if word.isalpha() and len(word) > 2 and word not in stop_words and word not in domain_specific_stopwords and pos in allowed_pos
        ]

        all_words.update(filtered_words)
    return all_words

def save_to_json(word_counts, filename):
    """
    将统计结果保存为 JSON 文件。

    参数:
    word_counts: 单词频率的统计结果。
    filename: 保存的文件名。
    """

     # 使用 remove_chinese 函数移除中文
    filtered_word_counts = {remove_chinese(key): value for key, value in word_counts.items()}

    # 写入 JSON 文件
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(filtered_word_counts, f, indent=4)
    print(f"结果已保存到 {filename}")

def selenium_crawl(query, engine="google", start_index=0, link_count=30):
    """
    主爬取函数，调用 Selenium 浏览器并获取搜索链接。

    参数:
    query (str): 搜索关键词。
    engine (str): 搜索引擎名称。
    start_index (int): 跳过的链接数量。
    link_count (int): 获取的链接数量。
    """
    browser = init_browser()
    try:
        urls = get_search_links(query, browser, engine, start_index, link_count)
        print(f"使用 {engine} 搜索引擎获取的链接数量: {len(urls)}")
        print("URLs:", urls)
        word_counts = count_words_in_articles(urls, browser)
        save_to_json(word_counts, filename=f"{query}_{engine}_word_counts.json")
    finally:
        browser.quit()  # 确保关闭浏览器

def main():
    """
    主程序，接收用户输入并调用爬取逻辑。
    """
    query = input("Please input query key word: ")
    engine = input("Please input search engine (google/bing/duckduckgo): ").lower()
    try:
        start_index = int(input("Please input the number of links to skip (e.g., 0, 10): "))
        link_count = int(input("Please input the number of links to retrieve (e.g., 10, 20, 30): "))
        if start_index < 0 or link_count <= 0:
            raise ValueError("Invalid input for start index or link count.")
    except ValueError as e:
        print(f"Invalid input: {e}. Defaulting to start_index=0 and link_count=30.")
        start_index = 0
        link_count = 30
    selenium_crawl(query, engine, start_index, link_count)

if __name__ == "__main__":
    main()
