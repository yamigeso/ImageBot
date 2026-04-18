"""
Replit 用のキープアライブ Web サーバー
=====================================

Replit の無料プランでは一定時間アクセスがないとプロセスが停止するため、
簡単な Flask サーバーを立てて外部から定期的にアクセスしてもらうことで
BOT を起動し続けられるようにする。

UptimeRobot (https://uptimerobot.com/) などで、Replit の Web URL に
5分おきに HTTP リクエストを送るよう設定すると常時稼働させられる。
"""

from threading import Thread

from flask import Flask


app = Flask("")


@app.route("/")
def home() -> str:
    return "Discord BOT is alive!"


def run() -> None:
    # 0.0.0.0 で listen しないと Replit の外から届かない
    app.run(host="0.0.0.0", port=8080)


def keep_alive() -> None:
    """BOT 本体と並行して Web サーバーを別スレッドで起動する。"""
    t = Thread(target=run, daemon=True)
    t.start()
