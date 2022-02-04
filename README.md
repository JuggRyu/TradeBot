# TradeBot

■説明
BinanceのADA/USDTを自動売買するBOTです。

また、購入情報はLINEにて通知されます。

■実行環境:python3.7

■以下、必要なimportモジュール

  pandas as pd

  line-bot-sdk

  flask

  ccxt

  requests

■以下、必要なアカウント

LINE Developers

Binance

■以下、settings.py に必要な内容

Binance APIキー、secretキー

LINE Developers チャンネルアクセストークン、ユーザID(LINE IDではない)

※settings.py はTradeBot.py と同階層へ配置してください。

※取引に関する損益につきましては、一切の責任を負いません。
