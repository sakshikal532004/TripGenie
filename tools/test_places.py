from tools.places import search_attractions


result = search_attractions.invoke({
    "destination": "Goa, India",
    "interest": "beaches"
})

print(result)