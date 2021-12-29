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
Including another URL conf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from Webapp import views, productionViews, reportViews, webViews, apiloginviews
from App import views as AppViews


urlpatterns = [

    path('admin/', admin.site.urls),
    # Read Edge Device Settings
    path('api/ReadDeviceSettings', views.ReadDeviceSettings().as_view()),
    # path('api/ReadDbData', views.ReadSeriesData().as_view()),
    # OPC-UA
    path('api/startopc', views.StartOpcService().as_view()),
    path('api/stopopc', views.StopOpcService().as_view()),
    # Change Edge Device Settings
    path('api/changeedgedeviceproperties', views.ConfigGatewayProperties().as_view()),
    path('api/changeDataService', views.ConfigDataServiceProperties.as_view()),
    # Websocket
    path('api/startWebSocket', views.StartWebSocket().as_view()),
    path('api/stopWebSocket', views.StopWebSocket().as_view()),
    path('socket', AppViews.index, name='index'),

    # path('api/getoeedata', views.GetOeeData().as_view()),
    path('api/getoeedata', views.GetOeeData().as_view()),

    path('api/getdowntimereason', productionViews.getdowntimereason().as_view()),

    path('api/getdowntimecategory', productionViews.getdowntimecategory().as_view()),
    path('api/getdowntimedata', productionViews.getdowntimedata().as_view()),
    path('api/postdowntimedata', productionViews.postdowntimedata().as_view()),

    path('api/getqualitycategory', productionViews.getqualitycategory().as_view()),
    path('api/getqualitydata', productionViews.getqualitydata().as_view()),
    path('api/getqualitycode', productionViews.getqualitycode().as_view()),
    path('api/postqualitydata', productionViews.postqualitydata().as_view()),

    path('api/getproductiondata', productionViews.getproductiondata().as_view()),
    path('api/postproductiondata', productionViews.postproductiondata().as_view()),
    path('api/getTotalProductionCount', productionViews.getTotalProductionCount().as_view()),

    path('api/report/production', reportViews.getproductionreport().as_view()),
    path('api/report/oee', reportViews.getoeereport().as_view()),
    path('api/report/downtime', reportViews.getdowntimereport().as_view()),
    path('api/report/getmachineid', reportViews.getmachineid().as_view()),

    # Web API
    # path('web/api/login', webViews.postlogindata().as_view()),
    path('web/api/dashboard', webViews.getdashboarddata().as_view()),
    path('web/api/devicesList', webViews.getdevicesList().as_view()),

    # Login API
    path('web/api/login', apiloginviews.ObtainTokenPairView.as_view(), name='token_create'),
    path('web/api/refreshtoken', apiloginviews.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('web/api/createuser', apiloginviews.CustomUserCreate.as_view(), name='create_user'),
    path('web/api/logout', apiloginviews.LogoutAndBlacklistRefreshTokenForUserView.as_view(), name='blacklist')
]

# """
# BoschMCM_API URL Configuration
#
# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/3.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URL conf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
#
# from django.contrib import admin
# from django.urls import path
# from Webapp import views, productionViews, reportViews, webViews, apiloginviews
# from App import views as AppViews
# from Webapp.TestAsyncApi import TestClass
#
#
# urlpatterns = [
#
#     path('admin/', admin.site.urls),
#     # Read Edge Device Settings
#     path('api/ReadDeviceSettings', views.ReadDeviceSettings().as_view()),
#     # path('api/ReadDbData', views.ReadSeriesData().as_view()),
#     # OPC-UA
#     path('api/startopc', views.StartOpcService().as_view()),
#     path('api/stopopc', views.StopOpcService().as_view()),
#     # Change Edge Device Settings
#     path('api/changeedgedeviceproperties', views.ConfigGatewayProperties().as_view()),
#     path('api/changeDataService', views.ConfigDataServiceProperties.as_view()),
#     # Websocket
#     path('api/startWebSocket', views.StartWebSocket().as_view()),
#     path('api/stopWebSocket', views.StopWebSocket().as_view()),
#     path('socket', AppViews.index, name='index'),
#
#     # path('api/getoeedata', views.GetOeeData().as_view()),
#     path('api/getoeedata', views.GetOeeData().as_view()),
#
#     path('api/getdowntimereason', productionViews.getdowntimereason.get),
#
#     path('api/getdowntimecategory', productionViews.getdowntimecategory.get),
#     path('api/getdowntimedata', productionViews.getdowntimedata.get),
#     path('api/postdowntimedata', productionViews.postdowntimedata.post),
#
#     path('api/getqualitycategory', productionViews.getqualitycategory.get),
#     path('api/getqualitydata', productionViews.getqualitydata.get),
#     path('api/getqualitycode', productionViews.getqualitycode.get),
#     path('api/postqualitydata', productionViews.postqualitydata.post),
#
#     path('api/getproductiondata', productionViews.getproductiondata.get),
#     path('api/getTotalProductionCount', productionViews.getTotalProductionCount.get),
#     path('api/postproductiondata', productionViews.postproductiondata.post),
#
#     path('api/report/production', reportViews.getproductionreport().as_view()),
#     path('api/report/oee', reportViews.getoeereport().as_view()),
#     path('api/report/downtime', reportViews.getdowntimereport().as_view()),
#     path('api/report/getmachineid', reportViews.getmachineid().as_view()),
#
#     # Web API
#     # path('web/api/login', webViews.postlogindata().as_view()),
#     path('web/api/dashboard', webViews.getdashboarddata().as_view()),
#     path('web/api/devicesList', webViews.getdevicesList().as_view()),
#
#     # Login API
#     path('web/api/login', apiloginviews.ObtainTokenPairView.as_view(), name='token_create'),
#     path('web/api/refreshtoken', apiloginviews.CustomTokenRefreshView.as_view(), name='token_refresh'),
#     path('web/api/createuser', apiloginviews.CustomUserCreate.as_view(), name='create_user'),
#     path('web/api/logout', apiloginviews.LogoutAndBlacklistRefreshTokenForUserView.as_view(), name='blacklist'),
#
#     path('api/async', TestClass.getData)
#
# ]





