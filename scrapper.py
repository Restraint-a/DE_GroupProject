import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import json
import re

# 确保nltk的停用词被下载（如果没下载过）
import nltk
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")

def get_search_links(query):
    """
    根据查询字符串获取Google搜索结果中的链接。

    参数:
    query (str): 要搜索的查询字符串。

    返回:
    list: 一个包含搜索结果中URL的列表。
    """
    # Google搜索URL的格式
    url = f"https://www.google.com/search?q={query}"
    # 模拟浏览器的User-Agent头，以避免服务器拒绝请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # 发送GET请求到Google搜索页面
    response = requests.get(url, headers=headers)
    # 使用BeautifulSoup解析响应的HTML内容
    soup = BeautifulSoup(response.text, "html.parser")

    urls = []
    # 遍历所有<a>标签以找到链接
    for link in soup.find_all("a"):
        href = link.get("href")
        # 检查链接是否符合包含 /url?q= 或者以 http 开头的完整网址
        if href and ("/url?q=" in href or href.startswith("http")) and "translate.google.com/translate" not in href:
            # 对于包含 /url?q= 的链接，进行切分，提取实际网址
            if "/url?q=" in href:
                href = href.split("/url?q=")[1].split("&")[0]
            # 将提取的网址添加到列表中
            urls.append(href)
    # 打印网址列表的长度
    print("url length:", len(url))

    # 返回网址列表的子集，从第10个到第40个链接
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
        # 发起HTTP请求获取页面内容，使用headers模拟浏览器访问
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()  # 检查是否成功获取内容
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # 获取页面的所有文本
        text = " ".join([p.get_text() for p in soup.find_all("p")])
        #print("text: ", text)
        # 筛选仅包含英文字符的内容
        english_text = re.sub(r"[^a-zA-Z\s]", "", text)
        return english_text
    except requests.RequestException as e:
        # 处理请求异常
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
    # 初始化一个计数器对象，用于统计单词出现次数
    all_words = Counter()
    # 获取英文停用词集合
    stop_words = set(stopwords.words("english"))

    # 遍历每个URL，处理文章
    for url in urls:
        # 打印当前处理的URL
        print(f"正在处理: {url}")
        # 获取文章正文
        article_text = fetch_article_text(url)

        # 使用nltk进行分词
        words = word_tokenize(article_text.lower())

        # 仅统计非停用词的英文单词
        filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
        # 更新计数器
        all_words.update(filtered_words)

    # 返回统计结果
    return all_words



def save_to_json(word_counts, filename="calc.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(word_counts, f, indent=4)
    print(f"结果已保存到 {filename}")

def main():
    # 搜索特定单词并提取30个链接
    query = "Computer"
    urls = get_search_links(query)
    print("urls length: ", len(urls))
    print("urls :", urls)
    # 统计单词并保存
    word_counts = count_words_in_articles(urls)
    save_to_json(word_counts)

if __name__ == "__main__":
    main()