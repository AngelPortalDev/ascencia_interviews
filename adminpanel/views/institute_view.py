from django.shortcuts import render, redirect
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from adminpanel.models.institute import Institute
from django.http import Http404
from adminpanel.helpers import save_data, base64_encode, base64_decode
from django.core.exceptions import ValidationError
from django.utils import timezone


@login_required
def institute_list(request):
    institutes = Institute.objects.filter(deleted_at__isnull=True)
    institute_data = [{
        'institute_id': institute.institute_id,
        'institute_name': institute.institute_name,
        'encoded_id': base64_encode(institute.id)
    } for institute in institutes]

    return render(request, 'institute/institute.html', {'institutes': institute_data})



@login_required
def institute_add(request):
    if request.method == 'POST':
        data = request.POST
        institute_name = data.get('institute_name')
        institute_id = data.get('institute_id')

        try:
            data_to_save = {
                'institute_name': institute_name,
                'institute_id': institute_id,
            }

            result = save_data(Institute, data_to_save)

            if result['status']:
                return redirect('institute_list')
            else:
                return render(request, 'institute/institute_add.html', {'error_message': 'Failed to save the institute. Please try again.'})

        except IntegrityError as e:
            # Handle IntegrityError if needed
            print(f"IntegrityError: {e}")
            return render(request, 'institute/institute_add.html', {'error_message': 'Database error occurred, please try again later.'})

        except Exception as e:
            # Catch any other errors and show a generic error message
            print(f"Error: {e}")
            return render(request, 'institute/institute_add.html', {'error_message': 'An error occurred, please try again.'})

    queryset = Institute.objects.all()
    context = {'institutes': queryset}
    return render(request, 'institute/institute_add.html', context)


@login_required
def institute_update(request, id):
    id = base64_decode(id)

    if not id:
        return HttpResponse("Invalid or tampered ID", status=400)

    try:
        # Get the recipe by ID
        institute = Institute.objects.get(id=id)
    except Institute.DoesNotExist as e:
        # If the recipe is not found, raise 404
        raise Http404("Institute not found") from e

    if request.method == 'POST':
        try:
            institute_name = request.POST.get('institute_name')
            institute_id = request.POST.get('institute_id')

            if not institute_name or not institute_id:
                raise ValidationError("Institute Name and Institute Id are required.")

            # Prepare the data to be saved
            data = {
                'institute_name': institute_name,
                'institute_id': institute_id,
            }

            result = save_data(Institute, data, where={'id': id})

            if result['status']:
                return redirect('institute_list')
            else:
                raise Exception(result['error'])

        except ValidationError as e:
            context = {'error': str(e), 'institute': institute}
            return render(request, 'institute/institute_update.html', context)

        except Exception as e:
            context = {'error': 'Something went wrong. Please try again later.', 'institute': institute}
            return render(request, 'institute/institute_update.html', context)
    context = {'institute': institute}
    return render(request, 'institute/institute_update.html', context)


def institute_delete(request, id):

    id = base64_decode(id)
    print(id)

    if not id:
        return HttpResponse("Invalid or tampered ID", status=400)
    try:
        institute = Institute.objects.get(id=id)
        
        if institute.is_deleted:
            messages.error(request, "Institute is already soft deleted.")
        else:
            # Perform the soft delete by calling soft_delete method
            print("Soft delete")
            institute.soft_delete()
            messages.success(request, "Institute deleted successfully.")

    except Institute.DoesNotExist:
        messages.error(request, "Something went wrong. Institute not found.")
    
    return redirect('institute_list')