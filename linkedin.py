import requests

url = "https://www.linkedin.com/learning-api/searchV2?categorySlugs=List(business)&q=categorySlugs&searchRequestId=wK1tlct9RJiC8FVdxjWyKA%3D%3D&sortBy=RELEVANCE&start=10"

payload={}
headers = {
  # 'authority': 'www.linkedin.com',
  # 'accept': 'application/vnd.linkedin.normalized+json+2.1',
  # 'accept-language': 'en-US,en;q=0.9',
  'cookie': 'lang=v=2&lang=en-us; bcookie="v=2&370a4246-f114-44df-89d2-8b85dea338e2"; bscookie="v=1&20220928151439675477ef-247a-4dc7-850b-fd1eed5794b7AQHfXSE8mui85vY1as2h83ZmLZdQeneB"; G_ENABLED_IDPS=google; G_AUTHUSER_H=0; liap=true; li_at=AQEDASVw1KEDkOd0AAABg4SsOpcAAAGDqLi-l04AifsfabfRC-J8AZ26MWLVjl_tMTPKOpC4ry-sGU0_N6uV7zsFVYbu98Yi3AaFIcjika49B_ZYhB1m3CmQJFQiVv6_HeH-jPC_TXk__ogbJTyY0bsH; JSESSIONID="ajax:8303915952489337726"; timezone=Asia/Karachi; li_theme=light; li_theme_set=app; lil-lang=en_US; lidc="b=TB57:s=T:r=T:a=T:p=T:g=3288:u=339:x=1:i=1664512945:t=1664517067:v=2:sig=AQEx7kA6GipauT3yABoJ86d9YQnJuJyX"; UserMatchHistory=AQIoQg6uk5B1-wAAAYOMxTjJQzBKn49PTWFqU2ylKNqHWf6C1mRrv9RcZlgOp7jd3lmyPmzBMxIVxhvtPe7ReU2GRVuQJ_mPAv3pBOIDK2QWdLBxzCPFlXrTL_q9ujdpHhPCwjRl9STNAq6Hnflx5R7_taZYZS9NNNHFINYLmC9HKq2ZGXr_BCHqFMWYt2ReGH7pZoIn7KE_s-6vCplMn_S2asIVk27sXeyl-h-0-5BLrrK6xWEdDcklBPEiHpQDf3pLe6UAbg; li_mc=MTsyMTsxNjY0NTE0NTk2OzE7MDIxzpPT+t4yiLYi0zdgkgF6AiyL384IeQv2wvyl8hHIPm0=',
  'csrf-token': 'ajax:8303915952489337726',
  'dnt': '1',
  'referer': 'https://www.linkedin.com/learning/topics/business',
  'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
  'x-li-lang': 'en_US',
  'x-li-page-instance': 'urn:li:page:d_learning_topic;STf68cJGQ2OJz1QskxCkOQ==',
  'x-li-track': '{"clientVersion":"1.1.1019","mpVersion":"1.1.1019","osName":"web","timezoneOffset":5,"timezone":"Asia/Karachi","mpName":"learning-web","displayDensity":2.5,"displayWidth":3840,"displayHeight":2160}',
  'x-lil-intl-library': 'en_US',
  'x-restli-protocol-version': '2.0.0'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
