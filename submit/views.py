# # from django.shortcuts import render, get_object_or_404, redirect
# # from django.http import HttpRequest
# # from submit.forms import CodeSubmissionForm
# # from django.conf import settings
# # from submit.models import Problem,TestCase, TestResult, CodeSubmission
# # import os
# # import uuid              #unique ID to each submission
# # import subprocess
# # from pathlib import Path
# # import platform
# # import difflib
# # import time
# # from django.contrib.auth.decorators import login_required
# # import psutil
# # import resource
# # import signal

# # # Create your views here.

# # def problem_list(request):
# #     problems=Problem.objects.all().order_by('-created_at')
# #     return render(request, 'problem_list.html', {'problems': problems})

# # def problem_detail(request, problem_id):
# #     problem=get_object_or_404(Problem, id=problem_id)
# #     return render(request, 'problem_detail.html', {'problem': problem})

# # # @login_required
# # # def submit_solution(request, problem_id):
# # #     problem=get_object_or_404(Problem, id=problem_id)

# # #     if request.method=='POST':
# # #         form=CodeSubmissionForm(request.POST)
# # #         if form.is_valid():
# # #             submission=form.save(commit=False)   #don't save in database for now
# # #             submission.user=request.user
# # #             submission.problem=problem
# # #             submission.save()

# # #             #judge the submission
# # #             judge_submission(submission)
# # #             return redirect('submission_result',submission_id=submission.id)
# # #         else:
# # #             form=CodeSubmissionForm()
        
# # #         return render(request, 'submit_solution.html', {'form':form, 'problem':problem})

# # @login_required
# # def submit_solution(request, problem_id):
# #     problem = get_object_or_404(Problem, id=problem_id)

# #     if request.method == 'POST':
# #         form = CodeSubmissionForm(request.POST)
# #         if form.is_valid():
# #             submission = form.save(commit=False)
# #             submission.user = request.user
# #             submission.problem = problem
# #             submission.save()

# #             # Judge the submission
# #             judge_submission(submission)
# #             return redirect('submission_result', submission_id=submission.id)
# #         # ✅ If form is invalid, DON'T create new form - keep the one with errors
# #         # Fall through to render statement below
# #     else:
# #         # ✅ GET request - create empty form
# #         form = CodeSubmissionForm()
    
# #     # This handles BOTH cases:
# #     # 1. GET requests (empty form)
# #     # 2. POST requests with invalid form (form with errors)
# #     return render(request, 'submit_solution.html', {
# #         'form': form, 
# #         'problem': problem
# #     })


# # def judge_submission(submission):
# #     test_cases=submission.problem.test_cases.all()
# #     total_tests=len(test_cases)
# #     passed_tests=0
# #     max_time=0
# #     # max_memory=0

# #     submission.total_tests=total_tests

# #     for test_case in test_cases:
# #         result=run_single_test(submission, test_case)

# #         TestResult.objects.create(

# #             submission=submission,
# #             test_case=test_case,
# #             user_output=result['output'],
# #             verdict=result['verdict'],
# #             execution_time=result['time'],
# #             # memory_used=result['memory'],

# #         )

# #         if result['verdict']=='AC':
# #             passed_tests+=1
# #         elif result['verdict'] in ['TLE','RTE','CE','MLE']:
# #             break

# #         max_time=max(max_time, result.get('time',0))
# #         # max_memory=max(max_memory,result.get('memory',0))
    
# #     if passed_tests==total_tests:
# #         submission.verdict=='AC'
# #     elif any(tr.verdict=='CE' for tr in submission.test_results.all()):
# #         submission.verdict='CE'
# #     elif any(tr.verdict=='TLE' for tr in submission.test_results.all()):
# #         submission.verdict='TLE'
# #     elif any(tr.verdict=='RTE' for tr in submission.test_results.all()):
# #         submission.verdict='RTE'
# #     elif any(tr.verdict=='MLE' for tr in submission.test_results.all()):
# #         submission.verdict='MLE'
# #     else:
# #         submission.verdict='WA'
    
# #     submission.passed_tests=passed_tests
# #     submission.execution_time=max_time
# #     submission.memory_used=max_memory
# #     submission.save()

