
from adminpanel.common_imports import *


def common_questions(request):
    try:
        questions = CommonQuestion.active_objects.all()
        question_data = [
            {
                'question': question.question,
                'crm_id': question.crm_id,
                'encoded_id': base64_encode(question.id)
            }
            for question in questions
        ]

        breadcrumb_items = [
            {"name": "Dashboard", "url": reverse('admindashboard')},
            {"name": "Common Questions", "url": ""},
        ]
        data = {
            'questions': question_data,
            "show_breadcrumb": True,
            "breadcrumb_items": breadcrumb_items,
        }

        return render(request, 'common_question/common_question.html', data)

    except Exception as e:
        messages.error(request, f"An error occurred while fetching the questions: {e}")
        return redirect('admindashboard') 

def common_question_add(request):

    institutes = Institute.objects.filter(deleted_at__isnull=True)
    errors = {}

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Common Questions", "url": reverse('common_questions')},
        {"name": "Common Question Add", "url": ""},
    ]

    if request.method == 'POST':
        data = request.POST
        question = data.get('question')
        crm_id = data.get('crm_id')

        if not crm_id:
            errors['crm_id'] = "Institute is required."
        if not question:
            errors['question'] = "Question is required." 
        else:
            if CommonQuestion.objects.filter(question=question).exists():
                errors['question'] = "Question must be unique."

        if errors:
            return render(request, 'common_question/common_question_add.html', {'errors': errors, 'institutes': institutes, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items, })
        try:
            institute = Institute.objects.get(id=crm_id)
            data_to_save = {
                'question': question,
                'crm_id': institute,
            }

            result = save_data(CommonQuestion, data_to_save)

            if result['status']:
                messages.success(request, "Question added successfully!")
                return redirect('common_questions')
            else:
                messages.error(request, "Failed to save the question. Please try again.")
                return render(request, 'common_question/common_question_add.html', { 'institutes': institutes, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items, })

        except IntegrityError as e:
            messages.error(request, "A database error occurred. Please try again later.")
            return render(request, 'common_question/common_question_add.html', { 'institutes': institutes, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items, })

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'common_question/common_question_add.html', { 'institutes': institutes, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items, })


    data = { 
        'institutes': institutes,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    }
    
    return render(request, 'common_question/common_question_add.html', data)


def common_question_update(request, id):
    id = base64_decode(id)

    institutes = Institute.objects.filter(deleted_at__isnull=True)
    errors = {}

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Common Questions", "url": reverse('common_questions')},
        {"name": "Common Question Add", "url": ""},
    ]

    if not id:
        return HttpResponse("Invalid ID", status=400)

    question = get_object_or_404(CommonQuestion, id=id)

    if request.method == 'POST':
        question = request.POST.get('question')
        crm_id = request.POST.get('crm_id')

        if not crm_id:
            errors['crm_id'] = "Institute is required."
        if not question:
            errors['question'] = "Question is required."
        else:
            if CommonQuestion.objects.filter(question=question).exclude(id=id).exists():
                errors['question'] = "Question must be unique."

        if errors:
            question = get_object_or_404(CommonQuestion, id=id)
            return render(request, 'common_question/common_question_update.html', {'question': question, 'institutes': institutes, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items, 'errors': errors})

        try:
            institute = Institute.objects.get(id=crm_id)
            data = {
                'question': question,
                'crm_id': institute
            }

            result = save_data(CommonQuestion, data, where={'id': id})

            if result['status']:
                messages.success(request, "Question updated successfully!")
                return redirect('common_questions')
            else:
                messages.error(request, result.get('error', "Failed to update the question."))
                return render(request, 'common_question/common_question_update.html', {'question': question, 'institutes': institutes, "show_breadcrumb": True,"breadcrumb_items": breadcrumb_items, })

        except Exception as e:
            messages.error(request, f"An error occurred while updating the question: {e}")
            return render(request, 'common_question/common_question_update.html', {'question': question, 'institutes': institutes, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items, })

    data = {
        'question': question,
        'institutes': institutes,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    }

    return render(request, 'common_question/common_question_update.html', data)


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


