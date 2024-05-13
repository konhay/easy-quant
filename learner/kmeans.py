from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.preprocessing import scale
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import joblib
from mpl_toolkits.mplot3d import Axes3D


def print_mean(frame, n, col_list):
    for i in range(n):
        frame = frame[frame.label==i]
        ct = len(frame)
        print("cluster"+str(i)+": "+str(ct))
        mean_list = []
        for j in range(len(col_list)):
            mean_value = round(np.mean(frame[col_list[j]]),4)
            mean_list.append(mean_value)
        print(mean_list)


def find_cent(df, frame, centroids):
    for j in range(len(centroids)):
        tmp= abs(df- centroids[j])
        lst= []
        for i in range(tmp.shape[1]):
            idx = (tmp[i]).tolist().index(min(tmp[i]))
            lst.append(frame.ix[idx][i])
        print("cluster"+str(j)+": "+str(lst)+" "+str(len(frame[frame.label==j])))


def draw_scatter(n, X_scale, frame):
    tsne = TSNE()
    tsne.fit_transform(X_scale)
    X_tsne = pd.DataFrame(tsne.embedding_, index=frame.index)
    ax = plt.subplot(111)
    for i in range(n):
        d = X_tsne[frame['label']==i]
        ax.scatter(d[0], d[1])
    plt.show()


def draw_scatter_3d(frame, X_scale, n):
    X_tsne = pd.DataFrame(X_scale, index=frame.index)
    x, y, z = X_tsne[2], X_tsne[0], X_tsne[1]
    ax = plt.subplot(111, projection='3d')
    for i in range(n):
        ax.scatter(x[frame.label==i], y[frame.label==i], z[frame.label==i])
    ax.set_zlabel('Z')
    ax.set_ylabel('Y')
    ax.set_xlabel('X')
    plt.show()


def kmeans(df, n):
    """

    :param df:
    :param n: number of clusters
    :return:
    """
    X_train = np.array(df[['v1', 'v2', 'v3', 'v4']].values)
    X_scale = scale(X_train)

    estimator = KMeans(n_clusters=n)
    estimator.fit(X_scale)
    label_pred = estimator.labels_
    centroids = estimator.cluster_centers_
    inertia = estimator.inertia_
    df['label'] = label_pred

    # print("mean")
    # print_mean(df, n)
    # print("cent")

    # df_ = pd.DataFrame(X_scale, index=df.index)
    # find_cent(df_, df, centroids)
    # draw_scatter_3d(df, X_scale, n)

    return df


def kmeans_eclient(df):
    """
    Test method for EastMoney Client image dataset
    :param df:
    :return:
    """
    x = np.array(df.values)
    index = df.index.values
    n_clusters = 10
    k_means = KMeans(n_clusters=n_clusters, random_state=10)
    k_means.fit(x)

    # Print the k-th center
    print(k_means.cluster_centers_)
    # Print the cluster to which each sample belongs
    for i in range(len(index)):
        print(index[i], k_means.labels_[i])
    # It is used to evaluate whether the number of clusters is appropriate.
    # The smaller the distance is, the better the cluster is divided
    print(k_means.inertia_)

    # Make a prediction
    print(k_means.predict(x))
    y_predict = k_means.predict(x)

    # Save model
    joblib.dump(k_means , './kmeans-c9.pkl')

    # Load model
    k_means = joblib.load('./kmeans-c9.pkl')

    # Select the number of clusters of critical points
    for i in range(5,30,1):
        k_means = KMeans(n_clusters=i)
        s = k_means.fit(x)
        print(i, k_means.inertia_)

    x = range(468)
    for i in range(n_clusters):
        y = (341 - k_means.cluster_centers_ - 1)[i]
        plt.plot(x, y)

    plt.title('line chart')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()