# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import os

import paddle
import paddle.nn.functional as F
from paddlenlp.data import JiebaTokenizer, Stack, Tuple, Pad, Vocab

from deeplearning.model import LSTMModel
from deeplearning.utils import preprocess_prediction_data

# yapf: disable
parser = argparse.ArgumentParser(__doc__)
parser.add_argument('--device', choices=['cpu', 'gpu', 'xpu'], default="gpu", help="Select which device to train model, defaults to gpu.")
parser.add_argument("--batch_size", type=int, default=1, help="Total examples' number of a batch for training.")
parser.add_argument("--vocab_path", type=str, default="./vocab.json", help="The file path to vocabulary.")
parser.add_argument('--network', choices=['bow', 'lstm', 'bilstm', 'gru', 'bigru', 'rnn', 'birnn', 'bilstm_attn', 'cnn'],
    default="bilstm", help="Select which network to train, defaults to bilstm.")
parser.add_argument("--params_path", type=str, default='./checkpoints/final.pdparams', help="The path of model parameter to be loaded.")
args = parser.parse_args()
# yapf: enable


class LSTMSentiment:
    def __init__(self, model_path=None, vocab_path=None):
        self.init_model(model_path,vocab_path)

    def predict(self, text, batch_size=1):
        """
        Predicts the data labels.

        Args:
            model (obj:`paddle.nn.Layer`): A model to classify texts.
            data (obj:`List(Example)`): The processed data whose each element is a Example (numedtuple) object.
                A Example object contains `text`(word_ids) and `se_len`(sequence length).
            label_map(obj:`dict`): The label id (key) to label str (value) map.
            batch_size(obj:`int`, defaults to 1): The number of batch.
            pad_token_id(obj:`int`, optional, defaults to 0): The pad token index.

        Returns:
            results(obj:`dict`): All the predictions labels.
        """
        paddle.set_device('cpu')
        tokenizer = JiebaTokenizer(self.vocab)
        data = preprocess_prediction_data(text, tokenizer)
        # Seperates data into some batches.
        batches = [
            data[idx:idx + batch_size] for idx in range(0, len(data), batch_size)
        ]
        batchify_fn = lambda samples, fn=Tuple(
            Pad(axis=0, pad_val=self.pad_token_id),  # input_ids
            Stack(dtype="int64"),  # seq len
        ): [data for data in fn(samples)]

        results = []
        self.model.eval()
        for batch in batches:
            texts, seq_lens = batchify_fn(batch)
            texts = paddle.to_tensor(texts)
            seq_lens = paddle.to_tensor(seq_lens)
            logits = self.model(texts, seq_lens)
            probs = F.softmax(logits, axis=1)
            idx = paddle.argmax(probs, axis=1).numpy().tolist()
            probs_v = paddle.max(probs, axis=1).numpy().tolist()
            labels = [self.label_map[i] for i in idx]
            for i, label in enumerate(labels):
                res = {}
                res['prob'] = probs_v[i]
                res['label'] = label
                results.append(res)
        return results

    def init_model(self, model_path=None, vocab_path=None):
        if model_path is None or vocab_path is None:
            return
        # Loads vocab.
        self.vocab = Vocab.from_json(vocab_path)
        self.label_map = {0: 'negative', 1: 'positive'}
        self.vocab_size = len(self.vocab)
        self.num_classes = len(self.label_map)
        self.pad_token_id = self.vocab.to_indices('[PAD]')
        self.model = LSTMModel(
                self.vocab_size,
                self.num_classes,
                direction='bidirect',
                padding_idx=self.pad_token_id)
        # Loads model parameters.
        state_dict = paddle.load(model_path)
        self.model.set_dict(state_dict)
        print("Loaded parameters from %s" % args.params_path)

def sentimentalAnalysis_single(datas):
    current_path = os.path.dirname(__file__)
    model = LSTMSentiment(model_path=current_path + '/checkpoints/final.pdparams',
                          vocab_path=current_path + '/vocab.json')
    results = model.predict(datas)
    return results

def sentimentalAnalysis_multi():
    model = LSTMSentiment(model_path='./checkpoints/final.pdparams', vocab_path='./vocab.json')
    results = model.predict(data)
    print(results)

if __name__ == "__main__":
    # Firstly pre-processing prediction data  and then do predict.
    data = [
        '非常不错，服务很好，位于市中心区，交通方便，不过价格也高！',
        '怀着十分激动的心情放映，可是看着看着发现，在放映完毕后，出现一集米老鼠的动画片',
        '作为老的四星酒店，房间依然很整洁，相当不错。机场接机服务很好，可以在车上办理入住手续，节省时间。',
        '你们把苏州当乌克兰是不是，领了纳税人的工资就合伙打击报复纳税人吗？这事不说清楚我直接写挂号信给省委书记和市委书记',
        '这个电影的导演真的是不太行啊',
        '太好看了吧，画面强',
        '喜欢这个导演',
        '嗯~你问我对于他的看法'
    ]

    model = LSTMSentiment(model_path='./checkpoints/final.pdparams',vocab_path='./vocab.json')
    results = model.predict(data)
    for i in results:
        print(i)