# # # def run_single_test(submission, test_case):
# # #     try:
# # #         start_time=time.time()
# # #         output=run_code(submission.language, submission.code, test_case.input_data, submission.problem.time_limit, submission.problem.memory_limit)
# # #         end_time=time.time()
# # #         execution_time=int((end_time-start_time)*1000)  #into ms

# # #         if output.startswith('Error'):
# # #             return {
# # #                 'output':output, 'verdict':'CE'
# # #                 , 'time':0, 'memory':0,
# # #             }
        
# # #         user_output=output.strip()
# # #         expected_output=test_case.expected_output.strip()

# # #         if user_output==expected_output:
# # #             verdict='AC'
# # #         else:
# # #             verdict='WA'
# # #         return {
# # #             'output':output, 'verdict':verdict, 
# # #             'time':execution_time, 'memory':0
# # #         }
# # #     except subprocess.TimeoutExpired:
# # #         return {
# # #             'output':'', 'verdict':'TLE',
# # #             'time':submission.problem.time_limit,
# # #             'memory':0
# # #         }
# # #     except Exception as e:
# # #         return {
# # #             'output':str(e), 'verdict':'RTE',
# # #             'time':0, 'memory': 0,
# # #         }

# # def run_single_test(submission, test_case):
# #     try:
# #         start_time=time.time()
# #         result=run_code(submission.language, submission.code, test_case.input_data, submission.problem.time_limit, submission.problem.memory_limit)
# #         end_time=time.time()
# #         execution_time=int((end_time-start_time)*1000)  #into ms

# #         # Since we always return dict now, no need for isinstance check
# #         output = result['output']
# #         memory_used = result.get('memory', 0)
        
# #         if result.get('verdict') == 'MLE':
# #             return {
# #                 'output': output,
# #                 'verdict': 'MLE',
# #                 'time': execution_time,
# #                 'memory': memory_used
# #             }

# #         if output.startswith('Error'):
# #             return {
# #                 'output':output, 'verdict':'CE'
# #                 , 'time':0, 'memory':memory_used,
# #             }
        
# #         user_output=output.strip()
# #         expected_output=test_case.expected_output.strip()

# #         if user_output==expected_output:
# #             verdict='AC'
# #         else:
# #             verdict='WA'
# #         return {
# #             'output':output, 'verdict':verdict, 
# #             'time':execution_time, 'memory':memory_used
# #         }
# #     except subprocess.TimeoutExpired:
# #         return {
# #             'output':'', 'verdict':'TLE',
# #             'time':submission.problem.time_limit,
# #             'memory':0
# #         }
# #     except Exception as e:
# #         return {
# #             'output':str(e), 'verdict':'RTE',
# #             'time':0, 'memory': 0,
# #         }
# # # def submit(request):
# # #     if request.method=="POST":
# # #         form = CodeSubmissionForm(request.POST)   #get form data
# # #         if form.is_valid():
# # #             submission=form.save()       #save the form to database
# # #             print(submission.language)
# # #             print(submission.code)
# # #             output=run_code(submission.language, submission.code, submission.input_data)
# # #             submission.output_data=output
# # #             submission.save()
# # #             return render(request, "result.html", {"submission": submission})

# # #     else:
# # #         form=CodeSubmissionForm()         #creates empty form when user visits the page (GET request)
# # #     return render(request, "index.html", {"form": form})  #passing the form to template


# # def run_code(language,code, input_data, time_limit_ms, memory_limit_mb):
    
# #     #handle empty input
# #     if input_data is None:
# #         input_data=""

# #     project_path=Path(settings.BASE_DIR)  #project folder, we don't hardcode it since we need to deploy it later
# #     directories=["codes", "inputs", "outputs"]  #create these directories

# #     for directory in directories:
# #         dir_path = project_path/directory  #path of each directory
# #         if not dir_path.exists():
# #             dir_path.mkdir(parents=True, exist_ok=True)
    
# #     codes_dir=project_path/"codes"
# #     inputs_dir=project_path/"inputs"
# #     outputs_dir=project_path/"outputs"

# #     unique=str(uuid.uuid4())      #creates random strings to give uniques ID to all different submissions
# #     code_file_name=f"{unique}.{language}"
# #     input_file_name=f"{unique}.txt"
# #     output_file_name=f"{unique}.txt"     #input and output files have same name but different directories

