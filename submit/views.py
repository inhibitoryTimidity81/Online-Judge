# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpRequest
# from submit.forms import CodeSubmissionForm
# from django.conf import settings
# from submit.models import Problem, TestCase, TestResult, CodeSubmission
# import os
# import uuid
# import subprocess
# from pathlib import Path
# import platform
# import time
# from django.contrib.auth.decorators import login_required


# # Create your views here.

# def problem_list(request):
#     problems = Problem.objects.all().order_by('-created_at')
#     return render(request, 'problem_list.html', {'problems': problems})


# def problem_detail(request, problem_id):
#     problem = get_object_or_404(Problem, id=problem_id)
#     return render(request, 'problem_detail.html', {'problem': problem})

# @login_required
# def submit_solution(request, problem_id):
#     problem = get_object_or_404(Problem, id=problem_id)

#     if request.method == 'POST':
#         form = CodeSubmissionForm(request.POST)
#         if form.is_valid():
#             submission = form.save(commit=False)
#             submission.user = request.user
#             submission.problem = problem
#             submission.save()

#             # Judge the submission
#             judge_submission(submission)
#             return redirect('submission_result', submission_id=submission.id)
#     else:
#         form = CodeSubmissionForm()
    
#     return render(request, 'submit_solution.html', {
#         'form': form, 
#         'problem': problem
#     })


# def judge_submission(submission):
#     """Main judging function"""
#     test_cases = submission.problem.test_cases.all()
#     total_tests = len(test_cases)
#     passed_tests = 0
#     max_time = 0

#     submission.total_tests = total_tests

#     for test_case in test_cases:
#         result = run_single_test(submission, test_case)

#         TestResult.objects.create(
#             submission=submission,
#             test_case=test_case,
#             user_output=result['output'],
#             verdict=result['verdict'],
#             execution_time=result['time'],
#         )

#         if result['verdict'] == 'AC':
#             passed_tests += 1
#         elif result['verdict'] in ['TLE', 'RTE', 'CE']:
#             break

#         max_time = max(max_time, result.get('time', 0))
    
#     # Determine overall verdict
#     if passed_tests == total_tests:
#         submission.verdict = 'AC'
#     elif any(tr.verdict == 'CE' for tr in submission.test_results.all()):
#         submission.verdict = 'CE'
#     elif any(tr.verdict == 'TLE' for tr in submission.test_results.all()):
#         submission.verdict = 'TLE'
#     elif any(tr.verdict == 'RTE' for tr in submission.test_results.all()):
#         submission.verdict = 'RTE'
#     else:
#         submission.verdict = 'WA'
    
#     submission.passed_tests = passed_tests
#     submission.execution_time = max_time
#     submission.save()


# def run_single_test(submission, test_case):
#     """Run code against a single test case"""
#     try:
#         start_time = time.time()
#         output = run_code(
#             submission.language, 
#             submission.code, 
#             test_case.input_data, 
#             submission.problem.time_limit
#         )
#         end_time = time.time()
#         execution_time = int((end_time - start_time) * 1000)  # Convert to ms

#         # Check for compilation/runtime errors
#         if output.startswith('Error'):
#             return {
#                 'output': output, 
#                 'verdict': 'CE',
#                 'time': 0, 
#                 'memory': 0,
#             }
        
#         # Compare output
#         user_output = output.strip()
#         expected_output = test_case.expected_output.strip()

#         if user_output == expected_output:
#             verdict = 'AC'
#         else:
#             verdict = 'WA'
            
#         return {
#             'output': output, 
#             'verdict': verdict, 
#             'time': execution_time, 
#             'memory': 0
#         }
        
#     except subprocess.TimeoutExpired:
#         return {
#             'output': '', 
#             'verdict': 'TLE',
#             'time': submission.problem.time_limit,
#             'memory': 0
#         }
#     except Exception as e:
#         return {
#             'output': str(e), 
#             'verdict': 'RTE',
#             'time': 0, 
#             'memory': 0,
#         }


# def run_code(language, code, input_data, time_limit_ms):
#     """Execute code with given input and time limit"""
    
#     # Handle empty input
#     if input_data is None:
#         input_data = ""

#     project_path = Path(settings.BASE_DIR)
#     directories = ["codes", "inputs", "outputs"]

#     # Create necessary directories
#     for directory in directories:
#         dir_path = project_path / directory
#         if not dir_path.exists():
#             dir_path.mkdir(parents=True, exist_ok=True)
    
#     codes_dir = project_path / "codes"
#     inputs_dir = project_path / "inputs"
#     outputs_dir = project_path / "outputs"

#     # Generate unique file names
#     unique = str(uuid.uuid4())
#     code_file_name = f"{unique}.{language}"
#     input_file_name = f"{unique}.txt"
#     output_file_name = f"{unique}.txt"

#     code_file_path = codes_dir / code_file_name
#     input_file_path = inputs_dir / input_file_name
#     output_file_path = outputs_dir / output_file_name

#     # Write code to file
#     with open(code_file_path, "w") as code_file:
#         code_file.write(code)
    
#     # Write input to file
#     with open(input_file_path, "w", newline='') as input_file:
#         if input_data:
#             # Ensure consistent line endings and proper formatting
#             clean_input = input_data.replace('\r\n', '\n').replace('\r', '\n')
#             input_file.write(clean_input)
#             if not clean_input.endswith('\n'):
#                 input_file.write('\n')

#     timeout_seconds = time_limit_ms / 1000.0

#     try:
#         if language == "cpp":
#             if platform.system() == "Windows":
#                 executable_name = f"{unique}.exe"
#                 compiler = "g++"
#             else:
#                 executable_name = unique
#                 compiler = "clang++"

#             executable_path = codes_dir / executable_name

#             # Compile the code
#             compile_result = subprocess.run(
#                 [compiler, str(code_file_path), "-o", str(executable_path)], 
#                 capture_output=True, 
#                 text=True, 
#                 timeout=30
#             )

#             if compile_result.returncode != 0:
#                 return f"Error: {compile_result.stderr}"
            
#             # Execute the compiled program
#             with open(input_file_path, "r") as input_file:
#                 result = subprocess.run(
#                     [str(executable_path)], 
#                     stdin=input_file,
#                     stdout=subprocess.PIPE, 
#                     stderr=subprocess.PIPE,
#                     text=True, 
#                     timeout=timeout_seconds
#                 )
                
#                 if result.returncode == 0:
#                     return result.stdout
#                 else:
#                     return f"Error: {result.stderr}"

#         elif language == "py":
#             interpreter = "python" if platform.system() == "Windows" else "python3"

#             with open(input_file_path, "r") as input_file:
#                 result = subprocess.run(
#                     [interpreter, str(code_file_path)], 
#                     stdin=input_file,
#                     stdout=subprocess.PIPE, 
#                     stderr=subprocess.PIPE, 
#                     text=True, 
#                     timeout=timeout_seconds
#                 )
                
#                 if result.returncode == 0:
#                     return result.stdout
#                 else:
#                     return f"Error: {result.stderr}"
        
#         elif language == "c":
#             if platform.system() == "Windows":
#                 executable_name = f"{unique}.exe"
#                 compiler = "gcc"
#             else:
#                 executable_name = unique
#                 compiler = "clang"

#             executable_path = codes_dir / executable_name

