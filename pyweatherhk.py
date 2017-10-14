"""
Crawling 

 information
May be update for other places later?
  
  Further Link for updating the Hong Kong wrapping function.
  http://www.weather.gov.hk/cis/climat_c.htm
  http://www.weather.gov.hk/cgi-bin/hko/5dnor_c.pl?syr=2017&smon=10&sday=14

"""

"""Import: """
import os, re, requests, time, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")

from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from dateutil import parser

HTML_PARSER = "html.parser"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}

def wrapweather(date=(datetime.now()-timedelta(days=1)), start=None, end=None):
  """ 
  Wrapping from http://www.hko.gov.hk/cgi-bin/hko/yes.pl
  which contain Temp and GammaRad in difficult areas of Hong Kong 
  Args: date, datetime type variable, default as datetime.now()
        start, datetime type variable, a pair with end
        end, datetime type variable, a pair with start
  """
  urlhead = 'http://www.hko.gov.hk/cgi-bin/hko/yes.pl?'
  if start == None and end == None:
    url = urlhead + 'year={0}&month={1}&day={2}&language=english&B1'.format(date.strftime('%Y'),date.strftime('%m'),date.strftime('%d'))
    df0 = wrapping(url)
    
  elif start != None and end != None:
    def urlgenerate(start, end):
      l = []
      delta = timedelta(days=1)
      while(start <= end):
        urltail = 'year={0}&month={1}&day={2}&language=english&B1'.format(start.strftime('%Y'),start.strftime('%m'),start.strftime('%d'))
        l.append(urlhead + urltail)
        start += delta
      return l
    urllist = urlgenerate(start, end)
    counter = 0
    for url in urllist:
      for i in range(0, 5):
        try: # to prevent ConnectionRestError104.
          if counter == 0:
            print('  Start Crawling Weather from {0}'.format(str(start)))
            df0 = wrapping(url)
          else:
            df1 = wrapping(url)
            df0 = pd.concat([df0,df1], axis=1)
          break
        except:
          pass
      counter += 1
      if counter % 10 == 0:
        print('    Now is wrapping %d th days.' % counter)
        
  df0.columns = df0.loc['Date']
  df0 = df0.drop('Date', axis=0).T.fillna(method='ffill') 
  return df0
  
  
def wrapping(url):
  """ Wrap with url: 
    'http://www.hko.gov.hk/cgi-bin/hko/yes.pl?year={0}&month={1}&day={2}&language=english&B1'.format(start.strftime('%Y'),
      start.strftime('%m'),start.strftime('%d')
    '
  """
  d = {}
  list_req = requests.get(url, headers=headers)
  if(list_req.status_code == requests.codes.ok):
    soup = BeautifulSoup(list_req.content, HTML_PARSER)
    rawdata = str(soup.find('pre').text)

    # Crwaling with checking whether there is the target string s
    for line in rawdata.splitlines():
      l = []
      for s in ['Daily Weather Summary','Maximum Air Temperature','Minimum Air Temperature',
        'Grass Minimum Temperature','Relative Humidity','Rainfall','Total rainfall since 1st January',
        'Against an average of',"King's Park",'Wong Chuk Hang','Ta Kwu Ling','Lau Fau Shan','Tai Po',
        'Sha Tin','Tuen Mun','Tseung Kwan O','Sai Kung','Cheung Chau','Chek Lap Kok','Tsing Yi',
        'Shek Kong','Tsuen Wan Ho Koon','Tsuen Wan Shing Mun Valley','Hong Kong Park','Shau Kei Wan',
        'Kowloon City','Happy Valley','Wong Tai Sin','Stanley','Kwng Tong','Sham Shui Po','Kai Tak Runway Park',
        'Yuen Long Park','Duration of sunshine','mean UV','maximum UV index','Sea surface temperature','ranged from',
        'Ping Chau','Tap Mun','Kat O','Yuen Ng Fan','Tai Mei Tuk','Sha Tau Kok','Sai Wan Ho','Tsim Bei Tsui',"Cape D'Aguilar"]:
        if s in line:
          if s == 'Daily Weather Summary':
            l = [e for e in re.findall('[\d.]*\d+',line)]
            dt = ' '.join([l[1], l[0], l[2]])
            d['Date'] = parser.parse(dt).date()
          elif s == 'Relative Humidity':
            if re.search('(T|t)race', line) is not None:
              d['MinRelHumidity'] = 'Trace'
              d['MaxRelHumidity'] = 'Trace'
            else:
              l = [e for e in re.findall('[\d.]*\d+',line)]
              d['MinRelHumidity'] = l[0]
              d['MaxRelHumidity'] = l[1]
          elif s in ['Maximum Air Temperature','Minimum Air Temperature','Grass Minimum Temperature','Rainfall',
                      'Total rainfall since 1st January','Against an average of','Duration of sunshine',
                      'mean UV','maximum UV index','Sea surface temperature']:
            if re.search('(T|t)race', line) is not None:
              d[s] = 'Trace'
            else:
              for e in re.findall('[\d.]*\d+',line):
                d[s] = e
          elif s == 'ranged from':
            l = [e for e in re.findall('[\d.]*\d+',line)]
            d['MinAmbGammaRad'] = l[0]
            d['MaxAmbGammaRad'] = l[1]
          elif s in ['Ping Chau','Tap Mun','Kat O','Yuen Ng Fan','Tai Mei Tuk','Sha Tau Kok','Kwun Tong','Sai Wan Ho',
                        "King's Park",'Tsim Bei Tsui',"Cape D'Aguilar",'Chek Lap Kok']:
            if(s not in ['Kwun Tong',"King's Park",'Chek Lap Kok']):
              for e in re.findall('[\d.]*\d+',line):
                d['AmbGammaRadof ' + s] = e
            else:
              if(s != "King's Park"):
                for e in re.findall('[\d.]*\d+',line):
                  l.append(e)
                  if(len(l)<=1):
                    d['AmbGammaRadof ' + s] = l[0]
              else:
                if('Duration of sunshine' not in line):
                  for e in re.findall('[\d.]*\d+',line):
                    d['AmbGammaRadof ' + s] = e		
          else:
            for e in re.findall('[\d.]*\d+',line):
              l.append(e)
            if(len(l) >= 2):
              d[s + ' MinTemp'] = l[0]
              d[s + ' MaxTemp'] = l[1]

    df = pd.DataFrame(list(d.items()))
    df = df.set_index(df.iloc[:,0]).drop(0,1)
    return df
    
def main():
  print(wrapweather())
  print(wrapweather(date=datetime(2016,2,3)))
  print(wrapweather(start=datetime(2016,2,3), end=datetime(2016,2,6)))
  
if __name__ == '__main__':
  main()