# #     code_file_path=codes_dir/code_file_name
# #     input_file_path=inputs_dir/input_file_name
# #     output_file_path=outputs_dir/output_file_name

# #     with open(code_file_path,"w") as code_file:
# #         code_file.write(code)
    
# #     with open(input_file_path, "w") as input_file:
# #         '''
# #         It becomes a problem in python since it expects
# #         a newline at the end, until newline it reads so 
# #         it produces an EOF (end of file ) errors for 
# #         multiline  inputs. Generally not a problem in c, c++ since
# #         they don't care about the newline.
# #         '''
# #         if input_data:
# #             lines=input_data.strip().split('\n')
# #             for line in lines:
# #                 input_file.write(line.strip() + '\n')

# #     timeout_seconds=time_limit_ms/1000.0
# #     memory_limit_bytes=memory_limit_mb*1024*1024

# #     def set_memory_limit():
# #         if(platform.system()!='Windows'):
# #             resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))


# #     # with open(output_file_path, "w" ) as output_file:
# #     #     pass       #creates an empty output file

# #     try:
# #         if language=="cpp":
# #             if platform.system()=="Windows":   #Windows
# #                 executable_name=f"{unique}.exe"
# #                 compiler="g++"
# #             else:
# #                 executable_name=unique          #Mac and Linux.
# #                 compiler="clang++"

# #             executable_path=codes_dir/executable_name   #defined the path where the executable file will go, compiler will create it.


# #             #compile it
# #             compile_result=subprocess.run([compiler, str(code_file_path), "-o", str(executable_path)], capture_output=True, text=True, timeout=30)

# #             if compile_result.returncode != 0:
# #                 return f"Error: {compile_result.stderr}"
            
# #             with open(input_file_path, "r") as input_file:
# #                 result=subprocess.run([str(executable_path)], stdin=input_file,
# #                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
# #                                     text=True, timeout=timeout_seconds)
                
# #                 if result.returncode==0:
# #                     return result.stdout
# #                 else:
# #                     return f"Error: {result.stderr}"

# #         # if compile_result.returncode==0:
# #         #     with open(input_file_path, "r") as input_file:
# #         #         with open(output_file_path, "w") as output_file:
# #         #             subprocess.run([str(executable_path)], stdin=input_file, stdout=output_file)
    
# #         elif language=="py":
# #             #no need to compile
# #             # with open(input_file_path, "r") as input_file:
# #             #     with open(output_file_path, "w") as output_file:
# #             #         subprocess.run(["python", str(code_file_path)], stdin=input_file, stdout=output_file)

# #             if platform.system()=="Windows":
# #                 interpreter="python"
# #             else:
# #                 interpreter="python3"           #Mac and linux

# #             # with open(input_file_path, "r") as input_file:
# #             #     result=subprocess.run([interpreter, str(code_file_path)], stdin=input_file,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
# #             #     with open(output_file_path, "w") as output_file:
# #             #         if result.returncode==0:
# #             #             output_file.write(result.stdout)
# #             #         else:
# #             #             output_file.write(f"Error: {result.stderr}")

# #             with open(input_file_path, "r") as input_file:
# #                 result=subprocess.run([interpreter, str(code_file_path)], stdin=input_file,
# #                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
# #                                     text=True, timeout=timeout_seconds)
# #                 if result.returncode==0:
# #                     return result.stdout
# #                 else:
# #                     return f"Error: {result.stderr}"
        
# #         elif language=="c":
# #             if platform.system()=="Windows":
# #                 executable_name=f"{unique}.exe"
# #                 compiler="gcc"
# #             else:
# #                 executable_name=unique
# #                 compiler="clang"

# #             executable_path=codes_dir/executable_name

# #             #compile it
# #             compile_result=subprocess.run([compiler, str(code_file_path), "-o", str(executable_path)], capture_output=True, text=True, timeout=30)
# #             # if compile_result.returncode==0:
# #             #     with open(input_file_path, "r") as input_file:
# #             #         with open(output_file_path, "w") as output_file:
# #             #             subprocess.run([str(executable_path)], stdin=input_file, stdout=output_file)
# #             if compile_result.returncode != 0:
# #                 return f"Error: {compile_result.stderr}"
            
