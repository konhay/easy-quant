import math
import numpy as np
from rdp import rdp


def get_cv(df_bar):
    """
    Get coefficient of variation for bar dataframe
    :param df_bar:
    :return:
    """
    def cov(se):
        return np.std(se) / np.mean(se)
    cv = cov(df_bar['volume'])
    return cv


def get_rdp(arr, epsilon):
    """
    Ramer-Douglas-Peucker algorithm
    :param arr:
    :param epsilon:
    :return:
    """
    rdps = rdp(arr, epsilon)
    return rdps


def calculate_euclid(point_a, point_b):
    """
    @category: Similarity
    :param point_a: a data point of curve_a
    :param point_b: a data point of curve_b
    :return: The Euclid distance between point_a and point_b
    """
    return math.sqrt((point_a - point_b)**2)


def calculate_frechet_distance(dp, i, j, curve_a, curve_b):
    """
    @category: Similarity
    :param dp: The distance matrix
    :param i: The index of curve_a
    :param j: The index of curve_b
    :param curve_a: The data sequence of curve_a
    :param curve_b: The data sequence of curve_b
    :return: The frechet distance between curve_a[i] and curve_b[j]
    """
    if dp[i][j] > -1:
        return dp[i][j]
    elif i == 0 and j == 0:
        dp[i][j] = calculate_euclid(curve_a[0], curve_b[0])
    elif i > 0 and j == 0:
        dp[i][j] = max(calculate_frechet_distance(dp, i-1, 0, curve_a, curve_b), calculate_euclid(curve_a[i], curve_b[0]))
    elif i == 0 and j > 0:
        dp[i][j] = max(calculate_frechet_distance(dp, 0, j-1, curve_a,curve_b), calculate_euclid(curve_a[0],curve_b[j]))
    elif i > 0 and j > 0:
        dp[i][j] = max(min(calculate_frechet_distance(dp, i-1, j, curve_a, curve_b), calculate_frechet_distance(dp, i-1, j-1, curve_a, curve_b), calculate_frechet_distance(dp, i, j-1, curve_a, curve_b)), calculate_euclid(curve_a[i], curve_b[j]))
    else:
        dp[i][j] = float("inf")
    return dp[i][j]


def get_similarity(curve_a, curve_b):
    """
    @category: Similarity
    @reference: https://blog.csdn.net/qq_42517334/article/details/103506868
    :param curve_a:
    :param curve_b:
    :return:
    """
    dp = [[-1 for _ in range(len(curve_b))] for _ in range(len(curve_a))]
    similarity = calculate_frechet_distance(dp, len(curve_a)-1, len(curve_b)-1, curve_a, curve_b)
    return max(np.array(dp).reshape(-1, 1))[0]

