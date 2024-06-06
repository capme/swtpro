# sawitPRO #

Before you run alpha and beta app, please install docker and docker-compose.

### How to run the web app? ###

* Clone this repository
* Run `sudo docker-compose build`
* Run `sudo docker-compose up -d`
* Run `sudo docker-compose exec app bash`
* Wait aproximately 30 seconds to make sure all the services is up
* Inside bash shell of the app, run:

  ```
  /app# flask db upgrade
  /app# exit
  ```
  
Note: <br>
a. Access the web app -> http://127.0.0.1:10000/.<br>
b. It need port 3306 for MySQL DB, 10000 for the web app. Please free-up those ports on your machine.
