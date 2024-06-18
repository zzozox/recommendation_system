# coding = utf-8

# 基于物品的协同过滤推荐算法实现
import random

import math
import pymysql                          #数据库
from operator import itemgetter

cnn = pymysql.connect(host='127.0.0.1', user='root', password='123456', port=3306, database='flask_douban_comment',
                      charset='utf8')

class ItemBasedCF():
    # 初始化参数
    def __init__(self):
        # 找到相似的10部电影，为目标用户推荐4部电影
        self.n_sim_movie = 8
        self.n_rec_movie = 4

        # 将数据集划分为训练集和测试集
        self.trainSet = {}
        self.testSet = {}

        # 相似度矩阵
        self.movie_sim_matrix = {}
        self.movie_popular = {}
        self.movie_count = 0

        print('Similar movie number = %d' % self.n_sim_movie)
        print('Recommneded movie number = %d' % self.n_rec_movie)

    # 从数据库得到“用户-电影”数据
    def get_dataset(self, pivot=0.75):
        trainSet_len = 0
        testSet_len = 0
        cursor = cnn.cursor()
        sql = ' select * from tb_rate'
        cursor.execute(sql)
        for item in cursor.fetchall():
            user, movie, rating = item[1:]
            self.trainSet.setdefault(user, {})
            self.trainSet[user][movie] = rating
            trainSet_len += 1
            self.testSet.setdefault(user, {})
            self.testSet[user][movie] = rating
            testSet_len += 1
        cursor.close()

        # itemCF.trainSet = {
        #     1: {'A': 5, 'B': 3, 'C': 4},
        #     2: {'A': 4, 'C': 5, 'D': 2},
        #     3: {'B': 2, 'C': 4, 'D': 5},
        #     4: {'A': 3, 'C': 3, 'D': 4}
        # }

        print('Split trainingSet and testSet success!')
        print('TrainSet = %s' % trainSet_len)
        print('TestSet = %s' % testSet_len)

    # 读文件，返回文件的每一行
    def load_file(self, filename):
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i == 0:  # 去掉文件第一行的title
                    continue
                yield line.strip('\r\n')
        print('Load %s success!' % filename)

    # 计算电影之间的相似度
    def calc_movie_sim(self):
        for user, movies in self.trainSet.items():
            for movie in movies:
                if movie not in self.movie_popular:
                    self.movie_popular[movie] = 0
                self.movie_popular[movie] += 1

        # itemCF.movie_popular = {'A': 3, 'B': 2, 'C': 4, 'D': 3}
        # itemCF.movie_count = 4  # 总共4部电影

        self.movie_count = len(self.movie_popular)
        print("Total movie number = %d" % self.movie_count)

        for user, movies in self.trainSet.items():
            for m1 in movies:
                for m2 in movies:
                    if m1 == m2:
                        continue
                    self.movie_sim_matrix.setdefault(m1, {})
                    self.movie_sim_matrix[m1].setdefault(m2, 0)
                    self.movie_sim_matrix[m1][m2] += 1
        print("Build co-rated users matrix success!")

        # # 构建共现矩阵
        # itemCF.movie_sim_matrix = {
        #     'A': {'B': 1, 'C': 3, 'D': 1},
        #     'B': {'A': 1, 'C': 2, 'D': 2},
        #     'C': {'A': 3, 'B': 2, 'D': 3},
        #     'D': {'A': 1, 'B': 2, 'C': 3}
        # }

        # 计算电影之间的相似性 similarity matrix
        print("Calculating movie similarity matrix ...")
        for m1, related_movies in self.movie_sim_matrix.items():
            for m2, count in related_movies.items():
                # 注意0向量的处理，即某电影的用户数为0
                if self.movie_popular[m1] == 0 or self.movie_popular[m2] == 0:
                    self.movie_sim_matrix[m1][m2] = 0
                else:
                    self.movie_sim_matrix[m1][m2] = count / math.sqrt(self.movie_popular[m1] * self.movie_popular[m2])
        print('Calculate movie similarity matrix success!')

        # sim(A, B) =共现次数(A, B)/（电影A的评分次数×电影B的评分次数）^1/2

        # itemCF.movie_sim_matrix = {
        #     'A': {'B': 1 / math.sqrt(3 * 2), 'C': 3 / math.sqrt(3 * 4), 'D': 1 / math.sqrt(3 * 3)},
        #     'B': {'A': 1 / math.sqrt(2 * 3), 'C': 2 / math.sqrt(2 * 4), 'D': 2 / math.sqrt(2 * 3)},
        #     'C': {'A': 3 / math.sqrt(4 * 3), 'B': 2 / math.sqrt(4 * 2), 'D': 3 / math.sqrt(4 * 3)},
        #     'D': {'A': 1 / math.sqrt(3 * 3), 'B': 2 / math.sqrt(3 * 2), 'C': 3 / math.sqrt(3 * 4)}
        # }

    # 针对目标用户U，找到K部相似的电影，并推荐其N部电影
    def recommend(self, user):
        K = self.n_sim_movie
        N = self.n_rec_movie
        rank = {}
        if user > len(self.trainSet):
            user = random.randint(1, len(self.trainSet))
        watched_movies = self.trainSet[user]
        # 用户1看过的电影及其评分
        #watched_movies = {'A': 5, 'B': 3, 'C': 4}

        for movie, rating in watched_movies.items():
            for related_movie, w in sorted(self.movie_sim_matrix[movie].items(), key=itemgetter(1), reverse=True)[:K]:
                if related_movie in watched_movies:
                    continue
                rank.setdefault(related_movie, 0)
                rank[related_movie] += w * float(rating)

        # 电影A(5分)：B(0.29 * 5), C(0.87 * 5), D(0.19 * 5)
        # 电影B(3分)：A(0.29 * 3), C(0.71 * 3), D(0.82 * 3)
        # 电影C(4分)：A(0.87 * 4), B(0.71 * 4), D(0.87 * 4)

        #rank = {'B': 1.45, 'D': 6.89}

        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]

    # 产生推荐并通过准确率、召回率和覆盖率进行评估
    def evaluate(self):
        print('Evaluating start ...')
        N = self.n_rec_movie
        # 准确率和召回率
        hit = 0
        rec_count = 0
        test_count = 0
        # 覆盖率
        all_rec_movies = set()

        for i, user in enumerate(self.trainSet):
            test_moives = self.testSet.get(user, {})
            rec_movies = self.recommend(user)
            for movie, w in rec_movies:
                if movie in test_moives:
                    hit += 1
                all_rec_movies.add(movie)
            rec_count += N
            test_count += len(test_moives)

        precision = hit / (1.0 * rec_count)
        recall = hit / (1.0 * test_count)
        coverage = len(all_rec_movies) / (1.0 * self.movie_count)
        print('precisioin=%.4f\trecall=%.4f\tcoverage=%.4f' % (precision, recall, coverage))

    def rec_one(self,userId):
        print('推荐')
        rec_movies = self.recommend(userId)
        # print(rec_movies)
        return rec_movies

# itemCF 推荐算法接口
def recommend(userId):
    itemCF = ItemBasedCF()
    itemCF.get_dataset()
    itemCF.calc_movie_sim()
    recs = itemCF.rec_one(userId)
    return recs
