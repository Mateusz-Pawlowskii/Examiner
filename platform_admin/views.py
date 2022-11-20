from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, View, TemplateView
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib import messages
from django.http import FileResponse
from django.http import HttpResponseRedirect
from operator import attrgetter
from django.core.files.storage import FileSystemStorage

from exam.models import Platform, StudentGroup, Course
from student.forms import StudentSearchCourseForm
from examiner_user.views import CreateStudent
from .forms import (UserNameChangeForm, StudentGroupForm, AttachStudentForm, AttachCourseForm, ReverseAttachStudentForm, 
                   EditPlatformForm)
# Create your views here.
class PlatformHomepage(LoginRequiredMixin, View):
    template_name = "platform_homepage.html"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var" : "homepage",
                   "platform" : platform}
        return render(request, self.template_name, context)

# Examiner managment views
class ExaminerSearch(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "search_examiner.html"
    permission_required = ("auth.view_user")

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var" : "examiners",
                   "object_list" : User.objects.filter(groups=1, platform=platform),
                   "form" : StudentSearchCourseForm()}
        return render(request, self.template_name, context)

class CreateExaminer(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "create_examiner.html"
    permission_required = ("auth.add_user")

    def get(self, request):
        form = UserCreationForm()
        context = {"form" : form}
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            group = get_object_or_404(Group, name="Examiner")
            platform = Platform.objects.get(users=request.user)
            users = User.objects.all()
            user = users.order_by('-date_joined').first()
            group.user_set.add(user)
            platform.users.add(user)
            user.save()
        else:
            messages.error(request, "Niepoprawne dane")
        return redirect(reverse_lazy("platform_admin:examiner-search"))

class EditExaminer(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "edit_examiner.html"
    permission_required = ("auth.change_user")

    def get(self, request, *args, **kwargs):
        examiner = get_object_or_404(User, pk=self.kwargs["pk"])
        context = {"examiner" : examiner,
                   "form" : UserNameChangeForm(instance=examiner)}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        examiner = get_object_or_404(User, pk=self.kwargs["pk"])
        form = UserNameChangeForm(request.POST, instance=examiner)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("platform_admin:homepage"))

class ChangePassword(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.change_user")

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        form = SetPasswordForm(data=request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.info(request, "Hasło zostało pomyślnie zmienione")
            return redirect(reverse_lazy("platform_admin:examiner-search"))
        else:
            messages.error(request, "Niepoprawne dane. Podane hasła nie zgadzają się lub nie spełniają wymogów")
            return redirect(reverse_lazy("platform_admin:examiner-search"))

class DeleteUser(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.delete_user")

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        user.delete()
        messages.info(request, "Użytkownik usunięty")
        return redirect(reverse_lazy("platform_admin:examiner-search"))

# student managment views
class StudentSearch(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "search_student.html"
    permission_required = ("auth.view_user")

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var" : "students",
                   "object_list" : User.objects.filter(groups=2, platform=platform),
                   "form" : StudentSearchCourseForm()}
        return render(request, self.template_name, context)

class PlatformCreateStudent(CreateStudent):
    redirect = "platform_admin:student-search"

# I was thinking about inhereting EditExaminer but I was afraid that it might make code less clean
class EditStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "edit_student.html"
    permission_required = ("auth.change_user")

    def get(self, request, *args, **kwargs):
        student = get_object_or_404(User, pk=self.kwargs["pk"])
        context = {"student" : student,
                   "form" : UserNameChangeForm(instance=student),
                   "attach_form" : ReverseAttachStudentForm()}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        student = get_object_or_404(User, pk=self.kwargs["pk"])
        group = get_object_or_404(StudentGroup, name=request.POST["group"])
        group.students.add(student)
        group.save()
        return redirect(reverse_lazy("platform_admin:student-search"))

# Studen group managment views
class StudentGroupSearch(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "search_student_group.html"
    permission_required = ("exam.view_studentgroup")

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var" : "student_group",
                   "object_list" : StudentGroup.objects.filter(platform=platform),
                   "form" : StudentSearchCourseForm()}
        return render(request, self.template_name, context)

class CreateStudentGroup(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "create_student_group.html"
    permission_required = ("exam.add_studentgroup")

    def get(self, request, *args, **kwargs):
        form = StudentGroupForm()
        context = {"form" : form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = StudentGroupForm(request.POST)
        if form.is_valid():
            form.save()
            platform = Platform.objects.get(users=request.user)
            student_group = StudentGroup.objects.all().last()
            platform.studentgroup_set.add(student_group)
            platform.save()
        else:
            messages.error(request, "Stworzenie grupy nie powiodło się")
        return redirect(reverse_lazy("platform_admin:student-group-search"))

class EditStudentGroup(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "edit_student_group.html"
    permission_required = ("exam.change_studentgroup")

    def get(self, request, *args, **kwargs):
        student_group = StudentGroup.objects.get(pk=self.kwargs["pk"])
        form = StudentGroupForm(auto_id="group_%s",instance=student_group)
        student_form = AttachStudentForm(initial={"group" : student_group})
        course_form = AttachCourseForm(initial={"group" : student_group})
        platform = Platform.objects.get(users=request.user)
        group_courses = Course.objects.filter(studentgroup=student_group)
        categories = []
        for course in group_courses:
            categories.append(course.category)
        categories = set(categories)
        context = {"group" : student_group,
                   "form" : form,
                   "student_form" : student_form,
                   "all_students" : User.objects.filter(platform=platform, groups=2),
                   "group_students" : User.objects.filter(studentgroup=student_group, groups=2),
                   "course_form" : course_form,
                   "all_courses" : Course.objects.filter(platform=platform),
                   "group_courses" : group_courses,
                   "categories" : categories}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        student_group = StudentGroup.objects.get(pk=self.kwargs["pk"])
        form = StudentGroupForm(request.POST, instance=student_group)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, "Edycja grupy nie powiodła się")
        return redirect(reverse_lazy("platform_admin:student-group-search"))

class AttachStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.change_user")

    def post(self, request, *args, **kwargs):
        student = get_object_or_404(User, username=request.POST["student"])
        student_group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"])
        student_group.students.add(student)
        student_group.save()
        return redirect(reverse_lazy("platform_admin:edit-student-group", kwargs={"pk":self.kwargs["pk"]}))

class UnattachStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.change_user")
    
    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"])
        student = get_object_or_404(User, pk=request.POST["student"])
        group.students.remove(student)
        group.save()
        return redirect(reverse_lazy("platform_admin:edit-student-group", kwargs={"pk":self.kwargs["pk"]}))

class AttachCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, name=request.POST["course"])
        student_group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"])
        student_group.courses.add(course)
        student_group.save()
        return redirect(reverse_lazy("platform_admin:edit-student-group", kwargs={"pk":self.kwargs["pk"]}))

class UnattachCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"])
        course = get_object_or_404(Course, pk=request.POST["course"])
        group.courses.remove(course)
        group.save()
        return redirect(reverse_lazy("platform_admin:edit-student-group", kwargs={"pk":self.kwargs["pk"]}))

# views about settings
class SettingsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "settings.html"
    permission_required = ("exam.change_platform")

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"form" : EditPlatformForm(instance=platform),
                   "platform" : platform,
                   "nav_var" : "settings"}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        form = EditPlatformForm(request.POST, request.FILES, instance=platform)
        if form.is_valid():
            form.save()
            # file = request.FILES["logo"]
            # fs = FileSystemStorage(location='/media/logos')
            # fs.save(file.name, file)
            messages.error(request, "Ustawienia zostały zapisane")
        else:
            messages.info(request, "Niepoprawne logo")
        return HttpResponseRedirect(self.request.path_info)