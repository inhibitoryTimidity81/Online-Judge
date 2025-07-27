from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest
from submit.forms import CodeSubmissionForm
from django.conf import settings
from submit.models import Problem, TestCase, TestResult, CodeSubmission
import os
import uuid
import subprocess
from pathlib import Path
import platform
import time
from django.contrib.auth.decorators import login_required


# Create your views here.

def problem_list(request):
    problems = Problem.objects.all().order_by('-created_at')
    return render(request, 'problem_list.html', {'problems': problems})


def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    return render(request, 'problem_detail.html', {'problem': problem})


def submit_solution(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    if request.method == 'POST':
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.problem = problem
            submission.save()

            # Judge the submission
            judge_submission(submission)
            return redirect('submission_result', submission_id=submission.id)
    else:
        form = CodeSubmissionForm()
    
    return render(request, 'submit_solution.html', {
        'form': form, 
        'problem': problem
    })


def judge_submission(submission):
    """Main judging function"""
    test_cases = submission.problem.test_cases.all()
    total_tests = len(test_cases)
    passed_tests = 0
    max_time = 0

    submission.total_tests = total_tests

    for test_case in test_cases:
        result = run_single_test(submission, test_case)

        TestResult.objects.create(
            submission=submission,
            test_case=test_case,
            user_output=result['output'],
            verdict=result['verdict'],
            execution_time=result['time'],
        )

        if result['verdict'] == 'AC':
            passed_tests += 1
        elif result['verdict'] in ['TLE', 'RTE', 'CE']:
            break

        max_time = max(max_time, result.get('time', 0))
    
    # Determine overall verdict
    if passed_tests == total_tests:
        submission.verdict = 'AC'
    elif any(tr.verdict == 'CE' for tr in submission.test_results.all()):
        submission.verdict = 'CE'
    elif any(tr.verdict == 'TLE' for tr in submission.test_results.all()):
        submission.verdict = 'TLE'
    elif any(tr.verdict == 'RTE' for tr in submission.test_results.all()):
        submission.verdict = 'RTE'
    else:
        submission.verdict = 'WA'
    
    submission.passed_tests = passed_tests
    submission.execution_time = max_time
    submission.save()


def run_single_test(submission, test_case):
    """Run code against a single test case"""
    try:
        start_time = time.time()
        output = run_code(
            submission.language, 
            submission.code, 
            test_case.input_data, 
            submission.problem.time_limit
        )
        end_time = time.time()
        execution_time = int((end_time - start_time) * 1000)  # Convert to ms

        # Check for compilation/runtime errors
        if output.startswith('Error'):
            return {
                'output': output, 
                'verdict': 'CE',
                'time': 0, 
                'memory': 0,
            }
        
        # Compare output
        user_output = output.strip()
        expected_output = test_case.expected_output.strip()

        if user_output == expected_output:
            verdict = 'AC'
        else:
            verdict = 'WA'
            
        return {
            'output': output, 
            'verdict': verdict, 
            'time': execution_time, 
            'memory': 0
        }
        
    except subprocess.TimeoutExpired:
        return {
            'output': '', 
            'verdict': 'TLE',
            'time': submission.problem.time_limit,
            'memory': 0
        }
    except Exception as e:
        return {
            'output': str(e), 
            'verdict': 'RTE',
            'time': 0, 
            'memory': 0,
        }


def run_code(language, code, input_data, time_limit_ms):
    """Execute code with given input and time limit"""
    
    # Handle empty input
    if input_data is None:
        input_data = ""

    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]

    # Create necessary directories
    for directory in directories:
        dir_path = project_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    outputs_dir = project_path / "outputs"

    # Generate unique file names
    unique = str(uuid.uuid4())
    code_file_name = f"{unique}.{language}"
    input_file_name = f"{unique}.txt"
    output_file_name = f"{unique}.txt"

    code_file_path = codes_dir / code_file_name
    input_file_path = inputs_dir / input_file_name
    output_file_path = outputs_dir / output_file_name

    # Write code to file
    with open(code_file_path, "w") as code_file:
        code_file.write(code)
    
    # Write input to file
    with open(input_file_path, "w", newline='') as input_file:
        if input_data:
            # Ensure consistent line endings and proper formatting
            clean_input = input_data.replace('\r\n', '\n').replace('\r', '\n')
            input_file.write(clean_input)
            if not clean_input.endswith('\n'):
                input_file.write('\n')

    timeout_seconds = time_limit_ms / 1000.0

    try:
        if language == "cpp":
            if platform.system() == "Windows":
                executable_name = f"{unique}.exe"
                compiler = "g++"
            else:
                executable_name = unique
                compiler = "clang++"

            executable_path = codes_dir / executable_name

            # Compile the code
            compile_result = subprocess.run(
                [compiler, str(code_file_path), "-o", str(executable_path)], 
                capture_output=True, 
                text=True, 
                timeout=30
            )

            if compile_result.returncode != 0:
                return f"Error: {compile_result.stderr}"
            
            # Execute the compiled program
            with open(input_file_path, "r") as input_file:
                result = subprocess.run(
                    [str(executable_path)], 
                    stdin=input_file,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True, 
                    timeout=timeout_seconds
                )
                
                if result.returncode == 0:
                    return result.stdout
                else:
                    return f"Error: {result.stderr}"

        elif language == "py":
            interpreter = "python" if platform.system() == "Windows" else "python3"

            with open(input_file_path, "r") as input_file:
                result = subprocess.run(
                    [interpreter, str(code_file_path)], 
                    stdin=input_file,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    timeout=timeout_seconds
                )
                
                if result.returncode == 0:
                    return result.stdout
                else:
                    return f"Error: {result.stderr}"
        
        elif language == "c":
            if platform.system() == "Windows":
                executable_name = f"{unique}.exe"
                compiler = "gcc"
            else:
                executable_name = unique
                compiler = "clang"

            executable_path = codes_dir / executable_name

            # Compile the code
            compile_result = subprocess.run(
                [compiler, str(code_file_path), "-o", str(executable_path)], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if compile_result.returncode != 0:
                return f"Error: {compile_result.stderr}"
            
            # Execute the compiled program
            with open(input_file_path, "r") as input_file:
                result = subprocess.run(
                    [str(executable_path)], 
                    stdin=input_file, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    timeout=timeout_seconds
                )
                
                if result.returncode == 0:
                    return result.stdout
                else:
                    return f"Error: {result.stderr}"
                    
    except subprocess.TimeoutExpired:
        raise
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Clean up temporary files
        for file_path in [code_file_path, input_file_path, output_file_path]:
            try:
                if file_path.exists():
                    file_path.unlink()
            except:
                pass

        # Clean up executable for compiled languages
        if language in ["cpp", "c"]:
            try:
                executable_path = codes_dir / (unique + (".exe" if platform.system() == "Windows" else ""))
                if executable_path.exists():
                    executable_path.unlink()
            except:
                pass


def submission_result(request, submission_id):
    """Display submission results"""
    submission = get_object_or_404(CodeSubmission, id=submission_id)
    test_results = submission.test_results.all().order_by('id')
    return render(request, 'submission_result.html', {
        'submission': submission,
        'test_results': test_results  
    })