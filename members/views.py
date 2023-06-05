from django.http import HttpResponse
from django.template import loader
from .models import Member
import requests
from django.shortcuts import render
import pandas as pd

#Lấy ip public
ip = requests.get('https://api.ipify.org').text

#API lấy data thời tiết
GetLocal = "https://weatherapi-com.p.rapidapi.com/ip.json"
GetMappoint = "https://weatherapi-com.p.rapidapi.com/astronomy.json"
GetWeather = "https://weatherapi-com.p.rapidapi.com/current.json"
GetForecast = "https://weatherapi-com.p.rapidapi.com/forecast.json"

# Query của api
querystring = {"q":ip}

# Key sử dụng api
headers = {
        "X-RapidAPI-Key": "5761b749b1msh63b3d30b91858ddp173a64jsna65a320effd1",
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
        }

#Lấy data vị trí từ ip public
locals = requests.get(GetLocal, headers=headers, params=querystring)

querystringMappoint = {"q":locals.json()['city']}

#Lấy vị trí cụ thể trên map
Mappoint = requests.get(GetMappoint, headers=headers, params=querystring)

Stringmappoint = str(Mappoint.json()['location']['lat']) +',' +str(Mappoint.json()['location']['lon'])

querystringWeather = {"q": Stringmappoint}

#Lấy data thời tiết trong thời gian thực
Weather = requests.get(GetWeather, headers=headers, params=querystringWeather)

#Lấy data thời gian
date=pd.Timestamp(Weather.json()['location']['localtime'])

querystringForecast = {"q":locals.json()['city'],"days":"3"}

#Lấy data dự báo thời tiết
Forecast = requests.get(GetForecast, headers=headers, params=querystringForecast)

#Hiển thị thời tiết trang chủ, auto chọn vị trí từ IP
def weather(request):  
    info = {
            'forecastday' : [],
            'avgtemp_c' : [],
            'maxwind_kph' :[],
            'date' :[],
           }

    #Tại api xài free nên chỉ có cho xem dự báo thời tiết trong 3 ngày :'(
    for i in range(3):
            info['forecastday'].append(Forecast.json()['forecast']['forecastday'][i]['day']['condition']['icon']) 
            info['avgtemp_c'].append(Forecast.json()['forecast']['forecastday'][i]['day']['avgtemp_c'])
            info['maxwind_kph'].append(Forecast.json()['forecast']['forecastday'][i]['day']['maxwind_kph'])
            info['date'].append(pd.Timestamp(Forecast.json()['forecast']['forecastday'][i]['date']).day_name())
    
    return render(request,'template.html',{'city':locals.json()['city'],
                  'temp_c':int(Weather.json()['current']['temp_c']),
                  'humidity':int(Weather.json()['current']['humidity']),
                  'wind_kph':int(Weather.json()['current']['wind_kph']),
                  'icon':Weather.json()['current']['condition']['icon'],
                  'time':date.time(),
                  'date':date.day_name(),'month':date.month_name(),'datenumber':date.strftime("%d"),
                  'info':info,'n':range(3)})

# Dự báo thời tiết trong 24 giờ của ngày cụ thể nào đó
def weather24(request):
    weather24 ={
            'date':[],
            'time':[],
            'temp_c':[],
            'icon' :[],
            'wind_kph':[],
            'chance_of_rain':[],
            'humidity':[]
        }
    for i in range(3):
            #Lưu data trong 24 giờ vào direction
            for x in range(24):
                weather24['date'].append(pd.Timestamp(Forecast.json()['forecast']['forecastday'][i]['hour'][x]['time']).day_name())
                weather24['time'].append(pd.Timestamp(Forecast.json()['forecast']['forecastday'][i]['hour'][x]['time']).time())
                weather24['temp_c'].append(Forecast.json()['forecast']['forecastday'][i]['hour'][x]['temp_c'])
                weather24['icon'].append(Forecast.json()['forecast']['forecastday'][i]['hour'][x]['condition']['icon'])
                weather24['wind_kph'].append(Forecast.json()['forecast']['forecastday'][i]['hour'][x]['wind_kph'])
                weather24['chance_of_rain'].append(Forecast.json()['forecast']['forecastday'][i]['hour'][x]['chance_of_rain'])
                weather24['humidity'].append(Forecast.json()['forecast']['forecastday'][i]['hour'][x]['humidity'])

    return render(request,'weather24.html',{'weather24':weather24,
                                            'n':range(12)})

# Tìm theo tên thành phố
def search(request):
    #Lấy data từ form input của HTML
    city = request.POST['city']
    querystringForecast1 = {"q":city,"days":"3"}

    #Lấy data dự báo thời tiết dựa theo tên thành phố lấy từ form
    ForecastSearch = requests.get(GetForecast, headers=headers, params=querystringForecast1)
    
    info = {
            'forecastday' : [],
            'avgtemp_c' : [],
            'maxwind_kph' :[],
            'date' :[],
           }

    for i in range(3):
            info['forecastday'].append(ForecastSearch.json()['forecast']['forecastday'][i]['day']['condition']['icon']) 
            info['avgtemp_c'].append(ForecastSearch.json()['forecast']['forecastday'][i]['day']['avgtemp_c'])
            info['maxwind_kph'].append(ForecastSearch.json()['forecast']['forecastday'][i]['day']['maxwind_kph'])
            info['date'].append(pd.Timestamp(ForecastSearch.json()['forecast']['forecastday'][i]['date']).day_name())
            
    return render(request, 'search.html',{'info':info,'n':range(3),'city':ForecastSearch.json()['location']['name'],
                                        'temp_c':int(ForecastSearch.json()['current']['temp_c']),
                                        'humidity':int(ForecastSearch.json()['current']['humidity']),
                                        'wind_kph':int(ForecastSearch.json()['current']['wind_kph']),
                                        'date':pd.Timestamp(ForecastSearch.json()['location']['localtime']).day_name(),
                                        'time':pd.Timestamp(ForecastSearch.json()['location']['localtime']).time(),
                                        'month':pd.Timestamp(ForecastSearch.json()['location']['localtime']).month_name(),
                                        'datenumber':pd.Timestamp(ForecastSearch.json()['location']['localtime']).strftime("%d")})

