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


class LoginViewAPI(APIView):
    def post(self, request):
        success: bool = True
        filePath = './Json_Class/JSONCONFIG1.json'

        print(request.data)
        json_string: str = ""
        with open(filePath) as f:
            json_string = json.load(f)
            f.close()
        pwd: str = json_string["edge device"]["properties"]["Password"]

        if pwd == str(request.data):
            success = True
        # else:
        #     success = False

        print(success)
        return HttpResponse({success: success}, content_type="application/json")