#             # Compile the code
#             compile_result = subprocess.run(
#                 [compiler, str(code_file_path), "-o", str(executable_path)], 
#                 capture_output=True, 
#                 text=True, 
#                 timeout=30
#             )
            
#             if compile_result.returncode != 0:
#                 return f"Error: {compile_result.stderr}"
            
#             # Execute the compiled program
#             with open(input_file_path, "r") as input_file:
#                 result = subprocess.run(
#                     [str(executable_path)], 
#                     stdin=input_file, 
#                     stdout=subprocess.PIPE, 
#                     stderr=subprocess.PIPE, 
#                     text=True, 
#                     timeout=timeout_seconds
#                 )
                
#                 if result.returncode == 0:
#                     return result.stdout
#                 else:
#                     return f"Error: {result.stderr}"
                    
#     except subprocess.TimeoutExpired:
#         raise
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         # Clean up temporary files
#         for file_path in [code_file_path, input_file_path, output_file_path]:
#             try:
#                 if file_path.exists():
#                     file_path.unlink()
#             except:
#                 pass

#         # Clean up executable for compiled languages
#         if language in ["cpp", "c"]:
#             try:
#                 executable_path = codes_dir / (unique + (".exe" if platform.system() == "Windows" else ""))
#                 if executable_path.exists():
#                     executable_path.unlink()
#             except:
#                 pass


# def submission_result(request, submission_id):
#     """Display submission results"""
#     submission = get_object_or_404(CodeSubmission, id=submission_id)
#     test_results = submission.test_results.all().order_by('id')
#     return render(request, 'submission_result.html', {
#         'submission': submission,
#         'test_results': test_results  
#     })






# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpRequest
# from submit.forms import CodeSubmissionForm
# from django.conf import settings
# from submit.models import Problem, TestCase, TestResult, CodeSubmission
# import os
# import uuid
# import subprocess
# from pathlib import Path
# import platform
# import time


# # Create your views here.

# def problem_list(request):
#     problems = Problem.objects.all().order_by('-created_at')
#     return render(request, 'problem_list.html', {'problems': problems})  # Removed 'submit/' prefix


# def problem_detail(request, problem_id):
#     problem = get_object_or_404(Problem, id=problem_id)
#     return render(request, 'problem_detail.html', {'problem': problem})  # Removed 'submit/' prefix


# def submit_solution(request, problem_id):
#     problem = get_object_or_404(Problem, id=problem_id)

#     if request.method == 'POST':
#         form = CodeSubmissionForm(request.POST)
#         if form.is_valid():
#             submission = form.save(commit=False)
#             if request.user.is_authenticated:
#                 submission.user = request.user
#             else:
#                 submission.user = None  # Allow anonymous submissions
#             submission.problem = problem
#             submission.save()

#             # Judge the submission with OPTIMIZED batch processing
#             judge_submission_optimized(submission)
#             return redirect('submission_result', submission_id=submission.id)
#     else:
#         form = CodeSubmissionForm()
    
#     return render(request, 'submit_solution.html', {  # Removed 'submit/' prefix
#         'form': form, 
#         'problem': problem
#     })


# def judge_submission_optimized(submission):
#     """OPTIMIZED judging with batch processing"""
#     test_cases = submission.problem.test_cases.all()
#     total_tests = len(test_cases)
#     passed_tests = 0
#     max_time = 0

#     submission.total_tests = total_tests

#     # COMPILE ONCE for all test cases (for compiled languages)
#     compile_result = None
#     if submission.language in ['cpp', 'c']:
#         compile_result = compile_code_once(submission)
#         if compile_result['success'] == False:
#             # Handle compilation error for ALL test cases
#             for test_case in test_cases:
#                 TestResult.objects.create(
#                     submission=submission,
#                     test_case=test_case,
#                     user_output=compile_result['error'],
#                     verdict='CE',
#                     execution_time=0,
#                 )
#             submission.verdict = 'CE'
#             submission.passed_tests = 0
#             submission.execution_time = 0
#             submission.save()
#             return

#     elif submission.language in ['py', 'python']:
#         # Python syntax validation
#         try:
#             compile(submission.code, '<string>', 'exec')
#         except SyntaxError as e:
#             error_msg = f"Python Syntax Error: {str(e)}"
#             for test_case in test_cases:
#                 TestResult.objects.create(
#                     submission=submission,
#                     test_case=test_case,
#                     user_output=error_msg,
#                     verdict='CE',
#                     execution_time=0,
#                 )
#             submission.verdict = 'CE'
#             submission.passed_tests = 0
#             submission.execution_time = 0
#             submission.save()
#             return

#     # Run all test cases with the SAME compiled executable
#     for test_case in test_cases:
#         result = run_single_test_optimized(submission, test_case, compile_result)

#         TestResult.objects.create(
#             submission=submission,
#             test_case=test_case,
#             user_output=result['output'],
#             verdict=result['verdict'],
#             execution_time=result['time'],
#         )

#         if result['verdict'] == 'AC':
#             passed_tests += 1
#         elif result['verdict'] in ['TLE', 'RTE', 'CE']:
#             break

#         max_time = max(max_time, result.get('time', 0))
    
#     # Determine overall verdict
#     if passed_tests == total_tests:
#         submission.verdict = 'AC'
#     elif any(tr.verdict == 'CE' for tr in submission.test_results.all()):
#         submission.verdict = 'CE'
#     elif any(tr.verdict == 'TLE' for tr in submission.test_results.all()):
#         submission.verdict = 'TLE'
#     elif any(tr.verdict == 'RTE' for tr in submission.test_results.all()):
#         submission.verdict = 'RTE'
#     else:
#         submission.verdict = 'WA'
    
#     submission.passed_tests = passed_tests
#     submission.execution_time = max_time
#     submission.save()

#     # Cleanup compiled executable
#     if submission.language in ['cpp', 'c'] and compile_result:
#         cleanup_executable(compile_result.get('executable_path'))


# def compile_code_once(submission):
#     """Compile code ONCE and return executable path"""
#     project_path = Path(settings.BASE_DIR)
#     codes_dir = project_path / "codes"
    
#     if not codes_dir.exists():
#         codes_dir.mkdir(parents=True, exist_ok=True)
    
#     unique = str(uuid.uuid4())
#     code_file_name = f"{unique}.{submission.language}"
#     code_file_path = codes_dir / code_file_name
    
#     # Write code to file
#     with open(code_file_path, "w") as code_file:
#         code_file.write(submission.code)
    
#     try:
#         if submission.language == "cpp":
#             if platform.system() == "Windows":
#                 executable_name = f"{unique}.exe"
#                 compiler = "g++"
#             else:
#                 executable_name = unique
#                 compiler = "clang++"

#             executable_path = codes_dir / executable_name

#             # Compile with optimization
#             compile_result = subprocess.run(
#                 [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
#                 capture_output=True, 
#                 text=True, 
#                 timeout=30
#             )

#             # Cleanup source file immediately
#             try:
#                 code_file_path.unlink()
#             except:
#                 pass

#             if compile_result.returncode != 0:
#                 return {
#                     'success': False,
#                     'error': f"Error: {compile_result.stderr}",
#                     'executable_path': None
#                 }
            
#             return {
#                 'success': True,
#                 'error': None,
#                 'executable_path': executable_path
#             }
            
