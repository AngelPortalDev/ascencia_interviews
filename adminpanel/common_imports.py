from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from adminpanel.helpers import save_data, base64_encode, base64_decode
from datetime import datetime



# helper
from adminpanel.helpers import save_data, base64_encode, base64_decode

# models
from adminpanel.models.course import Course
from adminpanel.models.institute import Institute
from adminpanel.models.question import Question
from adminpanel.models.common_question import CommonQuestion
from adminpanel.models.student_manager_profile import StudentManagerProfile
from django.contrib.auth.models import User
