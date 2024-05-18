import mojito
import pprint

def buy_us_stock(key, secret, acc_no, exchange, ticker, price, quantity):
    if exchange == 'NASDAQ':
        exchange = '나스닥'
    elif exchange == 'NYSE':
        exchange = '뉴욕'
    elif exchange == 'AMEX':
        exchange = '아멕스'
    broker = mojito.KoreaInvestment(
        api_key=key,
        api_secret=secret,
        acc_no=acc_no,
        exchange=exchange
    )
    resp = broker.create_limit_buy_order(
        symbol=ticker,
        price=price,
        quantity=quantity
    )

    print(f"{ticker} on {exchange}: {quantity}주 매수")
    return resp

def sell_us_stock(key, secret, acc_no, exchange, ticker, price, quantity):
  if exchange == 'NASDAQ':
      exchange = '나스닥'
  elif exchange == 'NYSE':
      exchange = '뉴욕'
  elif exchange == 'AMEX':
      exchange = '아멕스'
  broker = mojito.KoreaInvestment(
      api_key=key,
      api_secret=secret,
      acc_no=acc_no,
      exchange=exchange
  )
  resp = broker.create_limit_sell_order(
      symbol=ticker,
      price=price,
      quantity=quantity
  )

  print(f"{ticker} on {exchange}: {quantity}주 매도")
  return resp
