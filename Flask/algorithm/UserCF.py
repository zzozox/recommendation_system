# coding = utf-8

# 基于用户的协同过滤推荐算法实现
import random

import math
from operator import itemgetter
import pymysql     #数据库

cnn = pymysql.connect(host='127.0.0.1', user='root', password='123456', port=3306, database='flask_douban_comment',
                      charset='utf8')

#1、搜索最相似的用户
#2、 计算u和新item的相似度
class UserBasedCF():
    # 初始化相关参数
    def __init__(self):
        # 找到与目标用户兴趣相似的4个用户，为其推荐4部电影
        self.n_sim_user = 4
        self.n_rec_movie = 4

        # 将数据集划分为训练集和测试集
        self.trainSet = {}
        self.testSet = {}

        # 用户相似度矩阵
        self.user_sim_matrix = {}
        self.movie_count = 0

        print('Similar user number = %d' % self.n_sim_user)
        print('Recommneded movie number = %d' % self.n_rec_movie)


    # 读文件得到“用户-电影”数据
    def get_dataset(self, pivot=0.75):
        trainSet_len = 0
        testSet_len = 0
        cursor = cnn.cursor()
        sql = ' select * from tb_rate'
        cursor.execute(sql)
        for item in cursor.fetchall():
            user, movie, rating = item[1:]
            if random.random() < pivot:
                self.trainSet.setdefault(user, {})
                self.trainSet[user][movie] = rating
                trainSet_len += 1
            else:
                self.testSet.setdefault(user, {})
                self.testSet[user][movie] = rating
                testSet_len += 1
        print('Split trainingSet and testSet success!')
        print('TrainSet = %s' % trainSet_len)
        print('TestSet = %s' % testSet_len)

        # userCF.trainSet = {
        #     1: {'A': 5, 'B': 3, 'C': 4},
        #     2: {'A': 4, 'C': 5, 'D': 2},
        #     3: {'B': 2, 'C': 4, 'D': 5},
        #     4: {'A': 3, 'C': 3, 'D': 4}
        # }

        cursor.close()

    # 读文件，返回文件的每一行
    def load_file(self, filename):
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i == 0:  # 去掉文件第一行的title
                    continue
                yield line.strip('\r\n')
        print('Load %s success!' % filename)


    # 计算用户之间的相似度
    def calc_user_sim(self):
        # 构建“电影-用户”倒排索引
        # key = movieID, value = list of userIDs who have seen this movie
        print('Building movie-user table ...')
        movie_user = {}
        for user, movies in self.trainSet.items():
            for movie in movies:
                if movie not in movie_user:
                    movie_user[movie] = set()
                movie_user[movie].add(user)
        print('Build movie-user table success!')

        # 构建“电影 - 用户”倒排索引
        # movie_user = {
        #     'A': {1, 2, 4},
        #     'B': {1, 3},
        #     'C': {1, 2, 3, 4},
        #     'D': {2, 3, 4}
        # }

        self.movie_count = len(movie_user)
        print('Total movie number = %d' % self.movie_count)

        print('Build user co-rated movies matrix ...')
        for movie, users in movie_user.items():
            for u in users:
                for v in users:
                    if u == v:
                        continue
                    self.user_sim_matrix.setdefault(u, {})
                    self.user_sim_matrix[u].setdefault(v, 0)
                    self.user_sim_matrix[u][v] += 1
        print('Build user co-rated movies matrix success!')

        # 构建用户共现矩阵
        # 不同的用户之之间，共同对一部电影评分的出现次数
        # user_sim_matrix = {
        #     1: {2: 2, 3: 1, 4: 2},
        #     2: {1: 2, 3: 2, 4: 2},
        #     3: {1: 1, 2: 2, 4: 2},
        #     4: {1: 2, 2: 2, 3: 2}
        # }

        # 计算相似性
        print('Calculating user similarity matrix ...')
        for u, related_users in self.user_sim_matrix.items():
            for v, count in related_users.items():
                #分子为共同评分的电影数量。
                #分母为用户1和用户2分别评分电影数量的乘积的平方根
                self.user_sim_matrix[u][v] = count / math.sqrt(len(self.trainSet[u]) * len(self.trainSet[v]))
        print('Calculate user similarity matrix success!')

        # user_sim_matrix = {
        #     1: {2: 2 / math.sqrt(3 * 3), 3: 1 / math.sqrt(3 * 3), 4: 2 / math.sqrt(3 * 3)},
        #     2: {1: 2 / math.sqrt(3 * 3), 3: 2 / math.sqrt(3 * 3), 4: 2 / math.sqrt(3 * 3)},
        #     3: {1: 1 / math.sqrt(3 * 3), 2: 2 / math.sqrt(3 * 3), 4: 2 / math.sqrt(3 * 3)},
        #     4: {1: 2 / math.sqrt(3 * 3), 2: 2 / math.sqrt(3 * 3), 3: 2 / math.sqrt(3 * 3)}
        # }


    # 针对目标用户U，找到其最相似的K个用户，产生N个推荐
    def recommend(self, user):
        K = self.n_sim_user
        N = self.n_rec_movie
        rank = {}
        if user > len(self.trainSet):
            user = random.randint(1, len(self.trainSet))
        watched_movies = self.trainSet[user]

        # watched_movies = {'A': 5, 'B': 3, 'C': 4}
        # v=similar user, wuv=similar factor
        for v, wuv in sorted(self.user_sim_matrix[user].items(), key=itemgetter(1), reverse=True)[0:K]:
            for movie in self.trainSet[v]:
                if movie in watched_movies:
                    continue
                rank.setdefault(movie, 0)
                rank[movie] += wuv

        # 对于用户2（相似度0.67），他的电影及评分：
        #  电影A：0.67（已经看过，跳过）
        #  电影C：0.67（已经看过，跳过）
        #  电影D：0.67

        # 对于用户3（相似度0.33），他的电影及评分：
        # 电影B：0.33（已经看过，跳过）
        # 电影C：0.33（已经看过，跳过）
        # 电影D：0.33

        # 对于用户4（相似度0.67），他的电影及评分：
        # 电影A：0.67（已经看过，跳过）
        # 电影C：0.67（已经看过，跳过）
        # 电影D：0.67

        # 最终推荐评分：
        # 电影
        # 推荐评分
        # 电影D
        # 0.67*（用户2对D的评分） + 0.33*（用户3对D的评分） + 0.67*（用户4对D的评分） = 1.67

        return sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]

    def rec_one(self, userId):
        print('推荐')
        rec_movies = self.recommend(userId)
        return rec_movies

    # 产生推荐并通过准确率、召回率和覆盖率进行评估
    def evaluate(self):
        print("Evaluation start ...")
        N = self.n_rec_movie
        # 准确率和召回率
        hit = 0
        rec_count = 0
        test_count = 0
        # 覆盖率
        all_rec_movies = set()

        for i, user, in enumerate(self.trainSet):
            test_movies = self.testSet.get(user, {})
            rec_movies = self.recommend(user)
            for movie, w in rec_movies:
                if movie in test_movies:
                    hit += 1
                all_rec_movies.add(movie)
            rec_count += N
            test_count += len(test_movies)

        precision = hit / (1.0 * rec_count)
        recall = hit / (1.0 * test_count)
        coverage = len(all_rec_movies) / (1.0 * self.movie_count)
        print('precisioin=%.4f\trecall=%.4f\tcoverage=%.4f' % (precision, recall, coverage))

# userCF 推荐算法接口
def recommend(userId):
    userCF = UserBasedCF()
    userCF.get_dataset()
    userCF.calc_user_sim()
    reclist = []
    recs = userCF.rec_one(userId)
    return recs

    # for movie, rate in recs:
    #     # print(movie, rate)
    #     # cursor = cnn.cursor()
    #     # sql = ' select * from tb_movie where id=%d' % movieId
    #     # cursor.execute(sql)
    #     # movie = cursor.fetchone()
    #     reclist.append(dict(item=movie, rate=rate))
    # # itemCF.evaluate()
    # return reclist
    # print(reclist)
