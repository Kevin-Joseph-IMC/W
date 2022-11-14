# REST API CMDs

## Newton
- https://github.com/aunyks/newton-api


py .\RestClient.py -r .\Newton.config -c https://newton.now.sh/api/v2/derive/x%5E2

py .\RestClient.py -r .\Newton.config -c /api/v2/simplify/2%5E2+2 -s https://newton.vercel.app -q result=8 

py .\RestClient.py -r .\Newton.config -c https://newton.now.sh/api/v2/derive/x%5E2 -q operation="derive"

py .\RestClient.py -r .\Newton.config -c https://newton.vercel.app/api/v2/simplify/2%5E2+2 -q result=8


## GoRest
- https://gorest.co.in/



py .\RestClient.py -r .\GoRest.config -c https://gorest.co.in/public/v2/users -m GET

py .\RestClient.py -r .\GoRest.config -c https://gorest.co.in/public/v2/posts -m GET