#         elif submission.language == "c":
#             if platform.system() == "Windows":
#                 executable_name = f"{unique}.exe"
#                 compiler = "gcc"
#             else:
#                 executable_name = unique
#                 compiler = "clang"

#             executable_path = codes_dir / executable_name

#             # Compile with optimization
#             compile_result = subprocess.run(
#                 [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
#                 capture_output=True, 
#                 text=True, 
#                 timeout=30
#             )

#             # Cleanup source file immediately
#             try:
#                 code_file_path.unlink()
#             except:
#                 pass

#             if compile_result.returncode != 0:
#                 return {
#                     'success': False,
#                     'error': f"Error: {compile_result.stderr}",
#                     'executable_path': None
#                 }
            
#             return {
#                 'success': True,
#                 'error': None,
#                 'executable_path': executable_path
#             }
            
#     except Exception as e:
#         try:
#             code_file_path.unlink()
#         except:
#             pass
#         return {
#             'success': False,
#             'error': f"Error: {str(e)}",
#             'executable_path': None
#         }


# def run_single_test_optimized(submission, test_case, compile_result=None):
#     """Optimized single test execution"""
#     try:
#         start_time = time.time()
        
#         if submission.language in ['cpp', 'c'] and compile_result:
#             # Use pre-compiled executable
#             output = run_compiled_code(compile_result['executable_path'], test_case.input_data, submission.problem.time_limit)
#         elif submission.language in ['py', 'python']:
#             # For Python, still needs file creation but optimized
#             output = run_code_python(submission.code, test_case.input_data, submission.problem.time_limit)
#         else:
#             # Fallback to original run_code
#             output = run_code(submission.language, submission.code, test_case.input_data, submission.problem.time_limit)
        
#         end_time = time.time()
#         execution_time = int((end_time - start_time) * 1000)

#         if output.startswith('Error'):
#             return {
#                 'output': output, 
#                 'verdict': 'CE',
#                 'time': 0, 
#                 'memory': 0,
#             }
        
#         user_output = output.strip()
#         expected_output = test_case.expected_output.strip()

#         if user_output == expected_output:
#             verdict = 'AC'
#         else:
#             verdict = 'WA'
            
#         return {
#             'output': output, 
#             'verdict': verdict, 
#             'time': execution_time, 
#             'memory': 0
#         }
        
#     except subprocess.TimeoutExpired:
#         return {
#             'output': '', 
#             'verdict': 'TLE',
#             'time': submission.problem.time_limit,
#             'memory': 0
#         }
#     except Exception as e:
#         return {
#             'output': str(e), 
#             'verdict': 'RTE',
#             'time': 0, 
#             'memory': 0,
#         }


# def run_compiled_code(executable_path, input_data, time_limit_ms):
#     """Execute pre-compiled code with input"""
#     project_path = Path(settings.BASE_DIR)
#     inputs_dir = project_path / "inputs"
    
#     if not inputs_dir.exists():
#         inputs_dir.mkdir(parents=True, exist_ok=True)
    
#     unique = str(uuid.uuid4())
#     input_file_path = inputs_dir / f"{unique}.txt"
    
#     try:
#         # Write input to temporary file
#         with open(input_file_path, "w", newline='') as input_file:
#             if input_data:
#                 clean_input = input_data.replace('\r\n', '\n').replace('\r', '\n')
#                 input_file.write(clean_input)
#                 if not clean_input.endswith('\n'):
#                     input_file.write('\n')

#         timeout_seconds = time_limit_ms / 1000.0

#         # Execute with input
#         with open(input_file_path, "r") as input_file:
#             result = subprocess.run(
#                 [str(executable_path)], 
#                 stdin=input_file,
#                 stdout=subprocess.PIPE, 
#                 stderr=subprocess.PIPE,
#                 text=True, 
#                 timeout=timeout_seconds
#             )
            
#             if result.returncode == 0:
#                 return result.stdout
#             else:
#                 return f"Error: {result.stderr}"
                
#     except subprocess.TimeoutExpired:
#         raise
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         try:
#             if input_file_path.exists():
#                 input_file_path.unlink()
#         except:
#             pass


# def run_code_python(code, input_data, time_limit_ms):
#     """Execute Python code efficiently"""
#     project_path = Path(settings.BASE_DIR)
#     codes_dir = project_path / "codes"
#     inputs_dir = project_path / "inputs"
    
#     for directory in [codes_dir, inputs_dir]:
#         if not directory.exists():
#             directory.mkdir(parents=True, exist_ok=True)
    
#     unique = str(uuid.uuid4())
#     code_file_path = codes_dir / f"{unique}.py"
#     input_file_path = inputs_dir / f"{unique}.txt"
    
#     try:
#         with open(code_file_path, "w") as code_file:
#             code_file.write(code)
        
#         with open(input_file_path, "w", newline='') as input_file:
#             if input_data:
#                 clean_input = input_data.replace('\r\n', '\n').replace('\r', '\n')
#                 input_file.write(clean_input)
#                 if not clean_input.endswith('\n'):
#                     input_file.write('\n')

#         timeout_seconds = time_limit_ms / 1000.0
#         interpreter = "python" if platform.system() == "Windows" else "python3"

#         with open(input_file_path, "r") as input_file:
#             result = subprocess.run(
#                 [interpreter, str(code_file_path)], 
#                 stdin=input_file,
#                 stdout=subprocess.PIPE, 
#                 stderr=subprocess.PIPE, 
#                 text=True, 
#                 timeout=timeout_seconds
#             )
            
#             if result.returncode == 0:
#                 return result.stdout
#             else:
#                 return f"Error: {result.stderr}"
                
#     except subprocess.TimeoutExpired:
#         raise
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         for file_path in [code_file_path, input_file_path]:
#             try:
#                 if file_path.exists():
#                     file_path.unlink()
#             except:
#                 pass


# def cleanup_executable(executable_path):
#     """Clean up compiled executable"""
#     try:
#         if executable_path and executable_path.exists():
#             executable_path.unlink()
#     except:
#         pass


# def submission_result(request, submission_id):
#     """Display submission results"""
#     submission = get_object_or_404(CodeSubmission, id=submission_id)
#     test_results = submission.test_results.all().order_by('id')
#     return render(request, 'submission_result.html', {  # Removed 'submit/' prefix
#         'submission': submission,
#         'test_results': test_results  
#     })


# def run_code(language, code, input_data, time_limit_ms):
#     """Fallback run_code function for compatibility"""
    
#     # Handle empty input
#     if input_data is None:
#         input_data = ""

#     # Route to appropriate language handler
#     if language in ['py', 'python']:
#         return run_code_python(code, input_data, time_limit_ms)
    
#     # For compiled languages (C/C++)
#     project_path = Path(settings.BASE_DIR)
#     directories = ["codes", "inputs", "outputs"]

#     for directory in directories:
#         dir_path = project_path / directory
#         if not dir_path.exists():
#             dir_path.mkdir(parents=True, exist_ok=True)
    
#     codes_dir = project_path / "codes"
#     inputs_dir = project_path / "inputs"
#     outputs_dir = project_path / "outputs"

#     unique = str(uuid.uuid4())
#     code_file_name = f"{unique}.{language}"
#     input_file_name = f"{unique}.txt"
#     output_file_name = f"{unique}.txt"

