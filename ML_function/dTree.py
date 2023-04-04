from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.tree import export_graphviz
from sklearn.ensemble import BaggingClassifier
import graphviz
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
import pandas as pd



def Dtree(data,target,new_data,feature_names,target_names):

    testdata = new_data

    # divide the data set
    x_train, x_test, y_train, y_test = train_test_split(data, target, test_size=0.2, random_state=0)

    # create Decision Tree
    dtc = DecisionTreeClassifier()

    # 使用BaggingClassifier进行集成学习
    bagging = BaggingClassifier(dtc, n_estimators=400, max_samples=0.8)

    # fitting models
    # dtc.fit(x_train, y_train)
    bagging.fit(x_train, y_train)

    # predict
    # train set
    y_pred = bagging.predict(x_test)

    # new set
    new_pred = bagging.predict(testdata)

    print(y_pred)
    print(new_pred)

    # import to new dataset
    testdata['pred_type'] = new_pred

    # accuracy test
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)



    result = [y_pred,accuracy,bagging,testdata]

    return

    # bagging to chart
    # for i, estimator in enumerate(bagging.estimators_):
    #     print(i)
    #     plt.figure(figsize=(20, 10))
    #     plot_tree(estimator, feature_names=feature_names, filled=True)
    #     plt.title('Tree {}'.format(i))
    #     # plt.show()
    #     plt.savefig("/Users/bensonyang/Desktop/Side-project/Python/SL_spotify/tree_chart/tree_chart_"+str(i),dpi=1028)


    # # 將Decision Tree轉換為Graphviz格式
    # dot_data = export_graphviz(dtc, out_file=None,
    #                          feature_names=feature_names,
    #                          class_names=target_names,
    #                          filled=True, rounded=True,
    #                          special_characters=True)
    # graph = graphviz.Source(dot_data)
    #
    # # 顯示Decision Tree
    # graph.view()
