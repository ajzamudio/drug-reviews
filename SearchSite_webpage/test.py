from SearchSite_webpage.tasks import add

c = add.delay(2,5)
print("hi" + c)