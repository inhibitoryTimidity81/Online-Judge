from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Problem(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField()
    input_format=models.TextField()
    output_format=models.TextField()
    constraints=models.TextField()
    sample_input=models.TextField()
    sample_output=models.TextField()
    time_limit=models.IntegerField(default=1000)
    memory_limit=models.IntegerField(default=256)
    difficulty=models.CharField(max_length=20, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='easy')
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class TestCase(models.Model):
    problem=models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases')
    input_data=models.TextField()
    expected_output=models.TextField()
    is_sample=models.BooleanField(default=False)

    def __str__(self):
        return f"Test case for {self.problem.title}"


#Creating a database table.
class CodeSubmission(models.Model):

    VERDICT_CHOICES=[('AC', 'Accepted'), ('WA', 'Wrong Answer'), 
                     ('TLE','Time Limit Exceeded'), ('RTE','Runtime Error'),
                     ('CE', 'Compilation Error'), ('MLE', 'Memory Limit Exceeded')
                     , ('PENDING', 'Pending')]
    
    user=models.ForeignKey(User, on_delete=models.CASCADE,
                           null=True, blank=True)
    problem=models.ForeignKey(Problem, on_delete=models.CASCADE, 
                              null=True, blank=True)
    
    language=models.CharField(max_length=100)
    code=models.TextField()
    # input_data=models.TextField(null=True, blank=True)        #input can be empty also.
    verdict=models.CharField(max_length=10, choices=VERDICT_CHOICES, default='PENDING')
    execution_time=models.IntegerField(null=True, blank=True)
    memory_used=models.IntegerField(null=True, blank=True)
    passed_tests=models.IntegerField(default=0)
    total_tests=models.IntegerField(default=0)
    # output_data=models.TextField(null=True, blank=True)       #Storing outputs for comparing with the expected output later on.
    timestamp=models.DateTimeField(auto_now_add=True)         #To store the original submission Date and time.

class TestResult(models.Model):
    submission=models.ForeignKey(CodeSubmission, on_delete=models.CASCADE,
                                    related_name='test_results')
    test_case=models.ForeignKey(TestCase, on_delete=models.CASCADE)
    user_output=models.TextField()
    verdict=models.CharField(max_length=10, choices=CodeSubmission.VERDICT_CHOICES)
    execution_time=models.IntegerField(null=True, blank=True)
    memory_used=models.IntegerField(null=True, blank=True)
    
        