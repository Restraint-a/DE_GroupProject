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
    chrome_options.add_argument("--no-sandbox")  # 禁用沙箱模式
    chrome_options.add_argument("--disable-dev-shm-usage")  # 禁用/dev/shm 使用
    service = Service("D:/Anaconda/chromedriver.exe")  # 替换为你的 ChromeDriver 路径
    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser


def get_search_links(query, browser):
    """
    使用 Selenium 从 Google 搜索获取链接。

    参数:
    query (str): 搜索的关键词。
    browser: Selenium WebDriver 实例。

    返回:
    list: 搜索结果的 URL 列表。
    """
    search_url = f"https://www.google.com/search?q={query}"
    browser.get(search_url)
    time.sleep(3)  # 等待页面加载

    soup = BeautifulSoup(browser.page_source, "html.parser")
    urls = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and ("/url?q=" in href or href.startswith("http")) and "translate.google.com/translate" not in href:
            if "/url?q=" in href:
                href = href.split("/url?q=")[1].split("&")[0]
            urls.append(href)
    return urls[10:40]


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
    for url in urls:
        print(f"正在处理: {url}")
        article_text = fetch_article_text(url, browser)
        words = word_tokenize(article_text.lower())
        filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
        all_words.update(filtered_words)
    return all_words


def save_to_json(word_counts, filename):
    """
    将统计结果保存为 JSON 文件。

    参数:
    word_counts: 单词频率的统计结果。
    filename: 保存的文件名。
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(word_counts, f, indent=4)
    print(f"结果已保存到 {filename}")


def selenium_crawl(query):
    """
    使用 Selenium 爬取数据并保存结果。

    参数:
    query (str): 查询关键词。
    """
    browser = init_browser()
    try:
        urls = get_search_links(query, browser)
        print("urls length: ", len(urls))
        print("urls :", urls)
        word_counts = count_words_in_articles(urls, browser)
        save_to_json(word_counts, filename=f"{query}_selenium_word_counts.json")
    finally:
        browser.quit()  # 确保关闭浏览器


def main():
    query = input("Please input query key word：")
    selenium_crawl(query)


if __name__ == "__main__":
    main()
