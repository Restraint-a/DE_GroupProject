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
# import nltk
# nltk.download('averaged_perceptron_tagger_eng')

# 手动排除一些无意义高频词
domain_specific_stopwords = {"google", "scholar", "nature", "www", "https", "com", "article"}

# 配置 Chrome Driver
def init_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式（不显示浏览器窗口）
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    chrome_options.add_argument("--no-sandbox")  # 禁用沙盒模式
    chrome_options.add_argument("--disable-dev-shm-usage")  # 禁用 /dev/shm 使用
    service = Service("D:/Anaconda/chromedriver.exe")  # 替换为你的 ChromeDriver 路径
    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser

def remove_chinese(text):
    """
    移除文本中的中文字符。
    """
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

def get_nature_links(query, browser, link_count=10):
    """
    从 nature 搜索页面获取文章链接。
    """
    search_url = f"https://www.nature.com/search?q={query}&order=relevance"
    browser.get(search_url)
    time.sleep(5)  # 等待页面加载

    links = []
    while len(links) < link_count:
        soup = BeautifulSoup(browser.page_source, "html.parser")

        # 提取符合条件的链接
        for link in soup.find_all("a", href=True):
            if "articles" in link["href"]:
                full_link = f"https://www.nature.com{link['href']}"
                links.append(full_link)

                if len(links) >= link_count:
                    break

        # 如果达到了链接数量，就退出
        if len(links) >= link_count:
            break

        # 查找并点击“下一页”按钮
        try:
            next_button = browser.find_element(By.CSS_SELECTOR, "a.c-pagination__link span")
            next_button.click()  # 点击下一页
            time.sleep(3)  # 等待页面加载
        except Exception as e:
            print(f"没有找到下一页按钮或翻页出错，停止翻页：{e}")
            break

    print(f"提取到的有效链接: {links}")
    return links


def get_bbc_links(query, browser, link_count=10):
    """
    从 BBC 搜索页面获取指定数量的文章链接，仅包含 /news/articles，支持翻页。
    """
    base_url = f"https://www.bbc.com/search?q={query}"
    browser.get(base_url)
    time.sleep(5)  # 等待页面加载

    links = []
    while len(links) < link_count:
        soup = BeautifulSoup(browser.page_source, "html.parser")

        # 提取符合条件的链接
        for link in soup.find_all("a", href=True):
            if "news/articles" in link["href"]:
                full_link = f"https://www.bbc.com{link['href']}"
                links.append(full_link)

                if len(links) >= link_count:
                    break

        # 如果达到了链接数量，就退出
        if len(links) >= link_count:
            break

        # 查找并点击“下一页”按钮
        try:
            next_button = browser.find_element(By.CSS_SELECTOR, "button[data-testid='pagination-next-button']")
            next_button.click()  # 点击下一页按钮
            time.sleep(5)  # 等待页面加载
        except Exception as e:
            print(f"没有找到下一页按钮，停止爬取：{e}")
            break

    print(f"提取到的有效链接: {links}")
    return links

def fetch_article_text(url, browser):
    """
    使用 Selenium 获取动态生成的网页内容，并提取文章文本。
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

def fetch_article_text_nature(url, browser):
    """
    使用 Selenium 获取动态生成的网页内容，并提取文章标题和摘要。
    """
    try:
        # 访问文章页面
        browser.get(url)
        time.sleep(5)  # 等待页面加载

        # 解析页面内容
        soup = BeautifulSoup(browser.page_source, "html.parser")

        # 提取标题
        title_element = soup.find("h1", class_="c-article-title", attrs={"data-test": "article-title"})
        title = title_element.get_text(strip=True) if title_element else "标题未找到"

        # 提取摘要
        abstract_element = soup.find("div", class_="c-article-section__content", id="Abs1-content")
        abstract = abstract_element.get_text(strip=True) if abstract_element else "摘要未找到"

        return abstract  # 只返回摘要文本

    except Exception as e:
        print(f"请求失败: {url} 错误: {e}")
        return "摘要未找到"  # 如果出错，返回一个默认的摘要


def count_words_in_articles(urls, browser):
    """
    统计一组文章中每个单词的出现次数，排除停用词。
    """
    all_words = Counter()
    stop_words = set(stopwords.words("english"))

    domain_specific_stopwords = {"google", "scholar", "nature", "www", "https", "com", "article"}

    # 定义名词和动词的词性标签
    allowed_pos = {"NN", "NNS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"}

    for url in urls:
        print(f"正在处理: {url}")
        article_text = fetch_article_text(url, browser)
        words = word_tokenize(article_text.lower())

        # 词性标注
        tagged_words = nltk.pos_tag(words)

        # 过滤停用词、领域停用词以及非名词/动词
        filtered_words = [
            word for word, pos in tagged_words
            if word.isalpha() and word not in stop_words and word not in domain_specific_stopwords and pos in allowed_pos
        ]

        all_words.update(filtered_words)
    return all_words

def count_words_in_articles_nature(urls, browser):
    """
    统计一组文章中每个单词的出现次数，排除停用词。
    """
    all_words = Counter()
    stop_words = set(stopwords.words("english"))

    domain_specific_stopwords = {"google", "scholar", "nature", "www", "https", "com", "article" }

    # 定义名词和动词的词性标签
    allowed_pos = {"NN", "NNS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"}

    for url in urls:
        print(f"正在处理: {url}")
        article_text = fetch_article_text_nature(url, browser)
        words = word_tokenize(article_text.lower())

        # 词性标注
        tagged_words = nltk.pos_tag(words)

        # 过滤停用词、领域停用词以及非名词/动词
        filtered_words = [
            word for word, pos in tagged_words
            if word.isalpha() and word not in stop_words and word not in domain_specific_stopwords and pos in allowed_pos
        ]

        all_words.update(filtered_words)
    return all_words

def save_to_json(word_counts, filename):
    """
    将统计结果保存为 JSON 文件。
    """
     # 使用 remove_chinese 函数移除中文
    filtered_word_counts = {remove_chinese(key): value for key, value in word_counts.items()}

    # 写入 JSON 文件
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(filtered_word_counts, f, indent=4)
    print(f"结果已保存到 {filename}")

def selenium_crawl(query, source="nature", link_count=10):
    """
    主爬取函数，调用 Selenium 浏览器并获取指定平台的文章链接。
    """
    browser = init_browser()
    try:
        if source == "nature":
            urls = get_nature_links(query, browser, link_count)
        elif source == "bbc":
            urls = get_bbc_links(query, browser, link_count)
        else:
            raise ValueError("Unsupported source. Please choose 'nature' or 'bbc'.")

        print(f"从 {source} 获取的链接数量: {len(urls)}")
        if source == "nature":
            word_counts = count_words_in_articles_nature(urls, browser)
            save_to_json(word_counts, filename=f"{query}_{source}_word_counts.json")
        elif source == "bbc":
            word_counts = count_words_in_articles(urls, browser)
            save_to_json(word_counts, filename=f"{query}_{source}_word_counts.json")
    finally:
        browser.quit()  # 确保关闭浏览器

def main():
    """
    主程序，接收用户输入并调用爬取逻辑。
    """
    query = input("请输入搜索关键词: ")
    source = input("请选择数据来源 (nature/bbc): ").lower()

    try:
        link_count = int(input("请输入获取链接的数量 (例如: 10, 20): "))
        if link_count <= 0:
            raise ValueError("链接数量必须大于 0。")
    except ValueError as e:
        print(f"输入无效: {e}. 默认设置为 10。")
        link_count = 10



    selenium_crawl(query, source, link_count)

if __name__ == "__main__":
    main()
