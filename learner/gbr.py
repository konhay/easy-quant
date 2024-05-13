# -*- coding: UTF-8 -*-
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import ensemble
from sklearn.metrics import mean_squared_error
import pylab as plot


def gbr(sample_list, target_list):
    """
    GradientBoostingRegressor
    :param sample_list: list [[x11,x12,...],[x21,x22,...],...]
    :param target_list: list [y1,y2,...]
    :return:
    """
    X = np.array(sample_list)
    y = np.array(target_list)

    # take fixed holdout set 30% of data rows
    xTrain, xTest, yTrain, yTest = train_test_split(X, y, test_size=0.30, random_state=531)

    # Train Gradient Boosting learner to minimize mean squared error
    nEst = 2000
    depth = 7
    learnRate = 0.01
    subSamp = 0.5
    wineGBMModel = ensemble.GradientBoostingRegressor(n_estimators=nEst,
                                                      max_depth=depth,
                                                      learning_rate=learnRate,
                                                      subsample=subSamp,
                                                      loss='ls')
    wineGBMModel.fit(xTrain, yTrain)

    # compute mse on test set
    msError = []
    predictions = wineGBMModel.staged_predict(xTest)
    for p in predictions:
        msError.append(mean_squared_error(yTest, p))
    print("MSE")
    print(min(msError))
    print(msError.index(min(msError)))

    predictions_ = wineGBMModel.predict(xTest)
    for i in range(len(yTest)):
        print(round(yTest[i] * 100, 2), round(predictions_[i] * 100, 2))

    # plot training and test errors vs number of trees in ensemble
    plot.figure()
    plot.plot(range(1, nEst + 1), wineGBMModel.train_score_,
              label='Training Set MSE')
    plot.plot(range(1, nEst + 1), msError, label='Test Set MSE')
    plot.legend(loc='upper right')
    plot.xlabel('Number of Trees in Ensemble')
    plot.ylabel('Mean Squared Error')
    plot.show()
