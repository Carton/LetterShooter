import nltk
from nltk.corpus import words
from collections import Counter

# 下载nltk语料库中的words数据集
nltk.download("words")

# 获取英语单词列表
english_words = words.words()

# 提取所有2个字母的组合
bigrams = []
for word in english_words:
    bigrams.extend(nltk.bigrams(word))

# 使用Counter统计各个组合的出现次数
bigram_counts = Counter(bigrams)

# 找到出现频率最高的组合
top_bigrams = bigram_counts.most_common(100)

print("Top 10 most common bigrams:")
for bigram, count in top_bigrams:
    print(f"{bigram[0]}{bigram[1]}: {count}")
