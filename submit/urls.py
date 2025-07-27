# from django.urls import path
# from submit.views import problem_list, problem_detail, submit_solution, submission_result


# urlpatterns=[
#     path("", problem_list, name="problem_list"),
#     path("problem/<int:problem_id>/", problem_detail, name="problem_detail"),
#     path("problem/<int:problem_id>/submit/", submit_solution, name="submit_solution"),
#     path("submission/<int:submission_id>/", submission_result, name="submission_result"),
# ]


# from django.urls import path
# from submit.views import (
#     problem_list, problem_detail, submit_solution, submission_result
# )

# urlpatterns = [
#     path("", problem_list, name="problem_list"),
#     path("problem/<int:problem_id>/", problem_detail, name="problem_detail"),
#     path("problem/<int:problem_id>/submit/", submit_solution, name="submit_solution"),
#     path("submission/<int:submission_id>/", submission_result, name="submission_result"),
    
# ]

from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.problem_list, name='problem_list'),
    path('problems/', views.problem_list, name='problem_list'),
    path('problems/problem/<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('problems/problem/<int:problem_id>/submit/', views.submit_solution, name='submit_solution'),
    path('submission/<int:submission_id>/', views.submission_result, name='submission_result'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
