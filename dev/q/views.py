from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse , HttpResponseForbidden
import re

# @login_required
# def create_quiz(request):
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         question_texts = request.POST.getlist('question_text')
#         option1s = request.POST.getlist('option1')
#         option2s = request.POST.getlist('option2')
#         option3s = request.POST.getlist('option3')
#         option4s = request.POST.getlist('option4')
#         correct_options = request.POST.getlist('correct_option')
        
#         quiz = Quiz.objects.create(title=title, host=request.user)
        
#         for i in range(len(question_texts)):
#             question_text = question_texts[i]
#             option1 = option1s[i]
#             option2 = option2s[i]
#             option3 = option3s[i]
#             option4 = option4s[i]

#             # Safeguard against index errors
#             correct_option = correct_options[i] if i < len(correct_options) else None

#             # Check if all fields are filled correctly
#             if correct_option:
#                 Question.objects.create(
#                     quiz=quiz,
#                     question_text=question_text,
#                     option1=option1,
#                     option2=option2,
#                     option3=option3,
#                     option4=option4,
#                     correct_option=correct_option
#                 )
#             else:
#                 # Handle cases where a correct option isn't provided
#                 print(f"Question {i+1} does not have a correct option selected.")
        
#         return redirect('quiz_detail', quiz_id=quiz.id)

#     return render(request, 'quiz-v2.html')

    #     return redirect('dashboard')

    # return render(request, 'quiz/create_quiz.html')


@login_required
def create_quiz(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        questions = request.POST.getlist('questions')
        options = request.POST.getlist('options')
        correct_options = request.POST.getlist('correct_options')
        quiz = Quiz.objects.create(title=title, host=request.user)
        
        for i in range(len(questions)):
            Question.objects.create(
                quiz=quiz,
                question_text=questions[i],
                option1=options[i*4],
                option2=options[i*4 + 1],
                option3=options[i*4 + 2],
                option4=options[i*4 + 3],
                correct_option=correct_options[i]
            )
        
        return redirect('quiz_detail', quiz_id=quiz.id)

    return render(request, 'quiz-v2.html')

# def join_quiz(request, code):
#     quiz = get_object_or_404(Quiz, code=code)
    
#     if request.method == 'POST':
#         user_answers = request.POST.getlist('answers')
#         score = 0
#         for i, question in enumerate(quiz.questions.all()):
#             if question.correct_option == user_answers[i]:
#                 score += 1
        
#         QuizResult.objects.create(quiz=quiz, user=request.user, score=score)
        
#         return redirect('quiz_result', quiz_id=quiz.id)
    
#     return render(request, 'join_quiz.html', {'quiz': quiz})

# @login_required
# def join_quiz(request, code):
#     quiz = get_object_or_404(Quiz, code=code)
#     questions = quiz.questions.all()

#     if request.method == 'POST':
#         score = 0
#         for question in questions:
#             selected_option = request.POST.get(str(question.id))  # Get selected option for this question
#             if selected_option and selected_option == question.correct_option:
#                 score += 1

#         # Save the score to the database, or pass it to the template
#         # For simplicity, we're just returning the score here
#         return render(request, 'quiz_result.html', {'quiz': quiz.id, 'score': score})

#     return render(request, 'join_quiz.html', {'quiz': quiz, 'questions': questions})


# @login_required
# def join_quiz(request, code):
    # quiz = get_object_or_404(Quiz, code=code)
    
    # if request.method == 'POST':
    #     # user_answers = request.POST.getlist('answers')
    #     user_answer = request.POST.get(f'answers_{question.id}')
    #     score = 0
        
    #     # Make sure the length of user answers matches the number of questions
    #     questions = quiz.questions.all()
        
    #     for i, question in enumerate(questions):
    #         try:
    #             if question.correct_option == user_answers[i]:
    #                 score += 1
    #         except IndexError:
    #             # Handle the case where there are fewer answers than questions
    #             continue
        
    #     # Store the quiz result for the user
    #     QuizResult.objects.create(quiz=quiz, user=request.user, score=score)
        
    #     return redirect('quiz_result', quiz_id=quiz.id)
    
    # return render(request, 'join_quiz.html', {'quiz': quiz})

@login_required
def join_quiz(request, code):
    quiz = get_object_or_404(Quiz, code=code)
    
    if request.method == 'POST':
        score = 0
        
        questions = quiz.questions.all()
        total_questions = questions.count() 
        
        for question in questions:
            user_answer = request.POST.get(f'answers_{question.id}')
            
            if user_answer and user_answer == question.correct_option:
                score += 1
        
        # Store the quiz result for the user
        QuizResult.objects.create(quiz=quiz, user=request.user, score=score)

        request.session['score'] = score
        request.session['total_questions'] = total_questions
        
        return redirect('quiz_result', quiz_id=quiz.id)
    
    return render(request, 'join_quiz.html', {'quiz': quiz})

@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # results = quiz.results.all()

    # score = request.session.pop('score', None)
    score = request.session.get('score')
    total = request.session.get('total_questions')

    return render(request, 'result.html', {'quiz': quiz, 'score': score, 'total': total})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    results = quiz.results.all()
    return render(request, 'quiz_detail_v2.html', {'quiz': quiz , 'results': results})

@login_required
def view_quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Ensure that only the quiz creator can view the results
    if request.user != quiz.host:
        return HttpResponseForbidden("You are not allowed to view these results.")
    
    results = quiz.results.all().order_by('-score', 'submitted_at')
    
    return render(request, 'view_quiz_results.html', {'quiz': quiz, 'results': results})

# @login_required
# def join_room(request):
#     return render(request, 'room.html')


# def join_room(request):
#     if request.method == 'POST':
#         room_code = request.POST.get('room_code')
#         if room_code:
#             # Check if the room code exists in the QuizRoom model
#             if Quiz.objects.filter(code=room_code).exists():
#                 return redirect('join_quiz', code=room_code)
#             else:
#                 # If the room code does not exist, show an error
#                 return render(request, 'room.html', {'error': 'Room not found.'})
#     return render(request, 'room.html')

@login_required
def join_room(request):
    if request.method == 'POST':
        room_code = request.POST.get('room_code')
        if room_code:
            # Validate that the room code contains only digits
            if not re.match(r'^\d+$', room_code):
                return render(request, 'room.html', {'error': 'Invalid room code. Only numbers are allowed.'})

            # Check if the room code exists in the Quiz model
            if Quiz.objects.filter(code=room_code).exists():
                return redirect('join_quiz', code=room_code)
            else:
                # If the room code does not exist, show an error
                return render(request, 'room.html', {'error': 'Room not found.'})
    return render(request, 'room.html')

@login_required
def delete_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == "POST":
        quiz.delete()
        return redirect('teacher_home') 
    return render(request, 'delete_confirm.html', {'object': quiz, 'type': 'quiz'})

@login_required
def quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    results = quiz.results.all()
    return render(request, 'view.html', {'quiz': quiz , 'results': results})