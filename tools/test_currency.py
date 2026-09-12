from tools.currency import convert_currency


result = convert_currency.invoke({
    "amount": 30000,
    "from_currency": "INR",
    "to_currency": "USD"
})

print(result)