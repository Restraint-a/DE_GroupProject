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

def remove_chinese(text):
    """
    移除文本中的中文字符。
    """
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

# 配置 Chrome Driver
def init_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式（不显示浏览器窗口）
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    chrome_options.add_argument("--no-sandbox")  # 禁用沙盒模式
    chrome_options.add_argument("--disable-dev-shm-usage")  # 禁用 /dev/shm 使用
    service = Service("C:/Users/火箭筒/AppData/Local/Programs/Python/Python39/chromedriver.exe")  # 替换为你的 ChromeDriver 路径
    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser


def get_cnki_links(query, browser, link_count=10):
    """
    从知网搜索页面获取文章链接。
    """
    search_url = f"https://www.reddit.com/search/?q={query}"
    browser.get(search_url)
    time.sleep(5)  # 等待页面加载

    links = []
    while len(links) < link_count:
        soup = BeautifulSoup(browser.page_source, "html.parser")

        # 提取符合条件的链接（这里需要根据知网的实际页面结构来调整）
        for link in soup.find_all("a", class_= 'absolute inset-0'):

        # 假设知网的文章链接包含"Article"和"kns"字样
                full_link = link["href"]

                full_link = "https://www.reddit.com/" + full_link
                links.append(full_link)

                if len(links) >= link_count:
                    break

        # 如果达到了链接数量，就退出
        if len(links) >= link_count:
            break

        # 查找并点击“下一页”按钮（这里也需要根据知网的实际页面结构来调整）
        # try:
        #     next_button = browser.find_element(By.XPATH,  "/html/body/div[1]/div/div[1]/main/section[1]/div/div[1]/div/div/div[2]/div[1]/nav/ul/li[9]")
        #     next_button.click()  # 点击下一页
        #     time.sleep(3)  # 等待页面加载
        # except Exception as e:
        #     print(f"没有找到下一页按钮或翻页出错，停止翻页：{e}")
        #     break

    print(f"提取到的有效链接: {links}")
    return links


def fetch_cnki_article_text(url, browser):
    """
    使用 Selenium 获取知网文章页面的文本内容。
    """
    try:
        browser.get(url)
        time.sleep(5)  # 等待页面加载
        soup = BeautifulSoup(browser.page_source, "html.parser")

        # 提取文章文本（这里需要根据知网文章页面的实际结构来调整）
        text_elements = soup.find_all("p")
        text = " ".join([element.get_text() for element in text_elements])

        # 清洗文本，移除非英文字符等（根据需要调整）
        english_text = re.sub(r"[^a-zA-Z\s]", "", text)
        return english_text
    except Exception as e:
        print(f"请求失败: {url} 错误: {e}")
        return ""


def count_words_in_cnki_articles(urls, browser):
    """
    统计一组知网文章中每个单词的出现次数，排除停用词。
    """
    all_words = Counter()
    stop_words = set(stopwords.words("english"))

    domain_specific_stopwords = {"cnki", "work", "www", "https", "com", "article","also"}

    # 定义名词和动词的词性标签
    allowed_pos = {"NN", "NNS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"}

    for url in urls:
        print(f"正在处理: {url}")
        article_text = fetch_cnki_article_text(url, browser)
        words = word_tokenize(article_text.lower())

        # 词性标注
        tagged_words = nltk.pos_tag(words)

        # 过滤停用词、领域停用词以及非名词/动词
        filtered_words = [
            word for word, pos in tagged_words
            if
            word.isalpha() and word not in stop_words and word not in domain_specific_stopwords and pos in allowed_pos
        ]

        all_words.update(filtered_words)
    return all_words


def save_to_json(word_counts, filename):
    """
    将统计结果保存为 JSON 文件。
    """
    # 使用 remove_chinese 函数移除中文
    filtered_word_counts = {remove_chinese(key): value for key, value in word_counts.items()}

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(filtered_word_counts, f, indent=4)
    print(f"结果已保存到 {filename}")


def cnki_crawl(query, link_count=10):
    """
    主爬取函数，调用 Selenium 浏览器并获取知网的文章链接。
    """
    browser = init_browser()
    try:
        urls = get_cnki_links(query, browser, link_count)
        print(f"从知网获取的链接数量: {len(urls)}")
        word_counts = count_words_in_cnki_articles(urls, browser)
        save_to_json(word_counts, filename=f"{query}_cnki_word_counts.json")
    finally:
        browser.quit()  # 确保关闭浏览器


def main():
    """
    主程序，接收用户输入并调用爬取逻辑。
    """
    query = input("请输入知网搜索关键词: ")

    try:
        link_count = int(input("请输入获取链接的数量 (例如: 10, 20): "))
        if link_count <= 0:
            raise ValueError("链接数量必须大于 0。")
    except ValueError as e:
        print(f"输入无效: {e}. 默认设置为 10。")
        link_count = 10

    cnki_crawl(query, link_count)


if __name__ == "__main__":
    main()