from tools.weather import get_weather


result = get_weather.invoke({
    "city": "Goa"
})

print(result)