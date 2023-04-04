import json
import random
import warnings
import spotipy
import seaborn as sns
import matplotlib.pyplot as plt
import spotipy.util as util
import requests
import pandas as pd
import datetime
import numpy as np
import URL_scraper
import pymysql
import re

total_songs = pd.DataFrame()

username = 'Benson yang'
scope = 'user-library-read'
token = util.prompt_for_user_token(username,scope,
                          client_id='d0ec07ad19d247f3b12aad4821097d5d',
                          client_secret='e52c914739db43f7b0c00909c3dd7cc7',
                          # 注意需要在自己的web app中添加redirect url
                          redirect_uri='http://localhost:8888/callback')
headers = {"Authorization": "Bearer {}".format(token), "Accept-Language": "en"}


# responses = requests.get("https://api.spotify.com/v1/playlists/37i9dQZEVXbNG2KDcFcKOF", headers=headers)

# "https://open.spotify.com/genre/section0JQ5DAzQHECxDlYNI6xD1h" top 50
# "https://open.spotify.com/genre/section0JQ5IMCbQBLoSVpnseIhn6" pop
# "https://open.spotify.com/genre/section0JQ5IMCbQBLvzsc9IsbuOK" K pop
# "https://open.spotify.com/genre/section0JQ5IMCbQBLvhGBYx1XOBO" chill
# "https://open.spotify.com/genre/section0JQ5IMCbQBLimFASeYpIu3" Classic Blue
# "https://open.spotify.com/genre/section0JQ5IMCbQBLjM0PD2WsCNe" Electronic
# "https://open.spotify.com/genre/section0JQ5IMCbQBLuRvGbRRoxQW" R&B

def filter_emoji(desstr, restr=''):
    # 过滤表情
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)


# URLs = URL_scraper.Spotify_Genre_scraper("https://open.spotify.com/genre/section0JQ5IMCbQBLuRvGbRRoxQW")
URLs = range(1)
for n, i in enumerate(URLs):
    # track_id = "37i9dQZEVXbNG2KDcFcKOF"
    responses = requests.get("https://api.spotify.com/v1/playlists/"+"37i9dQZEVXbNG2KDcFcKOF", headers=headers)
    myjson_data = json.loads(responses.text)


    # song's attribute
    songs_attributes = []
    songs_analysis = []

    #song'name
    songs_names = []
    # classification
    songs_CF = filter_emoji(myjson_data.get('name'))

    def get_song_attributes(response_text):
        return json.loads(response_text)

    #这边先放其中一个歌单的歌曲请求
    for i in myjson_data.get('tracks')['items']:
        song_ids = i['track']['uri'].split(':')[2]
        # print(song_ids)
        song_name = i['track']['name']

        song_analysis = requests.get(f"https://api.spotify.com/v1/audio-analysis/{song_ids}", headers=headers)
        songs_analysis.append(get_song_attributes(song_analysis.text))

        song_attributes = requests.get(f"https://api.spotify.com/v1/audio-features/{song_ids}", headers=headers)
        songs_attributes.append(get_song_attributes(song_attributes.text))
        songs_names.append(song_name)



    # add name to song attributes
    songs = pd.DataFrame(songs_attributes)
    songs['song_name'] = songs_names

    #label owner name to dataframe
    songs['Classification'] = songs_CF


    # all in one
    total_songs = pd.concat([total_songs,songs]).reset_index(drop=True)
    print(n,'times')

    if n == 50:
        break