# #             with open(input_file_path, "r") as input_file:
# #                 result=subprocess.run([str(executable_path)], stdin=input_file, 
# #                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
# #                                     timeout=timeout_seconds)
                
# #                 if result.returncode==0:
# #                     return result.stdout
# #                 else:
# #                     return f"Error: {result.stderr}"
# #     except subprocess.TimeoutExpired:
# #         raise
# #     except Exception as e:
# #         return f"Error: {str(e)}"
# #     finally:
# #         for file_path in [code_file_path, input_file_path, output_file_path]:
# #             try:
# #                 if file_path.exists():
# #                     file_path.unlink()
# #             except:
# #                 pass

# #         if language in ["cpp", "c"]:
# #             try:
# #                 executable_path1=codes_dir/(unique+(".exe" if platform.system()=="Windows" else ""))
# #                 if executable_path1.exists():
# #                     executable_path1.unlink()
# #             except:
# #                 pass

# # def submission_result(request, submission_id):
# #     submission=get_object_or_404(CodeSubmission, id=submission_id)
# #     test_results=submission.test_results.all().order_by('id')
# #     return render(request, 'submission_result.html',
# #                   {
# #                     'submission':submission,
# #                     'test_results':test_results  
# #                   })


# # from django.shortcuts import render, get_object_or_404, redirect
# # from django.http import HttpRequest
# # from submit.forms import CodeSubmissionForm
# # from django.conf import settings
# # from submit.models import Problem,TestCase, TestResult, CodeSubmission
# # import os
# # import uuid              #unique ID to each submission
# # import subprocess
# # from pathlib import Path
# # import platform
# # import difflib
# # import time
# # from django.contrib.auth.decorators import login_required
# # import psutil


# # # Create your views here.


# # def problem_list(request):
# #     problems=Problem.objects.all().order_by('-created_at')
# #     return render(request, 'problem_list.html', {'problems': problems})


# # def problem_detail(request, problem_id):
# #     problem=get_object_or_404(Problem, id=problem_id)
# #     return render(request, 'problem_detail.html', {'problem': problem})


# # @login_required
# # def submit_solution(request, problem_id):
# #     problem = get_object_or_404(Problem, id=problem_id)

# #     if request.method == 'POST':
# #         form = CodeSubmissionForm(request.POST)
# #         if form.is_valid():
# #             submission = form.save(commit=False)
# #             submission.user = request.user
# #             submission.problem = problem
# #             submission.save()

# #             # Judge the submission
# #             judge_submission(submission)
# #             return redirect('submission_result', submission_id=submission.id)
# #         # If form is invalid, DON'T create new form - keep the one with errors
# #         # Fall through to render statement below
# #     else:
# #         # GET request - create empty form
# #         form = CodeSubmissionForm()
    
# #     # This handles BOTH cases:
# #     # 1. GET requests (empty form)  
# #     # 2. POST requests with invalid form (form with errors)
# #     return render(request, 'submit_solution.html', {
# #         'form': form, 
# #         'problem': problem
# #     })


# # def judge_submission(submission):
# #     test_cases=submission.problem.test_cases.all()
# #     total_tests=len(test_cases)
# #     passed_tests=0
# #     max_time=0
# #     max_memory=0

# #     submission.total_tests=total_tests

# #     for test_case in test_cases:
# #         result=run_single_test(submission, test_case)

# #         TestResult.objects.create(
# #             submission=submission,
# #             test_case=test_case,
# #             user_output=result['output'],
# #             verdict=result['verdict'],
# #             execution_time=result['time'],
# #             memory_used=result['memory'],
# #         )

# #         if result['verdict']=='AC':
# #             passed_tests+=1
# #         elif result['verdict'] in ['TLE','RTE','CE','MLE']:
# #             break

# #         max_time=max(max_time, result.get('time',0))
# #         max_memory=max(max_memory,result.get('memory',0))
    
