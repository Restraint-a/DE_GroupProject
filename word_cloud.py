from wordcloud import WordCloud
import matplotlib.pyplot as plt

import json


def get_word_counts(query):
    """
    从指定的JSON文件中加载词频数据。

    参数:
    - file_name: 包含词频数据的JSON文件的名称。

    返回:
    - word_counts: 一个字典，其中键是单词，值是这些单词在特定语境下的出现次数。
    """
    # 打开文件并加载JSON格式的词频数据
    file_name = f"{query}_word_counts.json"
    with open(file_name, 'r', encoding='utf-8') as f:
        word_counts = json.load(f)
    # 返回解析后的词频数据
    return word_counts


def get_wordcloud(word_counts,query):
    """
    根据单词频率生成词云。
    该函数创建了一个词云对象，并设置了各种属性以定制词云的外观。
    然后，使用matplotlib库显示生成的词云。

    参数:
    word_counts (dict): 单词频率的字典，键为单词，值为频率。
    """
    # 创建词云对象并设置属性
    wordcloud = WordCloud(
        background_color='white',  # 设置背景颜色
        max_words=200,             # 最多显示的单词数量
        colormap='viridis',         # 颜色方案
        contour_width=3,            # 轮廓宽度
        contour_color='steelblue',   # 轮廓颜色
        width = 1600,               #图片宽度
        height = 1200               #图片高度
    ).generate_from_frequencies(word_counts)

    # 使用 matplotlib 显示词云
    plt.figure(figsize=(20, 15))  # 设置图像大小
    plt.imshow(wordcloud, interpolation='bilinear')  # 绘制词云
    plt.axis("off")  # 关闭坐标轴
    plt.show()  # 显示图像

    wordCloud_name = f"{query}_word_cloud.png"
    # 如果你想保存词云为图片文件
    wordcloud.to_file(wordCloud_name)
    print(f'WordCloud of {query} has been saved as {wordCloud_name}!')

def main():
    file_name = 'calc.json'
    word_counts = get_word_counts(file_name)
    get_wordcloud(word_counts)

if __name__ == "__main__":
    main()