#     code_file_path = codes_dir / code_file_name
#     input_file_path = inputs_dir / input_file_name
#     output_file_path = outputs_dir / output_file_name

#     with open(code_file_path, "w") as code_file:
#         code_file.write(code)
    
#     with open(input_file_path, "w", newline='') as input_file:
#         if input_data:
#             clean_input = input_data.replace('\r\n', '\n').replace('\r', '\n')
#             input_file.write(clean_input)
#             if not clean_input.endswith('\n'):
#                 input_file.write('\n')

#     timeout_seconds = time_limit_ms / 1000.0

#     try:
#         if language == "cpp":
#             if platform.system() == "Windows":
#                 executable_name = f"{unique}.exe"
#                 compiler = "g++"
#             else:
#                 executable_name = unique
#                 compiler = "clang++"

#             executable_path = codes_dir / executable_name

#             compile_result = subprocess.run(
#                 [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
#                 capture_output=True, 
#                 text=True, 
#                 timeout=30
#             )

#             if compile_result.returncode != 0:
#                 return f"Error: {compile_result.stderr}"
            
#             with open(input_file_path, "r") as input_file:
#                 result = subprocess.run(
#                     [str(executable_path)], 
#                     stdin=input_file,
#                     stdout=subprocess.PIPE, 
#                     stderr=subprocess.PIPE,
#                     text=True, 
#                     timeout=timeout_seconds
#                 )
                
#                 if result.returncode == 0:
#                     return result.stdout
#                 else:
#                     return f"Error: {result.stderr}"

#         elif language == "c":
#             if platform.system() == "Windows":
#                 executable_name = f"{unique}.exe"
#                 compiler = "gcc"
#             else:
#                 executable_name = unique
#                 compiler = "clang"

#             executable_path = codes_dir / executable_name

#             compile_result = subprocess.run(
#                 [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
#                 capture_output=True, 
#                 text=True, 
#                 timeout=30
#             )
            
#             if compile_result.returncode != 0:
#                 return f"Error: {compile_result.stderr}"
            
#             with open(input_file_path, "r") as input_file:
#                 result = subprocess.run(
#                     [str(executable_path)], 
#                     stdin=input_file, 
#                     stdout=subprocess.PIPE, 
#                     stderr=subprocess.PIPE, 
#                     text=True, 
#                     timeout=timeout_seconds
#                 )
                
#                 if result.returncode == 0:
#                     return result.stdout
#                 else:
#                     return f"Error: {result.stderr}"
        
#         else:
#             return f"Error: Unsupported language '{language}'"
                    
#     except subprocess.TimeoutExpired:
#         raise
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         for file_path in [code_file_path, input_file_path, output_file_path]:
#             try:
#                 if file_path.exists():
#                     file_path.unlink()
#             except:
#                 pass

#         if language in ["cpp", "c"]:
#             try:
#                 executable_path = codes_dir / (unique + (".exe" if platform.system() == "Windows" else ""))
#                 if executable_path.exists():
#                     executable_path.unlink()
#             except:
#                 pass


# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpRequest
# from submit.forms import CodeSubmissionForm
# from django.conf import settings
# from submit.models import Problem, TestCase, TestResult, CodeSubmission
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# import os
# import uuid
# import subprocess
# from pathlib import Path
# import platform
# import time
# import tempfile


# # Create your views here.


# def problem_list(request):
#     problems = Problem.objects.all().order_by('-created_at')
#     return render(request, 'problem_list.html', {'problems': problems})


# def problem_detail(request, problem_id):
#     problem = get_object_or_404(Problem, id=problem_id)
#     return render(request, 'problem_detail.html', {'problem': problem})


# @login_required
# def submit_solution(request, problem_id):
#     problem = get_object_or_404(Problem, id=problem_id)

#     if request.method == 'POST':
#         form = CodeSubmissionForm(request.POST)
#         if form.is_valid():
#             submission = form.save(commit=False)
#             if request.user.is_authenticated:
#                 submission.user = request.user
#             else:
#                 submission.user = None  # Allow anonymous submissions
#             submission.problem = problem
#             submission.save()

#             # Use ultra-optimized judging
#             judge_submission_ultra_optimized(submission)
#             return redirect('submission_result', submission_id=submission.id)
#     else:
#         form = CodeSubmissionForm()
    
#     return render(request, 'submit_solution.html', {
#         'form': form, 
#         'problem': problem
#     })


# def judge_submission_ultra_optimized(submission):
#     """ULTRA OPTIMIZED judging with minimal I/O and batch processing"""
#     test_cases = list(submission.problem.test_cases.all())
#     total_tests = len(test_cases)
#     passed_tests = 0
#     max_time = 0
#     test_results = []  # Batch database operations

#     submission.total_tests = total_tests

#     # COMPILE ONCE for all test cases
#     compile_result = None
#     if submission.language in ['cpp', 'c']:
#         compile_result = compile_code_once(submission)
#         if not compile_result['success']:
#             # Handle compilation error for ALL test cases
#             bulk_create_ce_results(submission, test_cases, compile_result['error'])
#             return

#     elif submission.language in ['py', 'python']:
#         # Python syntax validation
#         try:
#             compile(submission.code, '<string>', 'exec')
#         except SyntaxError as e:
#             error_msg = f"Python Syntax Error: {str(e)}"
#             bulk_create_ce_results(submission, test_cases, error_msg)
#             return

#     # BATCH PROCESS all test cases
#     if submission.language in ['cpp', 'c']:
#         results = run_batch_compiled(compile_result['executable_path'], test_cases, submission.problem.time_limit)
#     else:
#         results = run_batch_python(submission.code, test_cases, submission.problem.time_limit)

#     # Process results and create TestResult objects in batch
#     for i, (test_case, result) in enumerate(zip(test_cases, results)):
#         test_results.append(TestResult(
#             submission=submission,
#             test_case=test_case,
#             user_output=result['output'],
#             verdict=result['verdict'],
#             execution_time=result['time'],
#             memory_used=result.get('memory', 0),
#         ))

#         if result['verdict'] == 'AC':
#             passed_tests += 1
#         elif result['verdict'] in ['TLE', 'RTE', 'CE']:
#             # Include remaining test cases as not run
#             break

#         max_time = max(max_time, result.get('time', 0))

#     # BULK CREATE all test results at once
#     with transaction.atomic():
#         TestResult.objects.bulk_create(test_results)

#     # Determine overall verdict
#     if passed_tests == total_tests:
#         submission.verdict = 'AC'
#     elif any(tr.verdict == 'CE' for tr in test_results):
#         submission.verdict = 'CE'
#     elif any(tr.verdict == 'TLE' for tr in test_results):
#         submission.verdict = 'TLE'
#     elif any(tr.verdict == 'RTE' for tr in test_results):
#         submission.verdict = 'RTE'
#     else:
#         submission.verdict = 'WA'
    
#     submission.passed_tests = passed_tests
#     submission.execution_time = max_time
#     submission.memory_used = 0  # Will be updated if memory monitoring is needed
#     submission.save()

#     # Cleanup
#     if submission.language in ['cpp', 'c'] and compile_result:
#         cleanup_executable(compile_result.get('executable_path'))


# def compile_code_once(submission):
#     """Compile code ONCE and return executable path"""
#     project_path = Path(settings.BASE_DIR)
#     codes_dir = project_path / "codes"
    