# #     if passed_tests==total_tests:
# #         submission.verdict='AC'  # Fixed: was == instead of =
# #     elif any(tr.verdict=='CE' for tr in submission.test_results.all()):
# #         submission.verdict='CE'
# #     elif any(tr.verdict=='TLE' for tr in submission.test_results.all()):
# #         submission.verdict='TLE'
# #     elif any(tr.verdict=='RTE' for tr in submission.test_results.all()):
# #         submission.verdict='RTE'
# #     elif any(tr.verdict=='MLE' for tr in submission.test_results.all()):
# #         submission.verdict='MLE'
# #     else:
# #         submission.verdict='WA'
    
# #     submission.passed_tests=passed_tests
# #     submission.execution_time=max_time
# #     submission.memory_used=max_memory
# #     submission.save()


# # def run_single_test(submission, test_case):
# #     try:
# #         start_time=time.time()
# #         result=run_code(submission.language, submission.code, test_case.input_data, submission.problem.time_limit, submission.problem.memory_limit)
# #         end_time=time.time()
# #         execution_time=int((end_time-start_time)*1000)  #into ms

# #         # Since we always return dict now, no need for isinstance check
# #         output = result['output']
# #         memory_used = result.get('memory', 0)
        
# #         if result.get('verdict') == 'MLE':
# #             return {
# #                 'output': output,
# #                 'verdict': 'MLE',
# #                 'time': execution_time,
# #                 'memory': memory_used
# #             }

# #         if output.startswith('Error'):
# #             return {
# #                 'output':output, 'verdict':'CE'
# #                 , 'time':0, 'memory':memory_used,
# #             }
        
# #         user_output=output.strip()
# #         expected_output=test_case.expected_output.strip()

# #         if user_output==expected_output:
# #             verdict='AC'
# #         else:
# #             verdict='WA'
# #         return {
# #             'output':output, 'verdict':verdict, 
# #             'time':execution_time, 'memory':memory_used
# #         }
# #     except subprocess.TimeoutExpired:
# #         return {
# #             'output':'', 'verdict':'TLE',
# #             'time':submission.problem.time_limit,
# #             'memory':0
# #         }
# #     except Exception as e:
# #         return {
# #             'output':str(e), 'verdict':'RTE',
# #             'time':0, 'memory': 0,
# #         }


# # def run_code(language,code, input_data, time_limit_ms, memory_limit_mb):
    
# #     #handle empty input
# #     if input_data is None:
# #         input_data=""

# #     project_path=Path(settings.BASE_DIR)
# #     directories=["codes", "inputs", "outputs"]

# #     for directory in directories:
# #         dir_path = project_path/directory
# #         if not dir_path.exists():
# #             dir_path.mkdir(parents=True, exist_ok=True)
    
# #     codes_dir=project_path/"codes"
# #     inputs_dir=project_path/"inputs"
# #     outputs_dir=project_path/"outputs"

# #     unique=str(uuid.uuid4())
# #     code_file_name=f"{unique}.{language}"
# #     input_file_name=f"{unique}.txt"
# #     output_file_name=f"{unique}.txt"

# #     code_file_path=codes_dir/code_file_name
# #     input_file_path=inputs_dir/input_file_name
# #     output_file_path=outputs_dir/output_file_name

# #     with open(code_file_path,"w") as code_file:
# #         code_file.write(code)
    
# #     with open(input_file_path, "w") as input_file:
# #         if input_data:
# #             lines=input_data.strip().split('\n')
# #             for line in lines:
# #                 input_file.write(line.strip() + '\n')

# #     timeout_seconds=time_limit_ms/1000.0
# #     memory_limit_bytes=memory_limit_mb*1024*1024

# #     # Cross-platform memory monitoring function
# #     def run_with_memory_monitoring(cmd, stdin_file, timeout):
# #         try:
# #             with open(stdin_file, "r") as input_file:
# #                 process = subprocess.Popen(
# #                     cmd,
# #                     stdin=input_file,
# #                     stdout=subprocess.PIPE,
# #                     stderr=subprocess.PIPE,
# #                     text=True
# #                 )
                
# #                 # Monitor memory usage across all platforms
# #                 max_memory_used = 0
# #                 try:
# #                     ps_process = psutil.Process(process.pid)
# #                     start_time = time.time()
                    
# #                     while process.poll() is None:
# #                         try:
# #                             # Get memory usage - works on all platforms
# #                             memory_info = ps_process.memory_info()
# #                             current_memory = memory_info.rss  # Resident Set Size in bytes
# #                             max_memory_used = max(max_memory_used, current_memory)
                            