def questions(request):
    try:
        questions = Question.active_objects.all()
        question_data = [
            {
                'question': question.question,
                'course_id': question.course_id,
                'encoded_id': base64_encode(question.id)
            }
            for question in questions
        ]

        breadcrumb_items = [
            {"name": "Dashboard", "url": reverse('admindashboard')},
            {"name": "Customized Questions", "url": ""},
        ]
        data = {
            'questions': question_data,
            "show_breadcrumb": True,
            "breadcrumb_items": breadcrumb_items,
        }

        return render(request, 'question/question.html', data)

    except Exception as e:
        messages.error(request, f"An error occurred while fetching the courses: {e}")
        return redirect('admindashboard') 

def question_add(request):

    courses = Course.objects.filter(deleted_at__isnull=True)
    errors = {}

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Customized Questions", "url": reverse('questions')},
        {"name": "Customized Question Add", "url": ""},
    ]

    if request.method == 'POST':
        data = request.POST
        question = data.get('question')
        course_id = data.get('course_id')

        if not question:
            errors['question'] = "Question is required."
        if not course_id:
            errors['course_id'] = "Course is required."

        if errors:
            return render(request, 'question/question_add.html', {'courses': courses, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items, 'errors': errors})
        try:
            course = Course.objects.get(id=course_id)

            # Check if the question already exists for the same course
            if Question.objects.filter(question=question, course_id=course).exists():
                messages.error(request, "This question is already assigned to the selected course.")
                return render(request, 'course/course_add.html', {'courses': courses, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items,})
            
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
                return render(request, 'question/question_add.html', {'courses': courses, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items,})

        except IntegrityError as e:
            messages.error(request, "A database error occurred. Please try again later.")
            return render(request, 'question/question_add.html', {'courses': courses, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items,})

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'question/question_add.html', {'courses': courses, "show_breadcrumb": True, "breadcrumb_items": breadcrumb_items,})

    data = {
        'courses': courses,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    }
    
    return render(request, 'question/question_add.html', data)


def question_update(request, id):
    id = base64_decode(id)

    courses = Course.objects.filter(deleted_at__isnull=True)
    errors = {}

    if not id:
        return HttpResponse("Invalid ID", status=400)

    questions = get_object_or_404(Question, id=id)

    if request.method == 'POST':
        question = request.POST.get('question')
        course_id = request.POST.get('course_id')

        if not question:
            errors['question'] = "Question is required."
        if not course_id:
            errors['course_id'] = "Course is required."

        if errors:
            questions = get_object_or_404(Question, id=id)
            return render(request, 'question/question_update.html', {'question': questions, 'courses': courses, 'errors': errors})

        try:
            course = Course.objects.get(id=course_id)

            # Check if the updated question is already assigned to this course (excluding the current course)
            if Question.objects.filter(question=question, course_id=course).exclude(id=id).exists():
                messages.error(request, "This question is already assigned to the selected course.")
                return render(request, 'question/question_update.html', {'question': questions, 'courses': courses })
                
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
                return render(request, 'question/question_update.html', {'question': questions, 'courses': courses })

        except Exception as e:
            messages.error(request, f"An error occurred while updating the question: {e}")
            return render(request, 'question/question_update.html', {'question': questions, 'courses': courses })

    breadcrumb_items = [
        {"name": "Dashboard", "url": reverse('admindashboard')},
        {"name": "Customized Questions", "url": reverse('questions')},
        {"name": "Customized Question Update", "url": ""},
    ]

    data = {
        'question': questions, 
        'courses': courses,
        "show_breadcrumb": True,
        "breadcrumb_items": breadcrumb_items,
    }

    return render(request, 'question/question_update.html', data)


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
