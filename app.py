import pandas as pd
from flask import Flask, jsonify, request, Response
import json
import redis
import bcrypt
import jwt
from datetime import datetime, time, timedelta
from google.cloud import bigquery
from flask_restful import Resource, Api
from apispec import APISpec
from flask_cors import CORS, cross_origin
from marshmallow import Schema, fields
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from apscheduler.schedulers.background import BackgroundScheduler
from schema import bigQueryGetResponseSchema,bigQueryRequestSchema,bigQueryResponseSchema
app = Flask(__name__)  # Flask app instance initiated
CORS(app, support_credentials=True)
api = Api(app)  # Flask restful wraps Flask app around it.
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='bigQuery Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

app.config.update({
    'HOST_INFO':"redis-17100.c100.us-east-1-4.ec2.cloud.redislabs.com",
    "REDIS_PORT":17100,
    'REDIS_PASSWORD':"l7cCnqir0PYZzEEsMDNLoVo6UVIKMtlL",
    "PRIVATE_KEY":"Ravindra"
})


##client= bigquery.Client.from_service_account_json("./clouddemo-service-account.json")
def updateRedis():
    print("sync data begins")
    """
    redisObj = redis.Redis(host=app.config["HOST_INFO"],port=app.config["REDIS_PORT"], password=app.config["REDIS_PASSWORD"])
    for j in range(redisObj.llen("keys")):
        id=redisObj.rpop("keys").decode('utf8')
        sqlQuery=
        SELECT * FROM `coral-gate-326913.testing_api.test` WHERE id=@id
       
        sqlConfig=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("id","INT64",id),
            ]
        )
        data=client.query(sqlQuery,sqlConfig)
        redisObj.lpush("keys",id)
        jsonData=json.dumps( [dict(i) for i in data]) 
        redisObj.set(id, {'data': jsonData})
    """
    print("sync data is done")

sched = BackgroundScheduler(daemon=True)
#morning 8 am
sched.add_job(
    updateRedis, 
    trigger='cron',
    hour='*/8',
)
sched.start()

#  Restful way of creating APIs through Flask Restful
class bigQueryAPI(MethodResource, Resource):
    @doc(description='My First GET bigQuery API.', tags=['bigQuery'])
    @marshal_with(bigQueryResponseSchema)  #marshalling
    def get(self):
        '''
        Get method represents a GET API method
        '''
        return {'message': 'My First bigQuery API'}

    @doc(description='My First GET bigQuery API.', tags=['bigQuery'])
    @use_kwargs(bigQueryRequestSchema, location=('json'))
    @marshal_with(bigQueryResponseSchema)  # marshalling
    def post(self, **kwargs):
        id=request.form.get('id')
        token=None
        if "Bearer" in request.headers['Authorization']:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return Response(json.dumps({"err": "Token is missing"}), mimetype="application/json")
        tokenDecoded = jwt.decode(token,app.config["PRIVATE_KEY"],algorithms=['HS256'])
        #try:
        #connecting to redis
        redisObj = redis.Redis(host=app.config["HOST_INFO"],port=app.config["REDIS_PORT"], password=app.config["REDIS_PASSWORD"])
        #check whether the data with id exists in redis
        if(tokenDecoded["email"]!=redisObj.get("email").decode('utf8')):
            return Response(json.dumps({"err": "Not authorized user"}), mimetype="application/json")
        data = redisObj.get(id)
        print(data)
        if(data):
            return Response(data.decode("utf8"), mimetype="application/json")
        #get data from bigquery
        #sqlQuery="""
        #SELECT * FROM `coral-gate-326913.testing_api.test` WHERE id=@id
        #"""
        #sqlConfig=bigquery.QueryJobConfig(
        #    query_parameters=[
        #        bigquery.ScalarQueryParameter("id","INT64",id),
        #    ]
        #)
        #data=client.query(sqlQuery,sqlConfig)
        
        if(redisObj.llen("keys")==10):
            delKey=redisObj.rpop("keys").decode('utf8')
            redisObj.delete(delKey)
        df=pd.read_csv("./test_data.csv")
        df=df[df['no']==int(id)]
        jsonData = df.to_json(orient ='index')
        redisObj.lpush("keys",id)
        redisObj.set(id, jsonData)
        redisObj.delete(id)
        redisObj.delete("keys")
        return Response(jsonData, mimetype="application/json")
  
        #except Exception as e:
        #    return Response(json.dumps({"err": "Error while querying the data"}), mimetype="application/json")

api.add_resource(bigQueryAPI, '/bigquery')
docs.register(bigQueryAPI)

@app.route('/login',methods = ['POST'])
def login():
    email=request.form.get('email')
    password=request.form.get('password')
    redisObj = redis.Redis(host=app.config["HOST_INFO"],port=app.config["REDIS_PORT"], password=app.config["REDIS_PASSWORD"])
    userBytes = password.encode('utf-8')
    check = userBytes==redisObj.get("password")
    now = datetime.utcnow()
    end_of_day = datetime.combine(now.date() + timedelta(days=1), time.min)
    if(email==redisObj.get('email').decode('utf8') and check):
        token = jwt.encode({
            'email': email,
            'exp' : int(end_of_day.timestamp())},app.config["PRIVATE_KEY"])
        return {"token":token}
    else:
        return Response(json.dumps({"err": "Incorrect email or password"}), mimetype="application/json")


@app.route('/', methods = ['GET'])
def post():
    #redisObj = redis.Redis(host=app.config["HOST_INFO"],port=app.config["REDIS_PORT"], password=app.config["REDIS_PASSWORD"])
    #redisObj.set('email',"ravindrareddy1217@gmail.com")
    #pass_="Password"
    #redisObj.set('password',pass_.encode('utf-8'))
    #print(redisObj.get('password'))
    return {'message': "welcome to home page"}

if __name__ == '__main__':
    app.run(debug=True)