# #                             # Cross-platform memory limit check
# #                             if current_memory > memory_limit_bytes:
# #                                 process.terminate()
# #                                 try:
# #                                     process.wait(timeout=2)  # Give it 2 seconds to terminate gracefully
# #                                 except subprocess.TimeoutExpired:
# #                                     process.kill()  # Force kill if it doesn't terminate
# #                                 return {
# #                                     'output': '',
# #                                     'verdict': 'MLE',
# #                                     'memory': current_memory // (1024 * 1024)  # Convert to MB
# #                                 }
                            
# #                             # Check timeout
# #                             if time.time() - start_time > timeout:
# #                                 process.terminate()
# #                                 try:
# #                                     process.wait(timeout=2)
# #                                 except subprocess.TimeoutExpired:
# #                                     process.kill()
# #                                 raise subprocess.TimeoutExpired(cmd, timeout)
                                
# #                             time.sleep(0.01)  # Small delay to prevent excessive CPU usage
# #                         except psutil.NoSuchProcess:
# #                             break
                    
# #                     stdout, stderr = process.communicate(timeout=max(0.1, timeout - (time.time() - start_time)))
                    
# #                     return {
# #                         'output': stdout if process.returncode == 0 else f"Error: {stderr}",
# #                         'memory': max_memory_used // (1024 * 1024)  # Convert to MB
# #                     }
                        
# #                 except psutil.NoSuchProcess:
# #                     stdout, stderr = process.communicate()
# #                     return {
# #                         'output': stdout if process.returncode == 0 else f"Error: {stderr}",
# #                         'memory': max_memory_used // (1024 * 1024)
# #                     }
                        
# #         except subprocess.TimeoutExpired:
# #             # Make sure process is killed
# #             try:
# #                 process.terminate()
# #                 process.wait(timeout=2)
# #             except:
# #                 try:
# #                     process.kill()
# #                 except:
# #                     pass
# #             raise
# #         except Exception as e:
# #             return {
# #                 'output': f"Error: {str(e)}",
# #                 'memory': 0
# #             }

# #     try:
# #         if language=="cpp":
# #             if platform.system()=="Windows":
# #                 executable_name=f"{unique}.exe"
# #                 compiler="g++"
# #             else:
# #                 executable_name=unique
# #                 compiler="clang++"

# #             executable_path=codes_dir/executable_name

# #             #compile it
# #             compile_result=subprocess.run([compiler, str(code_file_path), "-o", str(executable_path)], capture_output=True, text=True, timeout=30)

# #             if compile_result.returncode != 0:
# #                 return {
# #                     'output': f"Error: {compile_result.stderr}",
# #                     'memory': 0
# #                 }
            
# #             # Run with memory monitoring
# #             return run_with_memory_monitoring([str(executable_path)], input_file_path, timeout_seconds)

# #         elif language=="py":
# #             if platform.system()=="Windows":
# #                 interpreter="python"
# #             else:
# #                 interpreter="python3"

# #             # Run with memory monitoring
# #             return run_with_memory_monitoring([interpreter, str(code_file_path)], input_file_path, timeout_seconds)
        
# #         elif language=="c":
# #             if platform.system()=="Windows":
# #                 executable_name=f"{unique}.exe"
# #                 compiler="gcc"
# #             else:
# #                 executable_name=unique
# #                 compiler="clang"

# #             executable_path=codes_dir/executable_name

# #             #compile it
# #             compile_result=subprocess.run([compiler, str(code_file_path), "-o", str(executable_path)], capture_output=True, text=True, timeout=30)
            
# #             if compile_result.returncode != 0:
# #                 return {
# #                     'output': f"Error: {compile_result.stderr}",
# #                     'memory': 0
# #                 }
            
# #             # Run with memory monitoring
# #             return run_with_memory_monitoring([str(executable_path)], input_file_path, timeout_seconds)
            
# #     except subprocess.TimeoutExpired:
# #         raise
# #     except Exception as e:
# #         return {
# #             'output': f"Error: {str(e)}",
# #             'memory': 0
# #         }
# #     finally:
# #         for file_path in [code_file_path, input_file_path, output_file_path]:
# #             try:
# #                 if file_path.exists():
# #                     file_path.unlink()
# #             except:
# #                 pass

