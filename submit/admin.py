from django.contrib import admin
from submit.models import Problem, TestCase, CodeSubmission, TestResult

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'time_limit', 'memory_limit', 'created_at']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['title']

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['problem', 'is_sample']
    list_filter = ['problem', 'is_sample']

@admin.register(CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'problem', 'language', 'verdict', 'passed_tests', 'total_tests', 'timestamp']
    list_filter = ['verdict', 'language', 'timestamp']
    search_fields = ['user__username', 'problem__title']

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['submission', 'test_case', 'verdict', 'execution_time']
    list_filter = ['verdict']
