# -*- coding: utf-8 -*-
from flask import (Flask, request, jsonify, render_template)
from pywebpush import webpush, WebPushException
import os
from flask_cors import CORS

app = Flask(__name__)
port = int(os.environ.get("PORT", "3500"))
CORS(app) # CORS(app) 等於 CORS(app, resources={r"/*": {"origins": "*"}})

public_key = 'BI71JOpQDfwAttma_GJ2pIXLvpV3SqLzMHP92Q1snHUnCtUBoBCJyBYiwkX-4_4Z64rVtDW86kzG3peFHmAn88s'
private_key = 'FesoGZ-SCIKVTaEQSAO8g1gpcgwAT1lqqz6YRa6_Yx4'
my_db = {}

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route("/public", methods=["GET"])
def public():
    response = dict(status_code=200, message=public_key)
    return jsonify(response), 200

@app.route("/subscribe", methods=["POST"])
def subscribe():
    if request.is_json: # content_type == 'application/json'
        uid = request.json.get("uid")
        subscription_info = request.json.get("subscription_info")
        print('=========================================================')
        print(uid, subscription_info)
        print('=========================================================')
        # 比對 uid 是否有重複的 subscription_info

        # 無重複，將 subscription_info 存入資料庫
        my_db[uid] = subscription_info
        print('my_db', my_db)

        webpush(
            subscription_info,
            data="v1 push test",
            vapid_private_key=private_key,
            vapid_claims={"sub": "mailto:kikimiao1995@gmail.com"}
        )
        response = dict(message="Successfully subscribed")
        return jsonify(response), 200
    else:
        return "Content type is not supported."
    pass

@app.route("/unsubscribe", methods=["POST"]) # @app.route("/subscribe", methods=["DELETE"])
def unsubscribe():
    if request.is_json:
        uid = request.json.get("uid")
        subscription_info = request.json.get("subscription_info")
        print(uid, subscription_info)
        # 比對 uid 是否有存在 subscription_info
        # 將存在的 subscription_info 從資料庫中刪除
        response = dict(message="Successfully unsubscribed")
        return jsonify(response), 200
    else:
        return "Content type is not supported."
    pass

# trigger web-push event
def send_webpush(subscription_info, title='New message!', message=''):
    payload = {
        "notification": {
            "title": title,
            "body": message
        }
    }
    # return webpush(
    #     subscription_info,
    #     data=jsonify(payload),
    #     vapid_private_key=private_key,
    #     vapid_claims={"sub": "mailto:kikimiao1995@gmail.com"}
    # )
    # print('subscription_info: ', subscription_info, 'paylod:', payload)
    return webpush(
        subscription_info,
        data="v1 push test",
        vapid_private_key=private_key,
        vapid_claims={"sub": "mailto:kikimiao1995@gmail.com"}
    )

# demo
@app.route("/send-notfication", methods=["POST"])
def send_notfication():
    subscription_info = request.json.get("subscription_info")
    title = request.json.get("title")
    message = request.json.get("message")
    # response = dict(subscription_info=subscription_info, title=title, message=message)
    # print(response)
    try:
        send_webpush(subscription_info)
        return jsonify({'message': 'Notification sent successfully'}), 200
    except WebPushException as e:
        print(e)
        return jsonify({'message': 'Notification failed to send'})


if __name__ == "__main__":
    app.run(debug=True, port=port)