# #         if language in ["cpp", "c"]:
# #             try:
# #                 executable_path1=codes_dir/(unique+(".exe" if platform.system()=="Windows" else ""))
# #                 if executable_path1.exists():
# #                     executable_path1.unlink()
# #             except:
# #                 pass


# # def submission_result(request, submission_id):
# #     submission=get_object_or_404(CodeSubmission, id=submission_id)
# #     test_results=submission.test_results.all().order_by('id')
# #     return render(request, 'submission_result.html',
# #                   {
# #                     'submission':submission,
# #                     'test_results':test_results  
# #                   })


# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpRequest
# from submit.forms import CodeSubmissionForm
# from django.conf import settings
# from submit.models import Problem,TestCase, TestResult, CodeSubmission
# import os
# import uuid              #unique ID to each submission
# import subprocess
# from pathlib import Path
# import platform
# import difflib
# import time
# from django.contrib.auth.decorators import login_required


# # Create your views here.


# def problem_list(request):
#     problems=Problem.objects.all().order_by('-created_at')
#     return render(request, 'problem_list.html', {'problems': problems})


# def problem_detail(request, problem_id):
#     problem=get_object_or_404(Problem, id=problem_id)
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
#         # ✅ If form is invalid, DON'T create new form - keep the one with errors
#         # Fall through to render statement below
#     else:
#         # ✅ GET request - create empty form
#         form = CodeSubmissionForm()
    
#     # This handles BOTH cases:
#     # 1. GET requests (empty form)
#     # 2. POST requests with invalid form (form with errors)
#     return render(request, 'submit_solution.html', {
#         'form': form, 
#         'problem': problem
#     })



# def judge_submission(submission):
#     test_cases=submission.problem.test_cases.all()
#     total_tests=len(test_cases)
#     passed_tests=0
#     max_time=0


#     submission.total_tests=total_tests


#     for test_case in test_cases:
#         result=run_single_test(submission, test_case)


#         TestResult.objects.create(


#             submission=submission,
#             test_case=test_case,
#             user_output=result['output'],
#             verdict=result['verdict'],
#             execution_time=result['time'],


#         )


#         if result['verdict']=='AC':
#             passed_tests+=1
#         elif result['verdict'] in ['TLE','RTE','CE']:
#             break


#         max_time=max(max_time, result.get('time',0))
    
#     if passed_tests==total_tests:
#         submission.verdict='AC'
#     elif any(tr.verdict=='CE' for tr in submission.test_results.all()):
#         submission.verdict='CE'
#     elif any(tr.verdict=='TLE' for tr in submission.test_results.all()):
#         submission.verdict='TLE'
#     elif any(tr.verdict=='RTE' for tr in submission.test_results.all()):
#         submission.verdict='RTE'
#     else:
#         submission.verdict='WA'
    
#     submission.passed_tests=passed_tests
#     submission.execution_time=max_time
#     submission.save()


# def run_single_test(submission, test_case):
#     try:
#         start_time=time.time()
#         output=run_code(submission.language, submission.code, test_case.input_data, submission.problem.time_limit)
#         end_time=time.time()
#         execution_time=int((end_time-start_time)*1000)  #into ms


#         if output.startswith('Error'):
#             return {
#                 'output':output, 'verdict':'CE'
#                 , 'time':0, 'memory':0,
#             }
        
#         user_output=output.strip()
#         expected_output=test_case.expected_output.strip()


#         if user_output==expected_output:
#             verdict='AC'
#         else:
#             verdict='WA'
#         return {
#             'output':output, 'verdict':verdict, 
#             'time':execution_time, 'memory':0
#         }
#     except subprocess.TimeoutExpired:
#         return {
#             'output':'', 'verdict':'TLE',
#             'time':submission.problem.time_limit,
#             'memory':0
#         }
#     except Exception as e:
#         return {
#             'output':str(e), 'verdict':'RTE',
#             'time':0, 'memory': 0,
#         }


# def run_code(language,code, input_data, time_limit_ms):
    
#     #handle empty input
#     if input_data is None:
#         input_data=""