#     if not codes_dir.exists():
#         codes_dir.mkdir(parents=True, exist_ok=True)
    
#     unique = str(uuid.uuid4())
#     code_file_name = f"{unique}.{submission.language}"
#     code_file_path = codes_dir / code_file_name
    
#     # Write code to file
#     with open(code_file_path, "w") as code_file:
#         code_file.write(submission.code)
    
#     try:
#         if submission.language == "cpp":
#             if platform.system() == "Windows":
#                 executable_name = f"{unique}.exe"
#                 compiler = "g++"
#             else:
#                 executable_name = unique
#                 compiler = "clang++"

#             executable_path = codes_dir / executable_name

#             # Compile with optimization
#             compile_result = subprocess.run(
#                 [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
#                 capture_output=True, 
#                 text=True, 
#                 timeout=30
#             )

#             # Cleanup source file immediately
#             try:
#                 code_file_path.unlink()
#             except:
#                 pass

#             if compile_result.returncode != 0:
#                 return {
#                     'success': False,
#                     'error': f"Compilation Error: {compile_result.stderr}",
#                     'executable_path': None
#                 }
            
#             return {
#                 'success': True,
#                 'error': None,
#                 'executable_path': executable_path
#             }
            
#         elif submission.language == "c":
#             if platform.system() == "Windows":
#                 executable_name = f"{unique}.exe"
#                 compiler = "gcc"
#             else:
#                 executable_name = unique
#                 compiler = "clang"

#             executable_path = codes_dir / executable_name

#             # Compile with optimization
#             compile_result = subprocess.run(
#                 [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
#                 capture_output=True, 
#                 text=True, 
#                 timeout=30
#             )

#             # Cleanup source file immediately
#             try:
#                 code_file_path.unlink()
#             except:
#                 pass

#             if compile_result.returncode != 0:
#                 return {
#                     'success': False,
#                     'error': f"Compilation Error: {compile_result.stderr}",
#                     'executable_path': None
#                 }
            
#             return {
#                 'success': True,
#                 'error': None,
#                 'executable_path': executable_path
#             }
            
#     except Exception as e:
#         try:
#             code_file_path.unlink()
#         except:
#             pass
#         return {
#             'success': False,
#             'error': f"Compilation Error: {str(e)}",
#             'executable_path': None
#         }


# def run_batch_compiled(executable_path, test_cases, time_limit_ms):
#     """Run all test cases with minimal overhead"""
#     results = []
#     timeout_seconds = time_limit_ms / 1000.0
    
#     for test_case in test_cases:
#         start_time = time.time()
        
#         try:
#             # Use temporary file with context manager for auto cleanup
#             with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_input:
#                 if test_case.input_data:
#                     clean_input = test_case.input_data.replace('\r\n', '\n').replace('\r', '\n')
#                     temp_input.write(clean_input)
#                     if not clean_input.endswith('\n'):
#                         temp_input.write('\n')
#                 temp_input_path = temp_input.name

#             # Execute with minimal overhead
#             with open(temp_input_path, "r") as input_file:
#                 result = subprocess.run(
#                     [str(executable_path)], 
#                     stdin=input_file,
#                     stdout=subprocess.PIPE, 
#                     stderr=subprocess.PIPE,
#                     text=True, 
#                     timeout=timeout_seconds
#                 )
            
#             # Immediate cleanup
#             Path(temp_input_path).unlink(missing_ok=True)
            
#             end_time = time.time()
#             execution_time = int((end_time - start_time) * 1000)

#             if result.returncode == 0:
#                 output = result.stdout.strip()
#                 expected = test_case.expected_output.strip()
#                 verdict = 'AC' if output == expected else 'WA'
#             else:
#                 output = f"Runtime Error: {result.stderr}"
#                 verdict = 'RTE'

#             results.append({
#                 'output': output,
#                 'verdict': verdict,
#                 'time': execution_time,
#                 'memory': 0
#             })

#         except subprocess.TimeoutExpired:
#             try:
#                 Path(temp_input_path).unlink(missing_ok=True)
#             except:
#                 pass
#             results.append({
#                 'output': 'Time Limit Exceeded',
#                 'verdict': 'TLE',
#                 'time': time_limit_ms,
#                 'memory': 0
#             })
#             break  # Stop on first TLE
            
#         except Exception as e:
#             try:
#                 Path(temp_input_path).unlink(missing_ok=True)
#             except:
#                 pass
#             results.append({
#                 'output': f"Error: {str(e)}",
#                 'verdict': 'RTE',
#                 'time': 0,
#                 'memory': 0
#             })
#             break

#     return results


# def run_batch_python(code, test_cases, time_limit_ms):
#     """Run Python code with all test cases efficiently"""
#     results = []
#     timeout_seconds = time_limit_ms / 1000.0
    
#     # Create code file once
#     with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_code:
#         temp_code.write(code)
#         temp_code_path = temp_code.name

#     try:
#         interpreter = "python" if platform.system() == "Windows" else "python3"
        
#         for test_case in test_cases:
#             start_time = time.time()
            
#             try:
#                 # Create input file
#                 with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_input:
#                     if test_case.input_data:
#                         clean_input = test_case.input_data.replace('\r\n', '\n').replace('\r', '\n')
#                         temp_input.write(clean_input)
#                         if not clean_input.endswith('\n'):
#                             temp_input.write('\n')
#                     temp_input_path = temp_input.name

#                 # Execute
#                 with open(temp_input_path, "r") as input_file:
#                     result = subprocess.run(
#                         [interpreter, temp_code_path], 
#                         stdin=input_file,
#                         stdout=subprocess.PIPE, 
#                         stderr=subprocess.PIPE, 
#                         text=True, 
#                         timeout=timeout_seconds
#                     )
                
#                 # Cleanup input file immediately
#                 Path(temp_input_path).unlink(missing_ok=True)
                
#                 end_time = time.time()
#                 execution_time = int((end_time - start_time) * 1000)

#                 if result.returncode == 0:
#                     output = result.stdout.strip()
#                     expected = test_case.expected_output.strip()
#                     verdict = 'AC' if output == expected else 'WA'
#                 else:
#                     output = f"Runtime Error: {result.stderr}"
#                     verdict = 'RTE'

#                 results.append({
#                     'output': output,
#                     'verdict': verdict,
#                     'time': execution_time,
#                     'memory': 0
#                 })

#             except subprocess.TimeoutExpired:
#                 try:
#                     Path(temp_input_path).unlink(missing_ok=True)
#                 except:
#                     pass
#                 results.append({
#                     'output': 'Time Limit Exceeded',
#                     'verdict': 'TLE',
#                     'time': time_limit_ms,
#                     'memory': 0
#                 })
#                 break
                
#             except Exception as e:
#                 try:
#                     Path(temp_input_path).unlink(missing_ok=True)
#                 except:
#                     pass
#                 results.append({
#                     'output': f"Error: {str(e)}",
#                     'verdict': 'RTE',
#                     'time': 0,
#                     'memory': 0
#                 })
#                 break

#     finally:
#         # Cleanup code file
#         try:
#             Path(temp_code_path).unlink(missing_ok=True)
#         except:
#             pass

#     return results


