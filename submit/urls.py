# from django.urls import path
# from submit.views import problem_list, problem_detail, submit_solution, submission_result


# urlpatterns=[
#     path("", problem_list, name="problem_list"),
#     path("problem/<int:problem_id>/", problem_detail, name="problem_detail"),
#     path("problem/<int:problem_id>/submit/", submit_solution, name="submit_solution"),
#     path("submission/<int:submission_id>/", submission_result, name="submission_result"),
# ]


from django.urls import path
from submit.views import (
    problem_list, problem_detail, submit_solution, submission_result
)

urlpatterns = [
    path("", problem_list, name="problem_list"),
    path("problem/<int:problem_id>/", problem_detail, name="problem_detail"),
    path("problem/<int:problem_id>/submit/", submit_solution, name="submit_solution"),
    path("submission/<int:submission_id>/", submission_result, name="submission_result"),
    
]