#     project_path=Path(settings.BASE_DIR)  #project folder, we don't hardcode it since we need to deploy it later
#     directories=["codes", "inputs", "outputs"]  #create these directories


#     for directory in directories:
#         dir_path = project_path/directory  #path of each directory
#         if not dir_path.exists():
#             dir_path.mkdir(parents=True, exist_ok=True)
    
#     codes_dir=project_path/"codes"
#     inputs_dir=project_path/"inputs"
#     outputs_dir=project_path/"outputs"


#     unique=str(uuid.uuid4())      #creates random strings to give uniques ID to all different submissions
#     code_file_name=f"{unique}.{language}"
#     input_file_name=f"{unique}.txt"
#     output_file_name=f"{unique}.txt"     #input and output files have same name but different directories


#     code_file_path=codes_dir/code_file_name
#     input_file_path=inputs_dir/input_file_name
#     output_file_path=outputs_dir/output_file_name


#     with open(code_file_path,"w") as code_file:
#         code_file.write(code)
    
#     with open(input_file_path, "w") as input_file:
#         '''
#         It becomes a problem in python since it expects
#         a newline at the end, until newline it reads so 
#         it produces an EOF (end of file ) errors for 
#         multiline  inputs. Generally not a problem in c, c++ since
#         they don't care about the newline.
#         '''
#         if input_data:
#             lines=input_data.strip().split('\n')
#             for line in lines:
#                 input_file.write(line.strip() + '\n')


#     timeout_seconds=time_limit_ms/1000.0


#     try:
#         if language=="cpp":
#             if platform.system()=="Windows":   #Windows
#                 executable_name=f"{unique}.exe"
#                 compiler="g++"
#             else:
#                 executable_name=unique          #Mac and Linux.
#                 compiler="clang++"


#             executable_path=codes_dir/executable_name   #defined the path where the executable file will go, compiler will create it.



#             #compile it
#             compile_result=subprocess.run([compiler, str(code_file_path), "-o", str(executable_path)], capture_output=True, text=True, timeout=30)


#             if compile_result.returncode != 0:
#                 return f"Error: {compile_result.stderr}"
            
#             with open(input_file_path, "r") as input_file:
#                 result=subprocess.run([str(executable_path)], stdin=input_file,
#                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#                                     text=True, timeout=timeout_seconds)
                
#                 if result.returncode==0:
#                     return result.stdout
#                 else:
#                     return f"Error: {result.stderr}"

    
#         elif language=="py":
#             if platform.system()=="Windows":
#                 interpreter="python"
#             else:
#                 interpreter="python3"           #Mac and linux


#             with open(input_file_path, "r") as input_file:
#                 result=subprocess.run([interpreter, str(code_file_path)], stdin=input_file,
#                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
#                                     text=True, timeout=timeout_seconds)
#                 if result.returncode==0:
#                     return result.stdout
#                 else:
#                     return f"Error: {result.stderr}"
        
#         elif language=="c":
#             if platform.system()=="Windows":
#                 executable_name=f"{unique}.exe"
#                 compiler="gcc"
#             else:
#                 executable_name=unique
#                 compiler="clang"


#             executable_path=codes_dir/executable_name


#             #compile it
#             compile_result=subprocess.run([compiler, str(code_file_path), "-o", str(executable_path)], capture_output=True, text=True, timeout=30)
#             if compile_result.returncode != 0:
#                 return f"Error: {compile_result.stderr}"
            
#             with open(input_file_path, "r") as input_file:
#                 result=subprocess.run([str(executable_path)], stdin=input_file, 
#                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
#                                     timeout=timeout_seconds)
                
#                 if result.returncode==0:
#                     return result.stdout
#                 else:
#                     return f"Error: {result.stderr}"
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
#                 executable_path1=codes_dir/(unique+(".exe" if platform.system()=="Windows" else ""))
#                 if executable_path1.exists():
#                     executable_path1.unlink()
#             except:
#                 pass


# def submission_result(request, submission_id):
#     submission=get_object_or_404(CodeSubmission, id=submission_id)
#     test_results=submission.test_results.all().order_by('id')
#     return render(request, 'submission_result.html',
#                   {
#                     'submission':submission,
#                     'test_results':test_results  
#                   })


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


@login_required
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
