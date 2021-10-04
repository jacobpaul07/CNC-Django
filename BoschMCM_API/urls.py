"""
BoschMCM_API URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from Webapp import views
from App import views as AppViews
from django.conf.urls import url

urlpatterns = [

    path('admin/', admin.site.urls),
    # Read Edge Device Settings
    path('api/ReadDeviceSettings', views.ReadDeviceSettings().as_view()),
    # # OPC-UA
    path('api/startopc', views.StartOpcService().as_view()),
    path('api/stopopc', views.StopOpcService().as_view()),

    # Change Edge Device Settings
    # path('api/changeedgedeviceproperties', views.ConfigGatewayProperties().as_view()),
    # # Change DataCenter Properties
    # path('api/changeDataCenterProperties', views.ConfigDataCenterProperties().as_view()),
    # path('api/changeDataCenterDeviceProperties', views.ConfigDataCenterDeviceProperties().as_view()),
    # path('api/changeDataCenterDeviceIOTags', views.ConfigDataCenterDeviceIOTags.as_view()),
    # # Change DataService Properties
    # path('api/changeDataServiceProperties', views.ConfigDataServiceProperties.as_view()),
    # path('api/changePpmpStations', views.ConfigPpmpStations.as_view()),
    # # TCP
    # path('api/starttcp', views.StartTcpService().as_view()),
    # path('api/stoptcp', views.StopTcpService().as_view()),
    # # RTU
    # path('api/startrtu', views.StartRtuService().as_view()),
    # path('api/stoprtu', views.StopRtuService().as_view()),
    # # PPMP
    # path('api/startppmp', views.StartPpmpService().as_view()),
    # path('api/stopppmp', views.StopPpmpService().as_view()),
    # # path('api/doLogin', LoginView.LoginViewAPI.as_view())
    # path('api/changetcpip', views.ConfigIpChange().as_view()),
    #
    path('api/startWebSocket', views.startWebSocket().as_view()),
    path('api/stopWebSocket', views.stopWebSocket().as_view()),
    path('socket', AppViews.index, name='index')
]
