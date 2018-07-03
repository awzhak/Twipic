# -*- coding: utf-8 -*-
import tweepy
import datetime
import logging
import sys
import json
import os
import requests
import webbrowser
from time import sleep
from flask import Flask, session, redirect, render_template, request

# Keys
CK = 'wOEXhlK7izfzBN40d6kzFfk6F'
CS = 'wyvYrU0XVsLJjrXTVYuVqIVenXuMkXf4AHZ3q6Nuz4v4BXc94g'
auth = tweepy.OAuthHandler(CK, CS)
# 読み込むTweet数 max:200
count = 200

#
verifier = None
taco = None

# 画像の保存先ディレクトリ
IMAGES_DIR = 'path'

# Flask設定
app = Flask(__name__)
app.secret_key = os.urandom(24)

api = tweepy.API(auth)

# ルートへのアクセス
@app.route('/', methods=['GET'])
def main():
    redirect_url = auth.get_authorization_url()
    session['request_token'] = auth.request_token
    return redirect(redirect_url)

# /likesへのアクセス
@app.route('/likes')
def likes():
    global verifier
    if verifier is None:
        token = session.pop('request_token', None)
        verifier = request.args.get('oauth_verifier')
        auth.request_token = token
        auth.get_access_token(verifier)
        session.pop('oauth_verifier', None)
        verifier = None

    fav = api.favorites(count = count)
    return render_template('likes.html', fav=fav)

# /likedへのアクセス
@app.route('/liked', methods=['POST'])
def liked():
    global taco
    taco = request.form['taco']
    fav = api.favorites(taco, count = count)
    return render_template('likes.html', taco=taco, fav=fav)

# /likeへのアクセス
@app.route('/like')
def like():
    id = request.args.get('id')
    api.create_favorite(id)
    return redirect('javascript:history.go(-1)')

# /retweetへのアクセス
@app.route('/retweet')
def retweet():
    id = request.args.get('id')
    api.retweet(id)
    return redirect('javascript:history.go(-1)')

# Saveボタン
@app.route('/save')
def index2():
    global taco
    fav = api.favorites(taco, count = count)
    for result in fav:
        # Twitter ID
        screen_name = result.user.screen_name
        # ツイート日時
        jst = result.created_at + datetime.timedelta(hours=9)
        time_str = jst.strftime('%Y-%m%d-%H%M%S')
        # 画像付きか
        if 'media' in result.entities:
            # 画像保存
            i = 0
            for media in result.extended_entities['media']:
                url = media['media_url_https']
                i += 1
                filename = IMAGES_DIR + time_str + '_' + screen_name + str(i) + '.' + url.split('.')[-1]

                # :origサイズで画像をダウンロード
                res = requests.get(url+ ':orig')
                with open(os.path.join(filename), 'wb') as fp:
                     fp.write(res.content)
    return redirect('/liked')

# webサーバ起動
if __name__ == '__main__':
        app.run(debug = False)
