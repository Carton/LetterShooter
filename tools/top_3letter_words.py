import nltk
from nltk.corpus import words, brown
from collections import Counter

# 下载nltk语料库中的words和brown数据集
nltk.download("words")
nltk.download("brown")

# 获取英语单词列表
english_words = words.words()
three_letter_words = [word for word in english_words if len(word) == 3]

# 使用brown语料库统计单词频率
word_freq = nltk.FreqDist(word.lower() for word in brown.words())

# 获取三个字母单词的使用频率
three_letter_word_freq = {word: word_freq[word] for word in three_letter_words}

# 按使用频率排序
sorted_three_letter_words = sorted(three_letter_word_freq.items(), key=lambda x: x[1], reverse=True)

# 获取使用频率最高的前200个单词
top_words = sorted_three_letter_words[:200]

# 输出结果
print("Top 200 most frequent three-letter words:")
for word, count in top_words:
    print(f"{word}: {count}")
