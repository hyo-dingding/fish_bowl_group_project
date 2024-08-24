from django.urls import path
from accountapp.views import hello_world

app_name = "accountapp" 
# http://127.0.0.1:8000/account/hello_world/ 이것을 
# accountapp:hello_world 이렇게 routing 하기 위함으로 써줌

urlpatterns = [
    path("hello_world/", hello_world, name="hello_world" )  # path, view, route의 name
]
