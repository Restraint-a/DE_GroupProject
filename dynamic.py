from word_cloud import get_word_counts,get_wordcloud
from scrapper import get_search_links,count_words_in_articles,save_to_json
from selenium_scraper import selenium_crawl as Google_Bing_Duckduckgo_selenium_crawl
from Nature_BBC_scraper import selenium_crawl as Nature_BBC_selenium_crawl
import json
from collections import defaultdict
from Baidu_scrapper import process_keyword

def json_merge(query, *files):
        # 创建一个默认字典，用于存储合并后的结果
    merged_data = defaultdict(int)

    # 遍历所有提供的文件名
    for file_name in files:
        try:
            # 打开并读取每个JSON文件
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)  # 将文件内容加载为字典

                # 遍历字典中的每个键值对
                for key, value in data.items():
                    # 将相同键的值累加
                    merged_data[key] += value
        except FileNotFoundError:
            print(f"Warning: File {file_name} not found and will be skipped.")
        except json.JSONDecodeError:
            print(f"Warning: File {file_name} is not a valid JSON and will be skipped.")

    output_file = f"{query}_word_counts.json"
    # 将合并后的数据保存到新的JSON文件中
    with open(output_file, 'w', encoding='utf-8') as output_file:
        json.dump(dict(merged_data), output_file, ensure_ascii=False, indent=4)

    print(f"Files have been successfully merged into {output_file.name}")

def Nature_BBC_crawl(query):
    print("Nature_BBC_crawl:")
    source = input("请选择数据来源 (nature/bbc): ").lower()

    try:
        link_count = int(input("请输入获取链接的数量 (例如: 10, 20): "))
        if link_count <= 0:
            raise ValueError("链接数量必须大于 0。")
    except ValueError as e:
        print(f"输入无效: {e}. 默认设置为 10。")
        link_count = 10


    Nature_BBC_selenium_crawl(query, source, link_count)

def Google_Bing_Duckduckgo_crawl(query):
    print("Google_Bing_Duckduckgo_crawl:")
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
    Google_Bing_Duckduckgo_selenium_crawl(query, engine, start_index, link_count)

def Baidu_crawl(query):
    print("Baidu_crawl:")
    num_pages = int(input("请输入您想要查询的页数（默认为10）：") or 10)

    # 调用处理函数
    process_keyword(query, num_pages)


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
    save_to_json(word_counts, filename=f"{query}_scrapper_word_counts.json")

def main():
    while True:
        query = input("Please input query key word：")
        Nature_BBC_crawl(query)
        dynamic_crawl(query)
        Google_Bing_Duckduckgo_crawl(query)
        Baidu_crawl(query)
        files = [f"{query}_scrapper_word_counts.json", f"{query}_duckduckgo_word_counts.json", f"{query}_bing_word_counts.json", f"{query}_google_word_counts.json",f"{query}_bbc_word_counts.json",f"{query}_nature_word_counts.json",f"{query}_Baidu_word_counts.json"]
        json_merge(query, *files)
        get_wordcloud(get_word_counts(query),query)

if __name__ == "__main__":
    main()
