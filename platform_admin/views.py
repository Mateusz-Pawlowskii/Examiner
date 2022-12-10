from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.timezone import make_aware
from django.utils.text import slugify
from datetime import datetime

from exam.models import Platform, StudentGroup, Course, Question, Lesson, Term
from student.forms import StudentSearchCourseForm
from exam.functions import get_categories, get_timeover
from .forms import (UserNameChangeForm, StudentGroupForm, AttachStudentForm, AttachCourseForm, ReverseAttachStudentForm, 
                   EditPlatformForm, ChangeTermForm)
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
    form_class = StudentSearchCourseForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var" : "examiners",
                   "object_list" : User.objects.filter(groups=1, platform=platform),
                   "form" : self.form_class(),
                   "platform" : platform}
        return render(request, self.template_name, context)

class CreateExaminer(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "create_examiner.html"
    permission_required = ("auth.add_user")
    form_class = UserCreationForm

    def get(self, request):
        platform = Platform.objects.get(users=request.user)
        form = self.form_class()
        context = {"form" : form,
                   "platform" : platform}
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            group = get_object_or_404(Group, name="Examiner")
            platform = Platform.objects.get(users=request.user)
            group.user_set.add(user)
            platform.users.add(user)
            user.save()
        else:
            messages.error(request, "Niepoprawne dane")
        return redirect(reverse_lazy("platform_admin:examiner-search"))

class EditExaminer(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "edit_examiner.html"
    permission_required = ("auth.change_user")
    form_class = UserNameChangeForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        examiner = get_object_or_404(User, pk=self.kwargs["pk"])
        context = {"examiner" : examiner,
                   "form" : self.form_class(instance=examiner),
                   "platform" : platform}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        examiner = get_object_or_404(User, pk=self.kwargs["pk"])
        form = self.form_class(request.POST, instance=examiner)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("platform_admin:homepage"))

class ChangePassword(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.change_user")
    form_class = SetPasswordForm

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        form = self.form_class(data=request.POST, user=user)
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
    form_class = StudentSearchCourseForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var" : "students",
                   "object_list" : User.objects.filter(groups=2, platform=platform),
                   "form" : self.form_class(),
                   "platform" : platform}
        return render(request, self.template_name, context)

class PlatformCreateStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "create_student.html"
    permission_required = ("auth.add_user")
    form_class = UserCreationForm
    redirect = "platform_admin:student-search"
    base = "platform_base.html"

    def get(self, request):
        platform = Platform.objects.get(users=request.user)
        form = self.form_class()
        context = {"form" : form,
                   "base" : self.base,
                   "platform" : platform}
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            group = get_object_or_404(Group, name="Student")
            platform = Platform.objects.get(users=request.user)
            group.user_set.add(user)
            platform.users.add(user)
            user.save()
        else:
            messages.error(request, "Niepoprawne dane")
        return redirect(reverse_lazy(self.redirect))

class EditStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "edit_student.html"
    permission_required = ("auth.change_user")
    form_class_1 = UserNameChangeForm
    form_class_2 = ReverseAttachStudentForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        all_groups = StudentGroup.objects.filter(platform=platform)
        student = get_object_or_404(User, pk=self.kwargs["pk"])
        context = {"student" : student,
                   "form" : self.form_class_1(instance=student),
                   "attach_form" : self.form_class_2(),
                   "all_groups" : all_groups,
                   "platform" : platform}
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
    form_class = StudentSearchCourseForm
    side = "platform"
    base = "platform_base.html"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var" : "student_group",
                   "object_list" : StudentGroup.objects.filter(platform=platform),
                   "form" : self.form_class(),
                   "side" : self.side,
                   "base" : self.base,
                   "platform" : platform}
        return render(request, self.template_name, context)

