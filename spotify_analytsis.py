import time
import itertools
import pymysql
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from ML_function import dTree
from ML_function import strFilter
import json
import random
import warnings
import spotipy
import spotipy.util as util
import requests
import URL_scraper


def SQL(db, querys=[]):
    db_settings = {
        "host": "34.67.132.121",
        "port": 3306,
        "user": "root",
        "password": "",
        "db": db,
        "charset": "utf8"
    }

    conn = pymysql.connect(**db_settings)
    try:

        for query in querys:
            with conn.cursor() as cursor:
                print("query : ", query)
                cursor.execute(query)
                result = cursor.fetchall()
                df = pd.DataFrame(result)
        conn.commit()
        conn.close()
        return df

    except Exception as err:
        print(err)
        conn.close()
        raise (err)


DBtables = SQL("spotify", ['show tables'])
latest_table = DBtables.iloc[len(DBtables) - 1, 0]
print(latest_table)

DBdata = SQL("spotify",
             ["DROP TABLE IF EXISTS `spotify_temp`;  ",
              "CREATE TEMPORARY TABLE `spotify_temp` AS "
              "(SELECT DISTINCT  * , 'Pop' AS source FROM `Spotify_Pop`)"
              "UNION ALL "
              "(SELECT DISTINCT  * , 'Chill' AS source FROM `Spotify_Chill`)"
              "UNION ALL "
              "(SELECT DISTINCT  * , 'EDM' AS source FROM `Spotify_EDM`)"
              "UNION ALL "
              "(SELECT DISTINCT  * , 'HH' AS source FROM `Spotify_HH`)"
              "UNION ALL "
              "(SELECT DISTINCT  * , 'R&B' AS source FROM `Spotify_R&B`);",
              " select * from spotify_temp;"
              ]
             )

DBdata.columns = ["id", "acousticness", "danceability", "energy", "instrumentalness", "loudness", "speechiness",
                  "tempo", "valence", "key", "duration_ms", "Classification", "song_name", "source"]


DBdata["source"] = DBdata["source"].astype(str)
DBdata = DBdata.iloc[:, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13]]

# count nan values
print("missing values : \n", DBdata.isna().sum())
DBdata.dropna(axis=0, inplace=True)

print(DBdata)

DBdata.info()

# create axis
subplot_position = []
x_axis = 2
y_axis = 5
for i in range(x_axis):
    for j in range(y_axis):
        subplot_position.append([i, j])

# set random color
colorplate = []


def set_color():
    for i in range(x_axis * y_axis):
        i = lambda: random.randint(0, 255)
        color = '#%02X%02X%02X' % (i(), i(), i())
        colorplate.append(color)
    return colorplate


# hist chart
###
# fig, axes = plt.subplots(2, 5, figsize=(20, 8), sharex=False): 创建一个 2x5 的子图，每个子图都是一个 Axes 对象，并将这些对象存储在名为 axes 的二维数组中。figsize 指定了整个图形的大小，sharex=False 表示子图不共享 x 轴。
# subplot_position: 每个子图在二维数组中的位置，例如 (0, 0) 表示第一行第一列。
# colorplate: 每个子图所用的颜色。
# DBdata: 包含数据的 DataFrame。
# DBdata.columns[:-1]: 获取除最后一列以外的所有列的名称，即要绘制直方图的变量。
# DBdata.loc[DBdata.source == 'R&B'][column]: 从 DataFrame 中选择 source 列为 'R&B' 的行，并选择指定的 column 列，即要绘制直方图的数据。
# sns.histplot(): 用 seaborn 库绘制直方图，其中的参数包括要绘制的数据、颜色和要使用的 Axes 对象等。kde=True 表示同时绘制密度曲线。
###
#
genres = ["Pop", "Chill", "R&B", "EDM", "HH"]

# fig, axes = plt.subplots(2, 5, figsize=(20, 10), sharex=False)
#
# fig.suptitle("Whole")
# for pos, color, column in zip(subplot_position, set_color(), DBdata.columns[:-1]):
#     sns.histplot(DBdata[column],
#                  color=color,
#                  ax=axes[pos[0],pos[1]]
#                 ,kde=True)
#
# for a, b in itertools.combinations(genres, 2):
#     print(a, b)
#     fig, axes = plt.subplots(2, 5, figsize=(20, 10), sharex=False)
#     fig.suptitle(a+"vs"+b)
#     for pos, color, column in zip(subplot_position, set_color(), DBdata.columns[:-1]):
#         sns.histplot(DBdata.loc[DBdata.source== a ][column],
#                      color=color,
#                      ax=axes[pos[0],pos[1]]
#                      ,kde=True)
#
#         sns.histplot(DBdata.loc[DBdata.source== b ][column],
#                      color=color,
#                      ax=axes[pos[0],pos[1]]
#                      ,kde=True)
#     plt.savefig("/Users/bensonyang/Desktop/Side-project/Python/SL_spotify/spotify_chart/feature_" + a +" vs "+ b )
# plt.show()

