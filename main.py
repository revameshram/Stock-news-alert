import requests
import smtplib
import json
from dotenv import load_dotenv
import os

load_dotenv()

MY_EMAIL =os.getenv("MY_EMAIL")
MY_PASSWORD =os.getenv("MY_PASSWORD")
NEWS_API=os.getenv("NEWS_API")
API_KEY=os.getenv("API_KEY")

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={API_KEY}&timezone'


try:
    response = requests.get(url)
    data = response.json()
    
    if "Time Series (Daily)" in data:
        time_series = data["Time Series (Daily)"]
        keys = sorted(time_series.keys(), reverse=True)  # Sort latest first
            
        today=keys[0]
        yesterday=keys[1]

        today_open=float(data["Time Series (Daily)"][today]["1. open"])
        
        yesterday_close=float(data["Time Series (Daily)"][yesterday]["4. close"])
            
        diff_in_stock=abs(today_open-yesterday_close)
        percent=(diff_in_stock/yesterday_close)*100
        
        if diff_in_stock >= (0.01*yesterday_close):
            news_url = f"https://newsapi.org/v2/everything?q={COMPANY_NAME}&apiKey={NEWS_API}&sortBy=publishedAt&language=en"
            news_response=requests.get(news_url)
            news_data=news_response.json()
            
            
            top_articles = news_data["articles"][:3]
            news_summary = ""
            for article in top_articles:
                headline = article["title"]
                url = article["url"]
                news_summary += f"\n📰 {headline}\n🔗 {url}\n"

            with smtplib.SMTP("smtp.gmail.com",587) as connection:
                connection.starttls()
                connection.login(MY_EMAIL, MY_PASSWORD)
                
                if today_open>yesterday_close:
                
                    connection.sendmail(
                        from_addr=MY_EMAIL,
                        to_addrs="revameshram28@gmail.com",
                        msg=f"Subject: ⚠️🛑 Daily Stocks Alert! \n\n{STOCK} {COMPANY_NAME} stock has ⬆️increased by {percent:.2f}%.\n📰 Top News Headlines:\n{news_summary}"
                    )
                    
                if today_open < yesterday_close:
                    
                    connection.sendmail(
                    from_addr=MY_EMAIL,
                    to_addrs="revameshram28@gmail.com",
                    msg=f"Subject: ⚠️🛑 Daily Stocks Alert! \n\n{STOCK} {COMPANY_NAME} stock has ⬇️decreased by {percent:.2f}%.\n📰 Top News Headlines:\n{news_summary}"
                    )
                    
        else:
            print("not much change")
                
except (KeyError, IndexError, requests.exceptions.RequestException) as e:
    print("❌ Error occurred:", e)


   
   
   