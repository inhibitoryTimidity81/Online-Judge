from django import forms
from submit.models import CodeSubmission,Problem

LANGUAGE_CHOICES=[("py", "Python"), ("c", "C"), ("cpp", "C++")]

class CodeSubmissionForm(forms.ModelForm):
    language=forms.ChoiceField(choices=LANGUAGE_CHOICES)

    class Meta:
        model=CodeSubmission                         #which model we will use to make the form.
        fields=['language', 'code']    #which fields will be displayed in the form.
    
class ProblemForm(forms.ModelForm):
    class Meta:
        model=Problem
        fields='__all__'