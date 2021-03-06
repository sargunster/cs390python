"""
UniversitiesApp Views

Created by Jacob Dunbar on 11/5/2016.
"""
from django.shortcuts import render, get_object_or_404

from UniversitiesApp.forms import StudentForm, CourseForm
from UniversitiesApp.models import University
from . import models
from . import forms


def getUniversities(request):
    if request.user.is_authenticated():
        universities_list = models.University.objects.all()
        context = {
            'universities': universities_list,
            'canCreate': request.user.is_staff
        }
        return render(request, 'universities.html', context)
    # render error page if user is not logged in
    return render(request, 'autherror.html')


def getUniversity(request):
    if request.user.is_authenticated():
        in_name = request.GET.get('name', 'None')
        in_university = get_object_or_404(University, name=in_name)
        is_member = in_university.members.filter(email__exact=request.user.email)
        context = {
            'university': in_university,
            'userIsMember': is_member,
            'userIsProfessor': is_member and request.user.is_professor
        }
        return render(request, 'university.html', context)
    # render error page if user is not logged in
    return render(request, 'autherror.html')


def getUniversityForm(request):
    if request.user.is_authenticated() and request.user.is_staff:
        return render(request, 'universityform.html')
    # render error page if user is not logged in
    return render(request, 'autherror.html')


def getUniversityFormSuccess(request):
    if request.user.is_authenticated() and request.user.is_staff:
        if request.method == 'POST':
            form = forms.UniversityForm(request.POST, request.FILES)
            if form.is_valid():
                if models.University.objects.filter(name__exact=form.cleaned_data['name']).exists():
                    return render(request, 'universityform.html',
                                  {'error': 'Error: That university name already exists!'})
                new_university = models.University(name=form.cleaned_data['name'],
                                                   photo=request.FILES['photo'],
                                                   description=form.cleaned_data['description'],
                                                   website=form.cleaned_data['website'])
                new_university.save()
                context = {
                    'name': form.cleaned_data['name'],
                }
                return render(request, 'universityformsuccess.html', context)
            else:
                return render(request, 'universityform.html', {'error': 'Error: Photo upload failed!'})
        else:
            form = forms.UniversityForm()
        return render(request, 'universityform.html')
    # render error page if user is not logged in
    return render(request, 'autherror.html')


def joinUniversity(request):
    if request.user.is_authenticated():
        in_name = request.GET.get('name', 'None')
        in_university = models.University.objects.get(name__exact=in_name)
        in_university.members.add(request.user)
        in_university.save()
        if request.user.university_set.count() > 0:
            universities = request.user.university_set.all()
            request.user.university_set.remove(universities[0])
        request.user.university_set.add(in_university)
        request.user.save()
        return getUniversity(request)
    return render(request, 'autherror.html')


def unjoinUniversity(request):
    if request.user.is_authenticated():
        in_name = request.GET.get('name', 'None')
        in_university = models.University.objects.get(name__exact=in_name)
        in_university.members.remove(request.user)
        in_university.save()
        request.user.university_set.remove(in_university)
        request.user.save()
        return getUniversity(request)
    return render(request, 'autherror.html')


def getCourse(request):
    if request.user.is_authenticated():
        in_university_name = request.GET.get('name', 'None')
        in_university = models.University.objects.get(name__exact=in_university_name)
        in_course_tag = request.GET.get('course', 'None')
        in_course = in_university.course_set.get(tag__exact=in_course_tag)
        is_member = in_course.members.filter(email__exact=request.user.email)
        context = {
            'university': in_university,
            'course': in_course,
            'userInCourse': is_member,
            'userIsTeacher': request.user == in_course.professor,
            'form': StudentForm()
        }
        return render(request, 'course.html', context)
    return render(request, 'autherror.html')


def courseForm(request):
    if request.user.is_authenticated() and request.user.is_professor:
        in_university_name = request.GET.get('name', 'None')
        in_university = models.University.objects.get(name__exact=in_university_name)
        context = {
            'university': in_university
        }
        return render(request, 'courseform.html', context)
        # render error page if user is not logged in
    return render(request, 'autherror.html')


