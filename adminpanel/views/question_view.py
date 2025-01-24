from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from adminpanel.models.question import Question
from adminpanel.models.common_question import CommonQuestion
from adminpanel.models.course import Course
from adminpanel.models.institute import Institute
from adminpanel.helpers import save_data, base64_encode, base64_decode
from django.core.exceptions import ValidationError
from django.utils import timezone


@login_required
def common_questions(request):
    try:
        questions = CommonQuestion.active_objects.all()
        question_data = [
            {
                'question': question.question,
                'answer': question.answer,
                'encoded_id': base64_encode(question.id)
            }
            for question in questions
        ]

        return render(request, 'common_question/common_question.html', {'questions': question_data})

    except Exception as e:
        messages.error(request, f"An error occurred while fetching the questions: {e}")
        return redirect('admindashboard') 

@login_required
def common_question_add(request):

    courses = Course.objects.filter(deleted_at__isnull=True)
    errors = {}
    if request.method == 'POST':
        data = request.POST
        question = data.get('question')
        answer = data.get('answer')

        if not question:
            errors['question'] = "Question is required."

        if errors:
            return render(request, 'common_question/common_question_add.html', {'errors': errors})
        try:
            data_to_save = {
                'question': question,
                'answer': answer,
            }

            result = save_data(CommonQuestion, data_to_save)

            if result['status']:
                messages.success(request, "Question added successfully!")
                return redirect('common_questions')
            else:
                messages.error(request, "Failed to save the question. Please try again.")
                return render(request, 'common_question/common_question_add.html')

        except IntegrityError as e:
            messages.error(request, "A database error occurred. Please try again later.")
            return render(request, 'common_question/common_question_add.html')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'common_question/common_question_add.html')


    
    return render(request, 'common_question/common_question_add.html')


@login_required
def common_question_update(request, id):
    id = base64_decode(id)

    errors = {}

    if not id:
        return HttpResponse("Invalid ID", status=400)

    question = get_object_or_404(CommonQuestion, id=id)

    if request.method == 'POST':
        question = request.POST.get('question')
        answer = request.POST.get('answer')

        if not question:
            errors['question'] = "Question is required."

        if errors:
            question = get_object_or_404(CommonQuestion, id=id)
            return render(request, 'common_question/common_question_update.html', {'question': question, 'errors': errors})

        try:
            data = {
                'question': question,
                'answer': answer,
            }

            result = save_data(CommonQuestion, data, where={'id': id})

            if result['status']:
                messages.success(request, "Question updated successfully!")
                return redirect('common_questions')
            else:
                messages.error(request, result.get('error', "Failed to update the question."))
                return render(request, 'common_question/common_question_update.html', {'question': question })

        except Exception as e:
            messages.error(request, f"An error occurred while updating the question: {e}")
            return render(request, 'common_question/common_question_update.html', {'question': question })

    return render(request, 'common_question/common_question_update.html', {'question': question })


@login_required
def common_question_delete(request, id):
    id = base64_decode(id)

    if not id:
        return HttpResponse("Invalid or tampered ID", status=400)

    try:
        question = get_object_or_404(CommonQuestion, id=id)

        if question.deleted_at is not None:
            messages.warning(request, "Question is already soft deleted.")
        else:
            # Perform the soft delete
            question.deleted_at = timezone.now()
            question.soft_delete()
            messages.success(request, "Question deleted successfully!")

    except Exception as e:
        messages.error(request, f"An error occurred while deleting the question: {e}")

    return redirect('common_questions')


@login_required
def questions(request):
    try:
        questions = Question.active_objects.all()
        question_data = [
            {
                'question': question.question,
                'answer': question.answer,
                'course_id': question.course_id,
                'encoded_id': base64_encode(question.id)
            }
            for question in questions
        ]

        return render(request, 'question/question.html', {'questions': question_data})

    except Exception as e:
        messages.error(request, f"An error occurred while fetching the courses: {e}")
        return redirect('admindashboard') 

@login_required
def question_add(request):

    courses = Course.objects.filter(deleted_at__isnull=True)
    errors = {}
    if request.method == 'POST':
        data = request.POST
        question = data.get('question')
        course_id = data.get('course_id')

        if not question:
            errors['question'] = "Question is required."
        if not course_id:
            errors['course_id'] = "Course is required."

        if errors:
            return render(request, 'question/question_add.html', {'courses': courses, 'errors': errors})
        try:
            course = Course.objects.get(id=course_id)
            data_to_save = {
                'question': question,
                'course_id': course,
            }

            result = save_data(Question, data_to_save)

            if result['status']:
                messages.success(request, "Question added successfully!")
                return redirect('questions')
            else:
                messages.error(request, "Failed to save the question. Please try again.")
                return render(request, 'question/question_add.html', {'courses': courses})

        except IntegrityError as e:
            messages.error(request, "A database error occurred. Please try again later.")
            return render(request, 'question/question_add.html', {'courses': courses})

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'question/question_add.html', {'courses': courses})


    
    return render(request, 'question/question_add.html', {'courses': courses})


@login_required
def question_update(request, id):
    id = base64_decode(id)

    courses = Course.objects.filter(deleted_at__isnull=True)
    errors = {}

    if not id:
        return HttpResponse("Invalid ID", status=400)

    question = get_object_or_404(Question, id=id)

    if request.method == 'POST':
        question = request.POST.get('question')
        course_id = request.POST.get('course_id')

        if not question:
            errors['question'] = "Question is required."
        if not course_id:
            errors['course_id'] = "Course is required."

        if errors:
            question = get_object_or_404(Question, id=id)
            return render(request, 'question/question_update.html', {'question': question, 'courses': courses, 'errors': errors})

        try:
            course = Course.objects.get(id=course_id)
            data = {
                'question': question,
                'course_id': course,
            }

            result = save_data(Question, data, where={'id': id})

            if result['status']:
                messages.success(request, "Question updated successfully!")
                return redirect('questions')
            else:
                messages.error(request, result.get('error', "Failed to update the question."))
                return render(request, 'question/question_update.html', {'question': question, 'courses': courses })

        except Exception as e:
            messages.error(request, f"An error occurred while updating the question: {e}")
            return render(request, 'question/question_update.html', {'question': question, 'courses': courses })

    return render(request, 'question/question_update.html', {'question': question, 'courses': courses })


@login_required
def question_delete(request, id):
    id = base64_decode(id)

    if not id:
        return HttpResponse("Invalid or tampered ID", status=400)

    try:
        question = get_object_or_404(Question, id=id)

        if question.deleted_at is not None:
            messages.warning(request, "Question is already soft deleted.")
        else:
            # Perform the soft delete
            question.deleted_at = timezone.now()
            question.soft_delete()
            messages.success(request, "Question deleted successfully!")

    except Exception as e:
        messages.error(request, f"An error occurred while deleting the question: {e}")

    return redirect('questions')
