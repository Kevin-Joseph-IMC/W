# REST API CMDs

## Newton
py .\RestClient.py -r .\Newton.config -c https://newton.now.sh/api/v2/derive/x%5E2

py .\RestClient.py -r .\Newton.config -c https://newton.now.sh/api/v2/derive/x%5E2 -q operation="derive"

py .\RestClient.py -r .\Newton.config -c https://newton.vercel.app/api/v2/simplify/2%5E2+2 -q result=8


## GoRest

py .\RestClient.py -r .\GoRest.config -c https://gorest.co.in/public/v2/users -m GET

py .\RestClient.py -r .\GoRest.config -c https://gorest.co.in/public/v2/posts -m GET