def addCourse(request):
    if request.user.is_authenticated() and request.user.is_professor:
        if request.method == 'POST':
            form = forms.CourseForm(request.POST)
            if form.is_valid():
                in_university_name = request.GET.get('name', 'None')
                in_university = models.University.objects.get(name__exact=in_university_name)
                if in_university.course_set.filter(tag__exact=form.cleaned_data['tag']).exists():
                    return render(request, 'courseform.html',
                                  {'error': 'Error: That course tag already exists at this university!'})
                new_course = models.Course(tag=form.cleaned_data['tag'],
                                           name=form.cleaned_data['name'],
                                           description=form.cleaned_data['description'],
                                           university=in_university,
                                           professor=request.user)
                new_course.save()
                in_university.course_set.add(new_course)
                return getUniversity(request)
            else:
                return render(request, 'courseform.html', {'error': 'Undefined Error!'})
        else:
            form = forms.CourseForm()
            return render(request, 'courseform.html')
            # render error page if user is not logged in
    return render(request, 'autherror.html')


def removeCourse(request):
    if request.user.is_authenticated():
        in_university_name = request.GET.get('name', 'None')
        in_university = models.University.objects.get(name__exact=in_university_name)
        in_course_tag = request.GET.get('course', 'None')
        in_course = in_university.course_set.get(tag__exact=in_course_tag)
        in_course.delete()
        is_member = in_university.members.filter(email__exact=request.user.email)
        context = {
            'university': in_university,
            'userIsMember': is_member,
        }
        return render(request, 'university.html', context)
    # render error page if user is not logged in
    return render(request, 'autherror.html')


def addStudentToCourse(request):
    in_university_name = request.GET.get('name', 'None')
    in_university = models.University.objects.get(name__exact=in_university_name)
    in_course_tag = request.GET.get('course', 'None')
    in_course = in_university.course_set.get(tag__exact=in_course_tag)
    if request.user.is_authenticated() and request.user == in_course.professor:
        form = StudentForm(request.POST)
        users = models.MyUser.objects.filter(email__exact=form.data['email'])
        if users.exists() is False:
            return getCourse(request)
        in_course.members.add(users[0])
        in_course.save()
        users[0].course_set.add(in_course)
        users[0].save()
        context = {
            'university': in_university,
            'course': in_course,
            'userInCourse': in_course.members.filter(email__exact=request.user.email),
            'userIsTeacher': request.user == in_course.professor,
            'form': StudentForm()
        }
        return render(request, 'course.html', context)
    return render(request, 'autherror.html')


def removeStudentFromCourse(request):
    in_university_name = request.GET.get('name', 'None')
    in_university = models.University.objects.get(name__exact=in_university_name)
    in_course_tag = request.GET.get('course', 'None')
    in_course = in_university.course_set.get(tag__exact=in_course_tag)
    if request.user.is_authenticated() and request.user == in_course.professor:
        in_email = request.GET.get('member', 'None')
        users = models.MyUser.objects.filter(email__exact=in_email)
        if users.exists() is False:
            return getCourse(request)
        in_course.members.remove(users[0])
        in_course.save()
        users[0].course_set.remove(in_course)
        users[0].save()
        context = {
            'university': in_university,
            'course': in_course,
            'userInCourse': in_course.members.filter(email__exact=request.user.email),
            'userIsTeacher': request.user == in_course.professor,
            'form': StudentForm()
        }
        return render(request, 'course.html', context)
    return render(request, 'autherror.html')


def joinCourse(request):
    if request.user.is_authenticated():
        in_university_name = request.GET.get('name', 'None')
        in_university = models.University.objects.get(name__exact=in_university_name)
        in_course_tag = request.GET.get('course', 'None')
        in_course = in_university.course_set.get(tag__exact=in_course_tag)
        in_course.members.add(request.user)
        in_course.save()
        request.user.course_set.add(in_course)
        request.user.save()
        context = {
            'university': in_university,
            'course': in_course,
            'userInCourse': True,
            'userIsTeacher': request.user == in_course.professor
        }
        return render(request, 'course.html', context)
    return render(request, 'autherror.html')


def unjoinCourse(request):
    if request.user.is_authenticated():
        university_name = request.GET.get('name', 'None')
        university = get_object_or_404(University, name=university_name)
        in_course_tag = request.GET.get('course', 'None')
        in_course = university.course_set.get(tag__exact=in_course_tag)
        in_course.members.remove(request.user)
        in_course.save()
        request.user.course_set.remove(in_course)
        request.user.save()
        context = {
            'university': university,
            'course': in_course,
            'userInCourse': False,
            'userIsTeacher': request.user == in_course.professor
        }
        return render(request, 'course.html', context)
    return render(request, 'autherror.html')
