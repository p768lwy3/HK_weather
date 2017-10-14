# Weather
Using python to wrapping weather data from the websites

- Modules
  - PyWeatherHK: Wraping weahter of Hong Kong.
    - Function
      - wrapweather </br>
        Input: </br>
        date: use for wrapping with single date, datetime type variable, default as datetime.now()-timedelta(days=1) </br>
        start: use for wrapping with a range with from start to end, datetime type variable </br>
        end: use for wrapping with a range with from start to end, datetime type variable </br>
        
        return: </br>
        
        --------------------------------------
        |0      |MinTemp|MaxTemp|RainFall|...|
        |-------|-------|-------|--------|---|
        |Date   |       |       |        |   |
        |2016-02-03|1x.x| 1x.x  | 2xx.x  |   |
        