# insert to database ------------------------------------------------
def SQL(table,db, kind, df_insert=""):
    now = datetime.datetime.now()
    date_time_str = now.strftime("%Y-%m-%d")

    try:
        db_settings = {
            "host": "34.67.132.121",
            "port": 3306,
            "user": "root",
            "password": "",
            "db": db,
            "charset": "utf8"
        }
        conn = pymysql.connect(**db_settings)

        if kind == "create":
            with conn.cursor() as cursor:

                cursor.execute("DROP TABLE IF EXISTS "'`' + str(date_time_str) + '_' + table+'`')

                cursor.execute(
                    'CREATE TABLE ' + '`' + str(date_time_str) + '_'+table+'`(' +
                    '`id` INT NOT NULL AUTO_INCREMENT,' +
                    '`acousticness` FlOAT NOT NULL,' +
                    '`danceability` FlOAT NOT NULL,' +
                    '`energy` FlOAT NOT NULL,' +
                    '`instrumentalness` FlOAT NOT NULL,' +
                    '`loudness` FlOAT NOT NULL,' +
                    '`speechiness` FlOAT NOT NULL,' +
                    '`tempo` INT NOT NULL,' +
                    '`valence` FlOAT NOT NULL,' +
                    '`key` FlOAT NOT NULL,' +
                    '`duration_ms` FlOAT NOT NULL,' +
                    '`Classification` VARCHAR(128),' +
                    '`song_name` VARCHAR(512),' +
                    'PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;'
                )

        if kind == "insert":

            df = df_insert

            values = []

            for i in range(len(df)):
                values.append(tuple(df.iloc[i, :]))

            head = 'INSERT INTO ' + db + ".`" + str(
                date_time_str) + "_"+table + """` (acousticness,danceability,energy,instrumentalness,loudness,speechiness,tempo,valence,`key`,duration_ms,Classification,song_name) """ \
                   + """VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            print('-------------print query--------------')
            # print(head)
            print(values)
            with conn.cursor() as cursor:
                cursor.executemany(str(head), (values))
                insert = cursor.fetchall()
                conn.commit()
                conn.close()

            print(insert)

    except Exception as err:
        print(err)

        conn.close()
        raise (err)



#get attributes we need
data = total_songs[[ 'acousticness','danceability','energy','instrumentalness',
                    'loudness','speechiness','tempo',
                    'valence','key','duration_ms','Classification','song_name'
                   ]]

data.to_csv(
        'report.csv', # 檔案名稱
        encoding = 'utf-8-sig', # 編碼
        index=True # 是否保留index
        )

# import to database
# SQL("Blues","spotify", "create")
# SQL("Blues","spotify", "insert",data)


# normalization时我们需要ignore 文本数据，比如 歌曲名和 Owner
data_num = data.select_dtypes(include=[np.number])
data_norm = (data_num - data_num.mean()) / (data_num.max() - data_num.min())
data_norm[['Classification','song_name']]  = data[['Classification','song_name']]

# SQL("Blues_norm","spotify", "create")
# SQL("Blues_norm","spotify", "insert",data_norm)

data_norm.to_csv(
        'report.csv', # 檔案名稱
        encoding = 'utf-8-sig', # 編碼
        index=True # 是否保留index
        )


# chart----------------------------------------------------------------------------------------

# create axis
subplot_position = []
x_axis = 2
y_axis = 5
for i in range(x_axis):
    for j in range(y_axis):
        subplot_position.append([i, j])


#set random color
colorplate = []
def set_color():
    for i in range(x_axis*y_axis):
        i = lambda: random.randint(0,255)
        color = '#%02X%02X%02X' % (i(),i(),i())
        colorplate.append(color)
    return colorplate


#chart
fig, axes = plt.subplots(2, 5, figsize=(20, 10), sharex=False)
for pos, color, column in zip(subplot_position, set_color(), data_norm.columns[:-2]):
    sns.histplot(data_norm[column],
                 color=color,
                 ax=axes[pos[0],pos[1]]
                ,kde=True)
plt.show()





#对比
# f, axes = plt.subplots(2, 4, figsize=(20, 8), sharex=False)
# for pos, color, column in zip(subplot_position, colorplate, data_norm.columns[:-2]):
#     sns.distplot(data_norm.loc[data_norm.Owner=='Anwar'][column],
#                  color=color,
#                  ax=axes[pos[0],pos[1]])
#     sns.distplot(data_norm.loc[data_norm.Owner=='Alex'][column],
#                  color=color,
#                  ax=axes[pos[0],pos[1]])