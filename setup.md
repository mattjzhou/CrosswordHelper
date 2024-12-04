az login
az webapp up --runtime PYTHON:3.9 --sku P0v3 --logs
autoscale:
    azure portal -> monitor -> settings -> autoscale -> click service plan
    custom autoscale -> scale based on metric -> add scale out (default) and scale in rules -> increase maximum to 3 -> save
jmeter:
    terminal -> jmeter
    open "Test Plan.jmx" -> edit number of threads in thread group -> edit url in http requests defaults
metrics:
    azure portal -> app services -> click app -> monitoring -> metrics -> cpu time, sum
    or go to autoscale and click run history
az group delete -n <name> -y


map:
azure portal -> create new resource group -> go to azure maps in azure portal -> create new azure maps account resource
get subscription key and paste in html file locally
open html file in browser
change center = [-74.0060, 40.7128]
search for restaurants (fictitious)