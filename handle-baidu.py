import requests
from bs4 import BeautifulSoup
import time
import random
from collections import Counter
from googletrans import Translator
import re
import json


def fetch_baidu_news(keyword, num_pages=10):
    base_url = "https://www.baidu.com/s"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    news_titles = []

    for page in range(num_pages):
        params = {
            'tn': 'news',
            'rtt': '1',
            'bsst': '1',
            'cl': '2',
            'wd': keyword,
            'pn': page * 10  # 百度每页显示10条新闻
        }
        response = requests.get(base_url, params=params, headers=headers)

        if response.status_code != 200:
            print(f"请求失败，状态码：{response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # 解析新闻标题
        titles = soup.find_all('a', attrs={'aria-label': True, 'class': 'news-title-font_1xS-F'})
        for title in titles:
            news_titles.append(title.get_text(strip=True))

        # 添加随机延时
        time.sleep(random.uniform(1, 3))

    return news_titles


def save_to_file(titles, filename="output.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        for index, title in enumerate(titles, start=1):
            file.write(f"{index}. {title}\n")


def translate_text(text, src='en', dest='zh-cn'):
    translator = Translator(service_urls=['translate.google.com'])
    try:
        translated_text = translator.translate(text, src=src, dest=dest).text
    except Exception as e:
        print(f"翻译失败：{text}，错误：{e}")
        translated_text = text  # 保持原样
    return translated_text


def extract_top_words(text, top_n=20):
    # 使用正则表达式去除标点符号和特殊字符，只保留字母和数字
    cleaned_text = re.sub(r'[^\w\s]', '', text)

    # 将文本转换为小写并分割成单词列表
    words = cleaned_text.lower().split()

    # 统计词频
    word_counts = Counter(words)

    # 获取出现次数最多的前N个词语
    most_common_words = word_counts.most_common(top_n)

    return dict(most_common_words)


def process_keyword(keyword, num_pages=10):
    # 将英文关键词翻译成中文
    translated_keyword = translate_text(keyword, src='en', dest='zh-cn')

    # 爬取新闻标题
    titles = fetch_baidu_news(translated_keyword, num_pages)

    # 保存新闻标题到文件
    save_to_file(titles)

    # 从文件中读取内容
    content = read_from_file()

    # 翻译内容
    translated_content = translate_text(content, src='zh-cn', dest='en')

    # 提取出现次数最多的前20个英文单词
    top_words = extract_top_words(translated_content, top_n=20)

    # 保存结果到JSON文件
    with open("top_words.json", "w", encoding="utf-8") as file:
        json.dump(top_words, file, ensure_ascii=False, indent=4)

    print("运行完毕，结果已保存到 top_words.json 文件中。")


def read_from_file(filename="output.txt"):
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()
    return content


if __name__ == "__main__":
    keyword = input("请输入您想要查询的关键词（英文）：")
    num_pages = int(input("请输入您想要查询的页数（默认为10）：") or 10)

    # 调用处理函数
    process_keyword(keyword, num_pages)