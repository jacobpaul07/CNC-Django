from rest_framework import fields, serializers
from . models import employees

class employeesSeerializer(serializers.ModelSerializer):
     class Meta:
         model=employees
#         fields=('firstName','lastName')
         fields = '__all__'