DBdata["source"] = DBdata["source"].replace({"Pop": 0, "Chill": 1, "R&B": 2, "EDM": 3, "HH": 4})

tree_data = DBdata.iloc[:, 0:DBdata.shape[1] - 1]
tree_target = DBdata["source"]
tree_feature = DBdata.columns[:-1]
target_name = strFilter.list2dic(genres)


# tree_data.to_csv(
#     'train_data.csv',  # 檔案名稱
#     encoding='utf-8-sig',  # 編碼
#     index=True  # 是否保留index
# )


# https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF top50

username = 'Benson yang'
scope = 'user-library-read'
token = util.prompt_for_user_token(username, scope,
                                   client_id='d0ec07ad19d247f3b12aad4821097d5d',
                                   client_secret='e52c914739db43f7b0c00909c3dd7cc7',
                                   # 注意需要在自己的web app中添加redirect url
                                   redirect_uri='http://localhost:8888/callback')
headers = {"Authorization": "Bearer {}".format(token), "Accept-Language": "en"}

i = "37i9dQZEVXbNG2KDcFcKOF"


def get_song_attributes(response_text):
    return json.loads(response_text)


# create piechart ------------------------------------

tracks = []
track_name = []

URLs = URL_scraper.Spotify_Genre_scraper("https://open.spotify.com/genre/section0JQ5DAzQHECxDlYNI6xD1h")

for n, i in enumerate(URLs):

    responses = requests.get("https://api.spotify.com/v1/playlists/" + i, headers=headers)
    myjson_data = json.loads(responses.text)

    # song's attribute
    songs_attributes = []
    songs_analysis = []

    # song'name
    songs_names = []

    # classification
    songs_CF = strFilter.filter_emoji(myjson_data.get('name'))

    # 这边先放其中一个歌单的歌曲请求
    for i in myjson_data.get('tracks')['items']:
        song_ids = i['track']['uri'].split(':')[2]
        # print(song_ids)
        song_name = i['track']['name']

        song_attributes = requests.get(f"https://api.spotify.com/v1/audio-features/{song_ids}", headers=headers)
        songs_attributes.append(get_song_attributes(song_attributes.text))
        songs_names.append(song_name)

    # add name to song attributes
    songs = pd.DataFrame(songs_attributes)
    songs['song_name'] = songs_names

    # label owner name to dataframe
    songs['Classification'] = songs_CF
    track_name.append(songs_CF)

    # 欄位順序
    columns_order = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'loudness',
                     'speechiness', 'tempo', 'valence', 'key', 'duration_ms', 'Classification',
                     'song_name'
                     ]
    #
    # columns_order = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'loudness',
    #                  'speechiness', 'tempo', 'valence', 'duration_ms', 'Classification',
    #                  'song_name'
    #                  ]

    # 重新排列列的順序
    songs = songs[columns_order]
    songs = songs.iloc[:, 0:songs.shape[1] - 2]

    tracks.append(songs)
    print("tracks : ", n)

    # if n == 0:
    #     break



# decision tree
ML = dTree.Dtree(tree_data, tree_target, tracks, tree_feature, target_name)

# return predicted tracks
test_tracks = ML[0]
for n, i in enumerate(test_tracks):
    test_track = pd.DataFrame(i)
    test_track["pred_type"] = test_track["pred_type"].replace({0: "Pop", 1: "Chill", 2: "R&B", 3: "EDM", 4: "HH"})

    test_track.to_csv(
        "/Users/bensonyang/Desktop/Side-project/Python/SL_spotify/spotify_chart/genre_" + track_name[n] + '_pred.csv',
        # 檔案名稱
        encoding='utf-8-sig',  # 編碼
        index=True  # 是否保留index
    )

    # 資料集
    categories = genres
    data = [test_track["pred_type"].value_counts().get('Pop', 0),
            test_track["pred_type"].value_counts().get('Chill', 0),
            test_track["pred_type"].value_counts().get('R&B', 0),
            test_track["pred_type"].value_counts().get('HH', 0),
            test_track["pred_type"].value_counts().get('EDM', 0)]

    # 繪製圓餅圖
    plt.pie(data, labels=categories, autopct='%1.1f%%')

    # 設定圖表標題
    plt.title(track_name[n])

    # 顯示圖表
    plt.savefig("/Users/bensonyang/Desktop/Side-project/Python/SL_spotify/spotify_chart/genre_" + track_name[n])
    plt.clf()
    print("PieChart", n)
