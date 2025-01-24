"""
URL configuration for ascencia_interviews project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from adminpanel.views.auth_view import login_view, register_view, logout_view, index
from adminpanel.views.dashboard_view import admindashboard
from adminpanel.views.institute_view import institute_list, institute_add, institute_update, institute_delete
from adminpanel.views.course_view import courses, course_add, course_update, course_delete
from adminpanel.views.question_view import questions, question_add, question_update, question_delete, common_questions, common_question_add, common_question_update, common_question_delete

urlpatterns = [
    path('index/', index),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    path('adminpanel/', include([
        # institute
        path('institute/', institute_list, name='institute_list'),
        path('institute/add', institute_add, name='institute_add'),
        path('institute/update/<id>/', institute_update, name='institute_update'),
        path('institute/delete/<id>/', institute_delete, name='institute_delete'),

        # courses
        path('courses/', courses, name='courses'),
        path('course/add', course_add, name='course_add'),
        path('course/update/<id>/', course_update, name='course_update'),
        path('course/delete/<id>/', course_delete, name='course_delete'),
        
        # common questions
        path('common_questions/', common_questions, name='common_questions'),
        path('common_question/add', common_question_add, name='common_question_add'),
        path('common_question/update/<id>/', common_question_update, name='common_question_update'),
        path('common_question/delete/<id>/', common_question_delete, name='common_question_delete'),

        # questions
        path('questions/', questions, name='questions'),
        path('question/add', question_add, name='question_add'),
        path('question/update/<id>/', question_update, name='question_update'),
        path('question/delete/<id>/', question_delete, name='question_delete'),
        
        # Dashboards
        # path('dashboard/',userdashboard),
        path('dashboard/', admindashboard, name='admindashboard')
    ])),
    
]
