import pandas
from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import accuracy_score, classification_report
from sklearn.tree import export_graphviz
from sklearn.ensemble import BaggingClassifier
import graphviz
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
import pandas as pd



def Dtree(data,target,new_data,feature_names,target_names):

    testdata = new_data
    pred_tracks = []

    # divide the data set
    x_train, x_test, y_train, y_test = train_test_split(data, target, test_size=0.2, random_state=0)

    # create Decision Tree
    dtc = DecisionTreeClassifier()

    # 使用BaggingClassifier进行集成学习
    bagging = BaggingClassifier(dtc, n_estimators=500, max_samples=0.8)

    # fitting models
    # dtc.fit(x_train, y_train)
    bagging.fit(x_train, y_train)

    # predict
    # train set
    # y_pred = dtc.predict(x_test)
    y_pred = bagging.predict(x_test)

    # accuracy test
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy : ", accuracy)
    # 計算F1-score等指標的報告

    report = classification_report(y_test, y_pred)
    print("classification_report : \n", report)

    # feature importances
    # importances = pd.DataFrame(columns=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
    importances = pd.DataFrame()
    for tree in bagging.estimators_:
        importance = pd.DataFrame(tree.feature_importances_).transpose()
        importances = pd.concat([importances, importance]).reset_index(drop=True)
    means = importances.mean(axis=0)
    mean_dic = {}
    for n,i in enumerate(feature_names.tolist()):
        mean_dic[n] = i
    means = means.rename(mean_dic)
    print(means)

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.barh(range(x_train.shape[1]), means, align='center')
    ax.set_yticks(range(x_train.shape[1]))
    ax.set_yticklabels(feature_names)
    ax.set_xlabel('Importance')
    ax.set_ylabel('Feature')

    plt.subplots_adjust(left=0.3)
    plt.savefig("/Users/bensonyang/Desktop/Side-project/Python/SL_spotify/spotify_chart/Feature_Importances")

    # fig, ax = plt.subplots()
    # ax.bar(range(x_train.shape[1]), means.tolist(), align='center')
    # ax.set_xticks(range(x_train.shape[1]))
    # ax.set_xticklabels(feature_names)
    # ax.set_xlabel('Feature')
    # ax.set_ylabel('Importance')
    # plt.savefig("/Users/bensonyang/Desktop/Side-project/Python/SL_spotify/spotify_chart/Feature_Importances")

    # new set
    for track in testdata:
        new_pred = bagging.predict(track)
        print(new_pred)
        track['pred_type'] = new_pred
        pred_tracks.append(track)

    # print(y_pred)

    # import to new dataset

    result = [pred_tracks,accuracy,bagging]

    return result

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
