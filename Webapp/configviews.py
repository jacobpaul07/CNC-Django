from django.shortcuts import render
from typing import List
import json

# Create your views here.

from django.http import HttpResponse
from django.shortcuts import get_list_or_404
from rest_framework import response
from rest_framework.decorators import api_view
from rest_framework.relations import ManyRelatedField
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from django.http import JsonResponse


class ConfigViewAPI(APIView):

    def get(self, request):
        filePath = './Json_Class/JSONCONFIG1.json'
        with open(filePath) as f:
            json_string = json.load(f)
            print("Equipment data has been successfully retrieved.")
            json_return = json.dumps(json_string)
            f.close()
        return HttpResponse(json_return, content_type="application/json")

    def post(self, request):
        json_string: str = ""
        filePath = './Json_Class/JSONCONFIG1.json'
        with open(filePath) as f:
            json_string = json.load(f)
            # json_string2 = json.load(f)
            f.close()

        postData = request.body.decode('utf8')  # .replace("'", '"')
        postDataJson = json.loads(postData)

        # print(postDataJson)
        # print(my_json)
        # for v in json_string.keys():
        #     print(v)

        json_string["edge device"]["properties"]["IP Address"] = postDataJson["IP Address"]

        # json_string2["edge device"]["properties"]["Mode1"] = postDataJson["Mode1"]

        # postData.update(json_string["edge device"]["properties"]["Name"] == postDataJson["Name"])

        # json_string["edge device"]["properties"] = postDataJson.update(postDataJson["Name"])

        # /**gopal bro
        # jsonsamplestring = json.dumps(json_string["edge device"]["properties"])

        # jsonsamplestring = json.dumps(postData)
        # json_dictionary = json.loads(jsonsamplestring)
        # jsondummy={}

        # for key in postDataJson:
        #     json_dict =  { key : postDataJson[key] }
        #     jsondummy.update(json_dict)
        # print(jsondummy)
        # print(json_dict)
        # /**gopal bro

        # json_string["edge device"]["properties"]["Password"] = postDataJson["Password"]

        # print(json_string["edge device"]["properties"]["Name"])Equipment data has been successfully retrieved.

        # if(json_string["edge device"]["properties"]["Name"]==False):
        #     json_string["edge device"]["properties"]["Name"] = postDataJson["Name"]
        # elif(json_string["edge device"]["properties"]["Mode1"]==True):
        #     json_string["edge device"]["properties"]["Mode1"] = postDataJson["Mode1"]

        # json_string["edge device"]["properties"]["Mode1"] = postDataJson["Mode1"]
        # for tc in json_string["edge device"]["properties"]:
        #     tc["edge device"]["properties"]["Name"] = postDataJson["Name"]
        #     tc["edge device"]["properties"]["Mode1"] = postDataJson["Mode1"]

        s = json.dumps(json_string)
        # print(s)

        with open(filePath, "w") as file:
            file.write(s)
        return HttpResponse({"status": "ok"}, content_type="application/json")
