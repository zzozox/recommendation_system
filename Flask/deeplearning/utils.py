from collections import defaultdict  # 导入 defaultdict 类，用于创建字典并提供默认值

from paddlenlp import Taskflow  # 导入 PaddleNLP 的 Taskflow 模块，用于自然语言处理任务
import jieba  # 导入 jieba 分词库，用于中文文本的分词
import numpy as np  # 导入 numpy 库，用于数值计算

word_segmenter = Taskflow("word_segmentation")  # 初始化一个 Taskflow 实例，用于中文分词


def convert_example(example, tokenizer, is_test=False):
    """
    将输入样本转换为序列分类任务的模型输入。
    使用 `jieba.cut` 对文本进行分词。

    参数：
        example (list[str]): 输入数据列表，包含文本和标签（如果有）。
        tokenizer (paddlenlp.data.JiebaTokenizer): 使用 jieba 对中文字符串进行分词的分词器。
        is_test (bool, 默认为 False): 输入样本是否为测试数据。

    返回值：
        input_ids (list[int]): token ids 列表。
        valid_length (int): 输入序列的有效长度。
        label (numpy.array, int64 类型，可选): 输入标签（如果不是测试数据）。
    """

    # 对文本进行分词并编码为 token ids
    input_ids = tokenizer.encode(example["text"])
    valid_length = np.array(len(input_ids), dtype='int64')  # 获取有效长度
    input_ids = np.array(input_ids, dtype='int64')  # 转换为 numpy 数组

    if not is_test:
        label = np.array(example["label"], dtype="int64")  # 获取标签并转换为 numpy 数组
        return input_ids, valid_length, label  # 返回 token ids、有效长度和标签
    else:
        return input_ids, valid_length  # 如果是测试数据，仅返回 token ids 和有效长度


def preprocess_prediction_data(data, tokenizer):
    """
    将预测数据处理成与训练数据相同的格式。

    参数：
        data (List[str]): 预测数据列表，每个元素是一个分词后的文本。
        tokenizer (paddlenlp.data.JiebaTokenizer): 使用 jieba 对中文字符串进行分词的分词器。

    返回值：
        examples (List[Example]): 处理后的数据列表，每个元素是一个 Example（命名元组）对象，
                                 包含 `text`（word ids）和 `seq_len`（序列长度）。
    """
    examples = []
    for text in data:
        ids = tokenizer.encode(text)  # 对文本进行编码
        examples.append([ids, len(ids)])  # 添加到示例列表中
    return examples  # 返回处理后的示例列表


def build_vocab(texts,
                stopwords=[],
                num_words=None,
                min_freq=10,
                unk_token="[UNK]",
                pad_token="[PAD]"):
    """
    根据输入文本构建词汇表。

    参数：
        texts (List[str]): 原始语料数据。
        stopwords (List[str]): 需要过滤的停用词列表。
        num_words (int, 可选): 词汇表的最大大小。
        min_freq (int): 词汇表中词的最小频率。
        unk_token (str): 未知词的特殊 token。
        pad_token (str): 填充 token。

    返回值：
        word_index (Dict): 从语料数据构建的词汇表。
    """
    word_counts = defaultdict(int)  # 创建一个默认值为 0 的字典用于计数
    for text in texts:
        if not text:
            continue
        for word in word_segmenter(text):  # 对文本进行分词
            if word in stopwords:
                continue
            word_counts[word] += 1  # 统计词频

    wcounts = []
    for word, count in word_counts.items():
        if count < min_freq:
            continue
        wcounts.append((word, count))  # 筛选出频率大于等于 min_freq 的词
    wcounts.sort(key=lambda x: x[1], reverse=True)  # 按词频从高到低排序

    if num_words is not None and len(wcounts) > (num_words - 2):
        wcounts = wcounts[:(num_words - 2)]  # 限制词汇表的大小
    sorted_voc = [pad_token, unk_token]  # 添加特殊 token 到词汇表
    sorted_voc.extend(wc[0] for wc in wcounts)  # 将排序后的词添加到词汇表
    word_index = dict(zip(sorted_voc, list(range(len(sorted_voc)))))  # 创建词汇表字典
    return word_index  # 返回词汇表
