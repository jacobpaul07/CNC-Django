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
from App import views as app_views


urlpatterns = [

    path('admin/', admin.site.urls),

    # Read Edge Device Settings
    path('api/ReadDeviceSettings', views.ReadDeviceSettings().as_view()),

    # OPC-UA
    path('api/startopc', views.StartOpcService().as_view()),
    path('api/stopopc', views.StopOpcService().as_view()),

    # Change Edge Device Settings
    path('api/changeedgedeviceproperties', views.ConfigGatewayProperties().as_view()),
    path('api/changeDataService', views.ConfigDataServiceProperties.as_view()),

    # Websocket
    path('api/startWebSocket', views.StartWebSocket().as_view()),
    path('api/stopWebSocket', views.StopWebSocket().as_view()),
    path('socket', app_views.index, name='index'),

    # Initial Data/ Specific Time Data API
    path('api/getoeedata', views.GetOeeData().as_view()),

    # Downtime API
    path('api/getdowntimereason', productionViews.GetDownTimeReason().as_view()),
    path('api/getdowntimecategory', productionViews.GetDownTimeCategory().as_view()),
    path('api/getdowntimedata', productionViews.GetDownTimeData().as_view()),
    path('api/postdowntimedata', productionViews.PostDownTimeData().as_view()),

    # Quality API
    path('api/getqualitycategory', productionViews.GetQualityCategory().as_view()),
    path('api/getqualitydata', productionViews.GetQualityData().as_view()),
    path('api/getqualitycode', productionViews.GetQualityCode().as_view()),
    path('api/postqualitydata', productionViews.PostQualityData().as_view()),

    # Production API
    path('api/getproductiondata', productionViews.GetProductionData().as_view()),
    path('api/postproductiondata', productionViews.PostProductionData().as_view()),
    path('api/getTotalProductionCount', productionViews.GetTotalProductionCount().as_view()),

    # Report API
    path('api/report/production', reportViews.GetProductionReport().as_view()),
    path('api/report/oee', reportViews.GetOeeReport().as_view()),
    path('api/report/downtime', reportViews.GetDownTimeReport().as_view()),
    path('api/report/getmachineid', reportViews.GetMachineId().as_view()),

    # Web API
    path('web/api/dashboard', webViews.GetDashboardData().as_view()),
    path('web/api/devicesList', webViews.GetDevicesList().as_view()),

    # Login API
    path('web/api/login', apiloginviews.ObtainTokenPairView.as_view(), name='token_create'),
    path('web/api/refreshtoken', apiloginviews.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('web/api/createuser', apiloginviews.CustomUserCreate.as_view(), name='create_user'),
    path('web/api/logout', apiloginviews.LogoutAndBlacklistRefreshTokenForUserView.as_view(), name='blacklist')
]
