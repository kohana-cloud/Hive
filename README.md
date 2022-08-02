![HIVE](.rsrc/hive-banner.png)
# Hive
Hive is Kohana's dashboard and frontend for deploying decoys and managing attacks against a target network. Hive is written in Flask, Bootstrap and a majority of the javascript us purejs. The sryle sheets used in this project need quite a bit of work and the application, while supporting various security mechanisms is absolutely not ready for a production deployment.

## Deployment and Usage
Deploy Hive in development using the below flask command with precursor environment variables. Modify the port and host as required. You will also need to ensure that you have adaquet permissions to run the tool on a known-port if you choose to run it as follows.
```
FLASK_APP=hive.py FLASK_ENV=development flask run --port 80 --host=0.0.0.0
```

## Contribution Guidelines
Kohana is deprecated as this point, but if you would like to continue to develop and maintain this project please get in touch with Nate Singer using the email located at the main README.