# def bulk_create_ce_results(submission, test_cases, error_msg):
#     """Create compilation error results for all test cases in bulk"""
#     ce_results = [
#         TestResult(
#             submission=submission,
#             test_case=test_case,
#             user_output=error_msg,
#             verdict='CE',
#             execution_time=0,
#             memory_used=0,
#         )
#         for test_case in test_cases
#     ]
    
#     with transaction.atomic():
#         TestResult.objects.bulk_create(ce_results)
    
#     submission.verdict = 'CE'
#     submission.passed_tests = 0
#     submission.execution_time = 0
#     submission.memory_used = 0
#     submission.save()


# def cleanup_executable(executable_path):
#     """Clean up compiled executable"""
#     try:
#         if executable_path and Path(executable_path).exists():
#             Path(executable_path).unlink()
#     except:
#         pass


# def submission_result(request, submission_id):
#     """Display submission results"""
#     submission = get_object_or_404(CodeSubmission, id=submission_id)
#     test_results = submission.test_results.all().order_by('id')
#     return render(request, 'submission_result.html', {
#         'submission': submission,
#         'test_results': test_results  
#     })


# # Fallback function for compatibility (if needed elsewhere)
# def run_code(language, code, input_data, time_limit_ms):
#     """Fallback run_code function for compatibility"""
    
#     # Handle empty input
#     if input_data is None:
#         input_data = ""

#     # Route to appropriate language handler
#     if language in ['py', 'python']:
#         return run_code_python(code, input_data, time_limit_ms)
    
#     # For compiled languages (C/C++)
#     project_path = Path(settings.BASE_DIR)
#     directories = ["codes", "inputs", "outputs"]

#     for directory in directories:
#         dir_path = project_path / directory
#         if not dir_path.exists():
#             dir_path.mkdir(parents=True, exist_ok=True)
    
#     codes_dir = project_path / "codes"
#     inputs_dir = project_path / "inputs"
#     outputs_dir = project_path / "outputs"

#     unique = str(uuid.uuid4())
#     code_file_name = f"{unique}.{language}"
#     input_file_name = f"{unique}.txt"
#     output_file_name = f"{unique}.txt"

#     code_file_path = codes_dir / code_file_name
#     input_file_path = inputs_dir / input_file_name
#     output_file_path = outputs_dir / output_file_name

#     with open(code_file_path, "w") as code_file:
#         code_file.write(code)
    
#     with open(input_file_path, "w", newline='') as input_file:
#         if input_data:
#             clean_input = input_data.replace('\r\n', '\n').replace('\r', '\n')
#             input_file.write(clean_input)
#             if not clean_input.endswith('\n'):
#                 input_file.write('\n')

#     timeout_seconds = time_limit_ms / 1000.0

#     try:
#         if language == "cpp":
#             if platform.system() == "Windows":
#                 executable_name = f"{unique}.exe"
#                 compiler = "g++"
#             else:
#                 executable_name = unique
#                 compiler = "clang++"

#             executable_path = codes_dir / executable_name

#             compile_result = subprocess.run(
#                 [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
#                 capture_output=True, 
#                 text=True, 
#                 timeout=30
#             )

#             if compile_result.returncode != 0:
#                 return f"Compilation Error: {compile_result.stderr}"
            
#             with open(input_file_path, "r") as input_file:
#                 result = subprocess.run(
#                     [str(executable_path)], 
#                     stdin=input_file,
#                     stdout=subprocess.PIPE, 
#                     stderr=subprocess.PIPE,
#                     text=True, 
#                     timeout=timeout_seconds
#                 )
                
#                 if result.returncode == 0:
#                     return result.stdout
#                 else:
#                     return f"Runtime Error: {result.stderr}"

#         elif language == "c":
#             if platform.system() == "Windows":
#                 executable_name = f"{unique}.exe"
#                 compiler = "gcc"
#             else:
#                 executable_name = unique
#                 compiler = "clang"

#             executable_path = codes_dir / executable_name

#             compile_result = subprocess.run(
#                 [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
#                 capture_output=True, 
#                 text=True, 
#                 timeout=30
#             )
            
#             if compile_result.returncode != 0:
#                 return f"Compilation Error: {compile_result.stderr}"
            
#             with open(input_file_path, "r") as input_file:
#                 result = subprocess.run(
#                     [str(executable_path)], 
#                     stdin=input_file, 
#                     stdout=subprocess.PIPE, 
#                     stderr=subprocess.PIPE, 
#                     text=True, 
#                     timeout=timeout_seconds
#                 )
                
#                 if result.returncode == 0:
#                     return result.stdout
#                 else:
#                     return f"Runtime Error: {result.stderr}"
        
#         else:
#             return f"Error: Unsupported language '{language}'"
                    
#     except subprocess.TimeoutExpired:
#         raise
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         for file_path in [code_file_path, input_file_path, output_file_path]:
#             try:
#                 if file_path.exists():
#                     file_path.unlink()
#             except:
#                 pass

#         if language in ["cpp", "c"]:
#             try:
#                 executable_path = codes_dir / (unique + (".exe" if platform.system() == "Windows" else ""))
#                 if executable_path.exists():
#                     executable_path.unlink()
#             except:
#                 pass


# def run_code_python(code, input_data, time_limit_ms):
#     """Execute Python code efficiently"""
#     project_path = Path(settings.BASE_DIR)
#     codes_dir = project_path / "codes"
#     inputs_dir = project_path / "inputs"
    
#     for directory in [codes_dir, inputs_dir]:
#         if not directory.exists():
#             directory.mkdir(parents=True, exist_ok=True)
    
#     unique = str(uuid.uuid4())
#     code_file_path = codes_dir / f"{unique}.py"
#     input_file_path = inputs_dir / f"{unique}.txt"
    
#     try:
#         with open(code_file_path, "w") as code_file:
#             code_file.write(code)
        
#         with open(input_file_path, "w", newline='') as input_file:
#             if input_data:
#                 clean_input = input_data.replace('\r\n', '\n').replace('\r', '\n')
#                 input_file.write(clean_input)
#                 if not clean_input.endswith('\n'):
#                     input_file.write('\n')

#         timeout_seconds = time_limit_ms / 1000.0
#         interpreter = "python" if platform.system() == "Windows" else "python3"

#         with open(input_file_path, "r") as input_file:
#             result = subprocess.run(
#                 [interpreter, str(code_file_path)], 
#                 stdin=input_file,
#                 stdout=subprocess.PIPE, 
#                 stderr=subprocess.PIPE, 
#                 text=True, 
#                 timeout=timeout_seconds
#             )
            
#             if result.returncode == 0:
#                 return result.stdout
#             else:
#                 return f"Runtime Error: {result.stderr}"
                
#     except subprocess.TimeoutExpired:
#         raise
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         for file_path in [code_file_path, input_file_path]:
#             try:
#                 if file_path.exists():
#                     file_path.unlink()
#             except:
#                 pass


from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest
from submit.forms import CodeSubmissionForm
from django.conf import settings
from submit.models import Problem, TestCase, TestResult, CodeSubmission
from django.contrib.auth.decorators import login_required
from django.db import transaction
import os
import uuid
import subprocess
from pathlib import Path
import platform
import time
import tempfile
import re


# Create your views here.


def problem_list(request):
    problems = Problem.objects.all().order_by('-created_at')
    return render(request, 'problem_list.html', {'problems': problems})


