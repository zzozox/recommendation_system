import random

from sklearn.preprocessing import LabelEncoder
from torch_geometric.nn.conv import MessagePassing
from torch_geometric.utils import degree
from torch import nn, optim, Tensor
import pandas as pd

import torch


def encode_data():
    rnames = ['userId', 'movieId', 'rating', 'timestamp']
    ratings = pd.read_csv("algorithm/LightGCN/ratings.dat", delimiter='::', engine='python', header=None, names=rnames)

    # 初始化LabelEncoder
    labelencoder_user = LabelEncoder()
    labelencoder_movie = LabelEncoder()

    # 拟合LabelEncoder并转换用户ID和电影ID
    user_ids = ratings['userId'].values
    movie_ids = ratings['movieId'].values

    # 转换用户ID和电影ID到整数索引
    user_indices = labelencoder_user.fit_transform(user_ids)
    movie_indices = labelencoder_movie.fit_transform(movie_ids)

    # 创建映射字典
    user_to_idx = {user_ids[i]: user_indices[i] for i in range(len(user_ids))}
    idx_to_user = {user_indices[i]: user_ids[i] for i in range(len(user_ids))}
    item_to_idx = {movie_ids[i]: movie_indices[i] for i in range(len(movie_ids))}
    idx_to_item = {movie_indices[i]: movie_ids[i] for i in range(len(movie_ids))}

    return user_to_idx, idx_to_user, item_to_idx, idx_to_item,len(labelencoder_user.classes_),len(labelencoder_movie.classes_)

class LightGCNConv(MessagePassing):
    def __init__(self, num_users, num_items, embedding_dim=64, K=3, add_self_loops=False, dropout_rate=0.1, bias=True,
                 **kwargs):
        super().__init__(aggr='add')
        #super().__init__()
        self.embedding_dim = embedding_dim
        self.num_users = num_users
        self.num_items = num_items
        self.embedding = nn.Embedding(self.num_users + self.num_items, self.embedding_dim)
        self.K = K
        self.add_self_loops = add_self_loops
        self.dropout = dropout_rate

        self.out = nn.Linear(self.embedding_dim + self.embedding_dim, 1)
        nn.init.normal_(self.embedding.weight, std=0.1)

    def forward(self, edge_index):
        emb0 = self.embedding.weight
        embs = [emb0]
        emb_k = emb0


        from_, to_ = edge_index

        deg = degree(to_, emb_k.size(0), dtype=emb_k.dtype)
        deg_inv_sqrt = deg.pow(-0.5)
        deg_inv_sqrt[deg_inv_sqrt == float('inf')] = 0
        norm = deg_inv_sqrt[from_] * deg_inv_sqrt[to_]

        for i in range(self.K):
            emb_k = self.propagate(edge_index=edge_index, x=emb_k, norm=norm)
            embs.append(emb_k)

        emb_final = torch.mean(torch.stack(embs, dim=0), dim=0)

        src = edge_index[0][:int(len(edge_index[0]) / 2)]
        dest = edge_index[1][:int(len(edge_index[0]) / 2)]

        user_embeds = emb_final[src]
        item_embeds = emb_final[dest]

        output = torch.cat([user_embeds, item_embeds], dim=1)
        output = self.out(output)

        return output

    def message(self, x_j, norm):
        return norm.view(-1, 1) * x_j

def LightGCNRecommend(userId):
    user_id = userId
    user_index = user_to_idx[user_id]

    # 准备用户嵌入向量
    with torch.no_grad():
        user_embedding = model.embedding.weight[user_index].to(device)

    # 计算用户和所有电影的相似度得分
    all_movie_embeddings = model.embedding.weight[num_users:].to(device)
    similarity_scores = torch.matmul(user_embedding, all_movie_embeddings.T)

    # 获取得分最高的电影索引
    top_movie_indices = similarity_scores.argsort(descending=True)[:50]

    # 确保idx_to_item包含所有可能的索引
    all_movie_indices = torch.arange(len(item_to_idx), device=device)
    idx_to_item = {i: movie_id for i, movie_id in enumerate(all_movie_indices)}

    # 将索引转换回电影ID，确保索引在字典的键中
    recommended_movie_indices = [idx.item() for idx in top_movie_indices if idx.item() in idx_to_item]
    recommended_movie_ids = [idx_to_item[i].tolist() for i in recommended_movie_indices]

    return  random.sample(recommended_movie_ids, 4)


ratings_threshold = 1
user_to_idx, idx_to_user, item_to_idx, idx_to_item,num_users,num_movies = encode_data()

model_path = "algorithm/LightGCN/best_model_lightgcn.pt"
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# 加载模型
model = LightGCNConv(num_users=num_users,
                     num_items=num_movies,
                     embedding_dim=64, K=2)
model.load_state_dict(torch.load(model_path))
model.eval()  # 设置为评估模式
model = model.to(device)