class CreateStudentGroup(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "create_student_group.html"
    permission_required = ("exam.add_studentgroup")
    form_class = StudentGroupForm
    redirect_to = "platform_admin:student-group-search"
    base = "platform_base.html"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        form = self.form_class()
        context = {"form" : form,
                   "base" : self.base,
                   "platform" : platform}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            platform = Platform.objects.get(users=request.user)
            student_group = StudentGroup.objects.all().last()
            platform.studentgroup_set.add(student_group)
            platform.save()
        else:
            messages.error(request, "Stworzenie grupy nie powiodło się")
        return redirect(reverse_lazy(self.redirect_to))

class EditStudentGroup(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "edit_student_group.html"
    permission_required = ("exam.change_studentgroup")
    redirect_to = "platform_admin:student-group-search"
    base = "platform_base.html"
    side = "platform"

    def get(self, request, *args, **kwargs):
        student_group = StudentGroup.objects.get(pk=self.kwargs["pk"])
        form = StudentGroupForm(auto_id="group_%s",instance=student_group)
        student_form = AttachStudentForm(initial={"group" : student_group})
        course_form = AttachCourseForm(initial={"group" : student_group})
        platform = Platform.objects.get(users=request.user)
        group_courses = Course.objects.filter(studentgroup=student_group)
        categories = get_categories(group_courses)
        terms = []
        for course in group_courses:
            term_info = []
            term = Term.objects.filter(group=student_group,course=course).first()
            term_info.append(term)
            if get_timeover(student_group, course):
                term_info.append("(Termin upłynął)")
            else:
                term_info.append(" ")
            terms.append(term_info)

        context = {"group" : student_group,
                   "form" : form,
                   "student_form" : student_form,
                   "all_students" : User.objects.filter(platform=platform, groups=2),
                   "group_students" : User.objects.filter(studentgroup=student_group, groups=2),
                   "course_form" : course_form,
                   "all_courses" : Course.objects.filter(platform=platform),
                   "group_courses" : group_courses,
                   "categories" : categories,
                   "base" : self.base,
                   "side" : self.side,
                   "terms" : terms,
                   "term_form" : ChangeTermForm(),
                   "platform" : platform}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        student_group = StudentGroup.objects.get(pk=self.kwargs["pk"])
        form = StudentGroupForm(request.POST, instance=student_group)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, "Edycja grupy nie powiodła się")
        return redirect(reverse_lazy(self.redirect_to))

class PlatformDetailCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "platform_detail_course.html"
    permission_required = ("exam.delete_course")

    def get(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        context = {"object" : course,
                   "questions" : Question.objects.filter(course=course),
                   "group" : StudentGroup.objects.get(pk=self.kwargs["group"]),
                   "lessons" : Lesson.objects.filter(course=course),
                   "students" : User.objects.filter(course=course),
                   "platform" : Platform.objects.get(users=request.user)}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        group = self.kwargs["group"]
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        course.delete()
        messages.info(request, "Kurs został usuniety")
        return redirect(reverse_lazy("platform_admin:edit-student-group", kwargs={"pk" : group}))

class DeleteGroup(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.delete_studentgroup")

    def post(self, request, *args, **kwargs):
        student_group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"])
        student_group.delete()
        messages.info(request, "Grupa usunięta")
        return redirect(reverse_lazy("platform_admin:student-group-search"))

class AttachStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.change_user")
    redirect_to = "platform_admin:edit-student-group"

    def post(self, request, *args, **kwargs):
        student = get_object_or_404(User, username=request.POST["student"])
        student_group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"])
        student_group.students.add(student)
        student_group.save()
        return redirect(reverse_lazy(self.redirect_to, kwargs={"pk":self.kwargs["pk"]}))

class UnattachStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.change_user")
    redirect_to = "platform_admin:edit-student-group"
    
    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"])
        student = get_object_or_404(User, pk=request.POST["student"])
        group.students.remove(student)
        group.save()
        return redirect(reverse_lazy(self.redirect_to, kwargs={"pk":self.kwargs["pk"]}))

class AttachCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")
    redirect_to = "platform_admin:edit-student-group"

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, name=request.POST["course"])
        student_group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"])
        student_group.courses.add(course)
        student_group.save()
        term = Term(time=make_aware(datetime.strptime(request.POST["term"],"%Y-%m-%d")), group=student_group, course=course)
        term.save()
        return redirect(reverse_lazy(self.redirect_to, kwargs={"pk":self.kwargs["pk"]}))

class UnattachCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"])
        course = get_object_or_404(Course, pk=request.POST["course"])
        term = Term.objects.filter(course=course, group=group)
        term.delete()
        group.courses.remove(course)
        group.save()
        return redirect(reverse_lazy("platform_admin:edit-student-group", kwargs={"pk":self.kwargs["pk"]}))

class ChangeTerm(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")
    redirect_to = "platform_admin:edit-student-group"
    redirect_arg = "pk"

    def post(self, request, *args, **kwargs):
        course = Course.objects.get(pk=self.kwargs["course"])
        group = StudentGroup.objects.get(pk=self.kwargs["pk"])
        term = Term.objects.filter(course=course,group=group).first()
        time = request.POST["time"]
        term.time = time
        term.save()
        return redirect(reverse_lazy(self.redirect_to, kwargs={"pk":self.kwargs[self.redirect_arg],"slug" : slugify(group.name)}))

# views about settings
class SettingsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "settings.html"
    permission_required = ("exam.change_platform")
    form_class = EditPlatformForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"form" : self.form_class(instance=platform),
                   "platform" : platform,
                   "nav_var" : "settings"}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        form = self.form_class(request.POST, request.FILES, instance=platform)
        if form.is_valid():
            form.save()
            messages.error(request, "Ustawienia zostały zapisane")
        else:
            messages.info(request, "Niepoprawne logo")
        return HttpResponseRedirect(self.request.path_info)