def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    return render(request, 'problem_detail.html', {'problem': problem})


@login_required
def submit_solution(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    if request.method == 'POST':
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            if request.user.is_authenticated:
                submission.user = request.user
            else:
                submission.user = None  # Allow anonymous submissions
            submission.problem = problem
            submission.save()

            # Use ultra-optimized judging
            judge_submission_ultra_optimized(submission)
            return redirect('submission_result', submission_id=submission.id)
    else:
        form = CodeSubmissionForm()
    
    return render(request, 'submit_solution.html', {
        'form': form, 
        'problem': problem
    })


def judge_submission_ultra_optimized(submission):
    """ULTRA OPTIMIZED judging with minimal I/O and batch processing"""
    test_cases = list(submission.problem.test_cases.all())
    total_tests = len(test_cases)
    passed_tests = 0
    max_time = 0
    test_results = []  # Batch database operations

    submission.total_tests = total_tests

    # COMPILE ONCE for all test cases
    compile_result = None
    if submission.language in ['cpp', 'c']:
        compile_result = compile_code_once(submission)
        if not compile_result['success']:
            # Handle compilation error for ALL test cases
            bulk_create_ce_results(submission, test_cases, compile_result['error'])
            return

    elif submission.language in ['py', 'python']:
        # Python syntax validation
        try:
            compile(submission.code, '<string>', 'exec')
        except SyntaxError as e:
            error_msg = f"Python Syntax Error: {str(e)}"
            bulk_create_ce_results(submission, test_cases, error_msg)
            return

    # BATCH PROCESS all test cases
    if submission.language in ['cpp', 'c']:
        results = run_batch_compiled(compile_result['executable_path'], test_cases, submission.problem.time_limit)
    else:
        results = run_batch_python(submission.code, test_cases, submission.problem.time_limit)

    # Process results and create TestResult objects in batch
    for i, (test_case, result) in enumerate(zip(test_cases, results)):
        test_results.append(TestResult(
            submission=submission,
            test_case=test_case,
            user_output=result['output'],
            verdict=result['verdict'],
            execution_time=result['time'],
            memory_used=result.get('memory', 0),
        ))

        if result['verdict'] == 'AC':
            passed_tests += 1
        elif result['verdict'] in ['TLE', 'RTE', 'CE']:
            # Include remaining test cases as not run
            break

        max_time = max(max_time, result.get('time', 0))

    # BULK CREATE all test results at once
    with transaction.atomic():
        TestResult.objects.bulk_create(test_results)

    # Determine overall verdict
    if passed_tests == total_tests:
        submission.verdict = 'AC'
    elif any(tr.verdict == 'CE' for tr in test_results):
        submission.verdict = 'CE'
    elif any(tr.verdict == 'TLE' for tr in test_results):
        submission.verdict = 'TLE'
    elif any(tr.verdict == 'RTE' for tr in test_results):
        submission.verdict = 'RTE'
    else:
        submission.verdict = 'WA'
    
    submission.passed_tests = passed_tests
    submission.execution_time = max_time
    submission.memory_used = 0  # Will be updated if memory monitoring is needed
    submission.save()

    # Cleanup
    if submission.language in ['cpp', 'c'] and compile_result:
        cleanup_executable(compile_result.get('executable_path'))


def compile_code_once(submission):
    """Compile code ONCE and return executable path"""
    project_path = Path(settings.BASE_DIR)
    codes_dir = project_path / "codes"
    
    if not codes_dir.exists():
        codes_dir.mkdir(parents=True, exist_ok=True)
    
    unique = str(uuid.uuid4())
    code_file_name = f"{unique}.{submission.language}"
    code_file_path = codes_dir / code_file_name
    
    # Write code to file
    with open(code_file_path, "w") as code_file:
        code_file.write(submission.code)
    
    try:
        if submission.language == "cpp":
            if platform.system() == "Windows":
                executable_name = f"{unique}.exe"
                compiler = "g++"
            else:
                executable_name = unique
                compiler = "clang++"

            executable_path = codes_dir / executable_name

            # Compile with optimization
            compile_result = subprocess.run(
                [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
                capture_output=True, 
                text=True, 
                timeout=30
            )

            # Cleanup source file immediately
            try:
                code_file_path.unlink()
            except:
                pass

            if compile_result.returncode != 0:
                return {
                    'success': False,
                    'error': f"Compilation Error: {compile_result.stderr}",
                    'executable_path': None
                }
            
            return {
                'success': True,
                'error': None,
                'executable_path': executable_path
            }
            
        elif submission.language == "c":
            if platform.system() == "Windows":
                executable_name = f"{unique}.exe"
                compiler = "gcc"
            else:
                executable_name = unique
                compiler = "clang"

            executable_path = codes_dir / executable_name

            # Compile with optimization
            compile_result = subprocess.run(
                [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
                capture_output=True, 
                text=True, 
                timeout=30
            )

            # Cleanup source file immediately
            try:
                code_file_path.unlink()
            except:
                pass

            if compile_result.returncode != 0:
                return {
                    'success': False,
                    'error': f"Compilation Error: {compile_result.stderr}",
                    'executable_path': None
                }
            
            return {
                'success': True,
                'error': None,
                'executable_path': executable_path
            }
            
    except Exception as e:
        try:
            code_file_path.unlink()
        except:
            pass
        return {
            'success': False,
            'error': f"Compilation Error: {str(e)}",
            'executable_path': None
        }


def preprocess_input_for_python(input_data):
    """
    Preprocess input data to make it compatible with Python's line-by-line input reading.
    Converts space-separated values on the same line to separate lines when appropriate.
    """
    if not input_data:
        return input_data
    
    lines = input_data.strip().split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Split by spaces
        parts = line.split()
        
        # If line has 2-5 numbers (likely parameters, not an array), split them
        if len(parts) >= 2 and len(parts) <= 5:
            # Check if all parts are integers
            try:
                [int(part) for part in parts]
                # If all are integers and not too many, split into separate lines
                processed_lines.extend(parts)
            except ValueError:
                # If not all integers, keep original line
                processed_lines.append(line)
        else:
            # Keep arrays and single values as they are
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)


def run_batch_compiled(executable_path, test_cases, time_limit_ms):
    """Run all test cases with minimal overhead"""
    results = []
    timeout_seconds = time_limit_ms / 1000.0
    
    for test_case in test_cases:
        start_time = time.time()
        
        try:
            # Use temporary file with context manager for auto cleanup
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_input:
                if test_case.input_data:
                    clean_input = test_case.input_data.replace('\r\n', '\n').replace('\r', '\n')
                    temp_input.write(clean_input)
                    if not clean_input.endswith('\n'):
                        temp_input.write('\n')
                temp_input_path = temp_input.name

            # Execute with minimal overhead
            with open(temp_input_path, "r") as input_file:
                result = subprocess.run(
                    [str(executable_path)], 
                    stdin=input_file,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True, 
                    timeout=timeout_seconds
                )
            
            # Immediate cleanup
            Path(temp_input_path).unlink(missing_ok=True)
            
            end_time = time.time()
            execution_time = int((end_time - start_time) * 1000)

            if result.returncode == 0:
                output = result.stdout.strip()
                expected = test_case.expected_output.strip()
                verdict = 'AC' if output == expected else 'WA'
            else:
                output = f"Runtime Error: {result.stderr}"
                verdict = 'RTE'

            results.append({
                'output': output,
                'verdict': verdict,
                'time': execution_time,
                'memory': 0
            })

        except subprocess.TimeoutExpired:
            try:
                Path(temp_input_path).unlink(missing_ok=True)
            except:
                pass
            results.append({
                'output': 'Time Limit Exceeded',
                'verdict': 'TLE',
                'time': time_limit_ms,
                'memory': 0
            })
            break  # Stop on first TLE
            
        except Exception as e:
            try:
                Path(temp_input_path).unlink(missing_ok=True)
            except:
                pass
            results.append({
                'output': f"Error: {str(e)}",
                'verdict': 'RTE',
                'time': 0,
                'memory': 0
            })
            break

    return results


def run_batch_python(code, test_cases, time_limit_ms):
    """Run Python code with all test cases efficiently"""
    results = []
    timeout_seconds = time_limit_ms / 1000.0
    
    # Create code file once
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_code:
        temp_code.write(code)
        temp_code_path = temp_code.name

    try:
        interpreter = "python" if platform.system() == "Windows" else "python3"
        
        for test_case in test_cases:
            start_time = time.time()
            
            try:
                # Create input file with preprocessed input for Python
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_input:
                    if test_case.input_data:
                        # Preprocess input for Python compatibility
                        processed_input = preprocess_input_for_python(test_case.input_data)
                        clean_input = processed_input.replace('\r\n', '\n').replace('\r', '\n')
                        temp_input.write(clean_input)
                        if not clean_input.endswith('\n'):
                            temp_input.write('\n')
                    temp_input_path = temp_input.name

                # Execute
                with open(temp_input_path, "r") as input_file:
                    result = subprocess.run(
                        [interpreter, temp_code_path], 
                        stdin=input_file,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True, 
                        timeout=timeout_seconds
                    )
                
                # Cleanup input file immediately
                Path(temp_input_path).unlink(missing_ok=True)
                
                end_time = time.time()
                execution_time = int((end_time - start_time) * 1000)

                if result.returncode == 0:
                    output = result.stdout.strip()
                    expected = test_case.expected_output.strip()
                    verdict = 'AC' if output == expected else 'WA'
                else:
                    output = f"Runtime Error: {result.stderr}"
                    verdict = 'RTE'

                results.append({
                    'output': output,
                    'verdict': verdict,
                    'time': execution_time,
                    'memory': 0
                })

            except subprocess.TimeoutExpired:
                try:
                    Path(temp_input_path).unlink(missing_ok=True)
                except:
                    pass
                results.append({
                    'output': 'Time Limit Exceeded',
                    'verdict': 'TLE',
                    'time': time_limit_ms,
                    'memory': 0
                })
                break
                
            except Exception as e:
                try:
                    Path(temp_input_path).unlink(missing_ok=True)
                except:
                    pass
                results.append({
                    'output': f"Error: {str(e)}",
                    'verdict': 'RTE',
                    'time': 0,
                    'memory': 0
                })
                break

    finally:
        # Cleanup code file
        try:
            Path(temp_code_path).unlink(missing_ok=True)
        except:
            pass

    return results


def bulk_create_ce_results(submission, test_cases, error_msg):
    """Create compilation error results for all test cases in bulk"""
    ce_results = [
        TestResult(
            submission=submission,
            test_case=test_case,
            user_output=error_msg,
            verdict='CE',
            execution_time=0,
            memory_used=0,
        )
        for test_case in test_cases
    ]
    
    with transaction.atomic():
        TestResult.objects.bulk_create(ce_results)
    
    submission.verdict = 'CE'
    submission.passed_tests = 0
    submission.execution_time = 0
    submission.memory_used = 0
    submission.save()


def cleanup_executable(executable_path):
    """Clean up compiled executable"""
    try:
        if executable_path and Path(executable_path).exists():
            Path(executable_path).unlink()
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


# Rest of the fallback functions remain the same...
def run_code(language, code, input_data, time_limit_ms):
    """Fallback run_code function for compatibility"""
    
    # Handle empty input
    if input_data is None:
        input_data = ""

    # Route to appropriate language handler
    if language in ['py', 'python']:
        return run_code_python(code, input_data, time_limit_ms)
    
    # For compiled languages (C/C++)
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]

    for directory in directories:
        dir_path = project_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    outputs_dir = project_path / "outputs"

    unique = str(uuid.uuid4())
    code_file_name = f"{unique}.{language}"
    input_file_name = f"{unique}.txt"
    output_file_name = f"{unique}.txt"

    code_file_path = codes_dir / code_file_name
    input_file_path = inputs_dir / input_file_name
    output_file_path = outputs_dir / output_file_name

    with open(code_file_path, "w") as code_file:
        code_file.write(code)
    
    with open(input_file_path, "w", newline='') as input_file:
        if input_data:
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

            compile_result = subprocess.run(
                [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
                capture_output=True, 
                text=True, 
                timeout=30
            )

            if compile_result.returncode != 0:
                return f"Compilation Error: {compile_result.stderr}"
            
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
                    return f"Runtime Error: {result.stderr}"

        elif language == "c":
            if platform.system() == "Windows":
                executable_name = f"{unique}.exe"
                compiler = "gcc"
            else:
                executable_name = unique
                compiler = "clang"

            executable_path = codes_dir / executable_name

            compile_result = subprocess.run(
                [compiler, "-O2", str(code_file_path), "-o", str(executable_path)], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if compile_result.returncode != 0:
                return f"Compilation Error: {compile_result.stderr}"
            
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
                    return f"Runtime Error: {result.stderr}"
        
        else:
            return f"Error: Unsupported language '{language}'"
                    
    except subprocess.TimeoutExpired:
        raise
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        for file_path in [code_file_path, input_file_path, output_file_path]:
            try:
                if file_path.exists():
                    file_path.unlink()
            except:
                pass

        if language in ["cpp", "c"]:
            try:
                executable_path = codes_dir / (unique + (".exe" if platform.system() == "Windows" else ""))
                if executable_path.exists():
                    executable_path.unlink()
            except:
                pass


def run_code_python(code, input_data, time_limit_ms):
    """Execute Python code efficiently"""
    project_path = Path(settings.BASE_DIR)
    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    
    for directory in [codes_dir, inputs_dir]:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
    
    unique = str(uuid.uuid4())
    code_file_path = codes_dir / f"{unique}.py"
    input_file_path = inputs_dir / f"{unique}.txt"
    
    try:
        with open(code_file_path, "w") as code_file:
            code_file.write(code)
        
        with open(input_file_path, "w", newline='') as input_file:
            if input_data:
                # Preprocess input for Python compatibility in fallback function too
                processed_input = preprocess_input_for_python(input_data)
                clean_input = processed_input.replace('\r\n', '\n').replace('\r', '\n')
                input_file.write(clean_input)
                if not clean_input.endswith('\n'):
                    input_file.write('\n')

        timeout_seconds = time_limit_ms / 1000.0
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
                return f"Runtime Error: {result.stderr}"
                
    except subprocess.TimeoutExpired:
        raise
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        for file_path in [code_file_path, input_file_path]:
            try:
                if file_path.exists():
                    file_path.unlink()
            except:
                pass
