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
from fpdf import FPDF, HTMLMixin
from django.http import FileResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from exam.models import Platform, StudentGroup, Course, Question, Lesson, Deadline, Grade
from student.forms import StudentSearchCourseForm
from exam.functions import get_categories, get_timeover, course_mark, course_grades, get_grade_data
from .forms import (UserNameChangeForm, StudentGroupForm, AttachStudentForm, AttachCourseForm, ReverseAttachStudentForm, 
                   EditPlatformForm, ChangeDeadlineForm, GradeForm, FeedbackForm)
# Create your views here.
class PlatformHomepage(LoginRequiredMixin, View):
    template_name = "platform_homepage.html"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        if platform.inactive:
            platform.inactive = False
            platform.save()
        context = {"nav_var" : "homepage",
                   "platform" : platform}
        return render(request, self.template_name, context)

class FeedbackView(View):
    template_name = "feedback.html"
    side = "platform"
    base = "platform_base.html"
    form_class = FeedbackForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"base" : self.base,
                   "form" : self.form_class,
                   "platform" : platform}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        mail_subject = _('Opinion')
        message = render_to_string('feedback_email.html', {
            "side" : self.side,
            "points" : request.POST["points"],
            "ease_of_use" : request.POST["ease_of_use"],
            "looks" : request.POST["looks"],
            "feedback" : request.POST["feedback"]
        })
        email = EmailMessage(mail_subject, message, to=["mm.pawlowski18@gmail.com"])
        email.send()
        messages.info(request, _("Thank you for sharing your opinion"))
        return redirect(reverse_lazy("exam:home-redirect"))

class PlatformHelp(View):
    def get(self, request, *args, **kwargs):
        return FileResponse(open(f"static/help/platform_{request.LANGUAGE_CODE}.pdf", "rb"), content_type="application/pdf")

# Examiner managment views
class ExaminerSearch(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "search_examiner.html"
    permission_required = ("auth.view_user")
    form_class = StudentSearchCourseForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var" : "examiners",
                   "object_list" : User.objects.filter(groups=2, platform=platform),
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
            messages.error(request, _("Name taken"))
        return redirect(reverse_lazy("platform_admin:examiner-search"))

class EditExaminer(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "edit_examiner.html"
    permission_required = ("auth.change_user")
    form_class = UserNameChangeForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        examiner = get_object_or_404(User, pk=self.kwargs["pk"], platform=platform)
        context = {"examiner" : examiner,
                   "form" : self.form_class(instance=examiner),
                   "platform" : platform}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        examiner = get_object_or_404(User, pk=self.kwargs["pk"], platform=platform)
        form = self.form_class(request.POST, instance=examiner)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("platform_admin:homepage"))

class ChangePassword(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.change_user")
    form_class = SetPasswordForm

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        user = get_object_or_404(User, pk=self.kwargs["pk"], platform=platform)
        form = self.form_class(data=request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.info(request, _("Password sucessfully changed"))
            return redirect(reverse_lazy("platform_admin:examiner-search"))
        else:
            messages.error(request, _("Incorrect data. Passwords do not match or doesen't fulfill the requirements"))
            return redirect(reverse_lazy("platform_admin:examiner-search"))

class DeleteUser(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.delete_user")

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        user = get_object_or_404(User, pk=self.kwargs["pk"], platform=platform)
        user.delete()
        messages.info(request, _("User deleted"))
        return redirect(reverse_lazy("platform_admin:examiner-search"))

# student managment views
class StudentSearch(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "search_student.html"
    permission_required = ("auth.view_user")
    form_class = StudentSearchCourseForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var" : "students",
                   "object_list" : User.objects.filter(groups=1, platform=platform),
                   "form" : self.form_class(),
                   "platform" : platform}
        return render(request, self.template_name, context)

class PlatformCreateStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "create_student.html"
    permission_required = ("auth.add_user")
    form_class = UserCreationForm
    redirect = "platform_admin:student-search"
    base = "platform_base.html"

    def create_student(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            group = get_object_or_404(Group, name="Student")
            platform = Platform.objects.get(users=request.user)
            group.user_set.add(user)
            platform.users.add(user)
            user.save()
        else:
            messages.error(request, _("Name taken"))

    def get(self, request):
        platform = Platform.objects.get(users=request.user)
        form = self.form_class()
        context = {"form" : form,
                   "base" : self.base,
                   "platform" : platform}
        return render(request, self.template_name, context)
    
    def post(self, request):
        platform = Platform.objects.get(users=request.user)
        max_amount = platform.student_limit
        if max_amount != 0:
            student_amount = len(User.objects.filter(groups=1, platform=platform))
            if student_amount >= max_amount:
                context = {"base" : self.base,
                           "kind" : _("students"),
                           "max_amount" : max_amount}
                return render(request, "limit_exceeded.html", context)
            else:
                self.create_student(request)
        else:
            self.create_student(request)
        return redirect(reverse_lazy(self.redirect))

class EditStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "edit_student.html"
    permission_required = ("auth.change_user")
    form_class_1 = UserNameChangeForm
    form_class_2 = ReverseAttachStudentForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        all_groups = StudentGroup.objects.filter(platform=platform)
        student = get_object_or_404(User, pk=self.kwargs["pk"], platform=platform)
        context = {"student" : student,
                   "form" : self.form_class_1(instance=student),
                   "attach_form" : self.form_class_2(),
                   "all_groups" : all_groups,
                   "platform" : platform}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        student = get_object_or_404(User, pk=self.kwargs["pk"], platform=platform)
        try:
            group = StudentGroup.objects.get(name=request.POST["group"], platform=platform)
        except:
            messages.error(request, _("Student group not found"))
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

    def create_group(self, request):
        platform = Platform.objects.get(users=request.user)
        form = self.form_class(request.POST)
        groups = StudentGroup.objects.filter(platform=platform)
        for group in groups:
            if request.POST["name"] == group.name:
                messages.error(request, _("Name taken"))
                return redirect(reverse_lazy(self.redirect_to))
        if form.is_valid():
            form.save()
        else:
            messages.error(request, _("Group creation failed"))

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        form = self.form_class({"platform" : platform})
        context = {"form" : form,
                   "base" : self.base,
                   "platform" : platform}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        max_amount = platform.group_limit
        if max_amount != 0:
            group_amount = len(StudentGroup.objects.filter(platform=platform))
            if group_amount >= max_amount:
                context = {"base" : self.base,
                           "kind" : _("student groups"),
                           "max_amount" : max_amount}
                return render(request, "limit_exceeded.html", context)
            else:
                self.create_group(request)
        else:
            self.create_group(request)
        return redirect(reverse_lazy(self.redirect_to))

class EditStudentGroup(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "edit_student_group.html"
    permission_required = ("exam.change_studentgroup")
    redirect_to = "platform_admin:student-group-search"
    base = "platform_base.html"
    side = "platform"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        student_group = StudentGroup.objects.get(pk=self.kwargs["pk"], platform=platform)
        form = StudentGroupForm(auto_id="group_%s",instance=student_group)
        student_form = AttachStudentForm(initial={"group" : student_group})
        course_form = AttachCourseForm(initial={"group" : student_group})
        group_courses = Course.objects.filter(studentgroup=student_group)
        categories = get_categories(group_courses)
        deadlines = []
        for course in group_courses:
            deadline_info = []
            deadline = Deadline.objects.filter(group=student_group,course=course).first()
            deadline_info.append(deadline)
            if get_timeover(student_group, course):
                deadline_info.append(_("(Deadline expired)"))
            else:
                deadline_info.append(" ")
            deadlines.append(deadline_info)

        context = {"group" : student_group,
                   "form" : form,
                   "student_form" : student_form,
                   "all_students" : User.objects.filter(platform=platform, groups=1),
                   "group_students" : User.objects.filter(studentgroup=student_group, groups=1),
                   "course_form" : course_form,
                   "all_courses" : Course.objects.filter(platform=platform),
                   "group_courses" : group_courses,
                   "categories" : categories,
                   "base" : self.base,
                   "side" : self.side,
                   "deadlines" : deadlines,
                   "deadline_form" : ChangeDeadlineForm(),
                   "platform" : platform}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        student_group = StudentGroup.objects.get(pk=self.kwargs["pk"], platform=platform)
        form = StudentGroupForm(request.POST, instance=student_group)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, _("Group edit failed"))
        return redirect(reverse_lazy(self.redirect_to))

class PlatformDetailCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "platform_detail_course.html"
    permission_required = ("exam.delete_course")

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"], platform=platform)
        context = {"object" : course,
                   "questions" : Question.objects.filter(course=course),
                   "group" : StudentGroup.objects.get(pk=self.kwargs["group"], platform=platform),
                   "lessons" : Lesson.objects.filter(course=course),
                   "platform" : Platform.objects.get(users=request.user)}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        group = StudentGroup.objects.get(pk = self.kwargs["group"])
        course = get_object_or_404(Course, pk=self.kwargs["pk"], platform=platform)
        course.delete()
        messages.info(request, _("Course deleted"))
        return redirect(reverse_lazy("platform_admin:edit-student-group",kwargs={"pk":group.pk,"slug":slugify(group.name)}))

class DeleteGroup(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.delete_studentgroup")

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        student_group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"], platform=platform)
        student_group.delete()
        messages.info(request, _("Group deleted"))
        return redirect(reverse_lazy("platform_admin:student-group-search"))

class AttachStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.change_user")
    redirect_to = "platform_admin:edit-student-group"
    base = "platform_base.html"

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"], platform=platform)
        try:
            student = User.objects.get(username=request.POST["student"], platform=platform)
        except:
            messages.error(request, _("Student not found"))
            return redirect(reverse_lazy(self.redirect_to, kwargs={"pk":self.kwargs["pk"],"slug":slugify(group.name)}))
        max_amount = platform.student_per_group_limit
        if max_amount != 0:
            if len(User.objects.filter(studentgroup=group)) >= max_amount:
                context = {"base" : self.base,
                           "attach" : "student",
                           "max_amount" : max_amount}
                return render(request, "limit_exceeded.html", context)
            else:
                group.students.add(student)
                group.save()
        else:
            group.students.add(student)
            group.save()
        return redirect(reverse_lazy(self.redirect_to, kwargs={"pk":self.kwargs["pk"],"slug":slugify(group.name)}))

class UnattachStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.change_user")
    redirect_to = "platform_admin:edit-student-group"
    
    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"], platform=platform)
        student = get_object_or_404(User, pk=request.POST["student"], platform=platform)
        group.students.remove(student)
        group.save()
        return redirect(reverse_lazy(self.redirect_to, kwargs={"pk":self.kwargs["pk"],"slug":slugify(group.name)}))

class AttachCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")
    redirect_to = "platform_admin:edit-student-group"
    base = "platform_base.html"

    def attach_course(self, request, course, group):
        group.courses.add(course)
        group.save()
        deadline = Deadline(time=make_aware(datetime.strptime(request.POST["deadline"],"%Y-%m-%d")), group=group, course=course)
        deadline.save()

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"], platform=platform)
        try:
            course = Course.objects.get(name=request.POST["course"], platform=platform)
        except:
            messages.error(request, _("Course not found"))
            return redirect(reverse_lazy(self.redirect_to, kwargs={"pk":self.kwargs["pk"],"slug":slugify(group.name)}))
        max_amount = platform.course_per_group_limit
        if max_amount != 0:
            if len(Course.objects.filter(studentgroup=group)) >= max_amount:
                context = {"base" : self.base,
                           "attach" : "course",
                           "max_amount" : max_amount}
                return render(request, "limit_exceeded.html", context)
            else:
                self.attach_course(request, course, group)
        else:
            self.attach_course(request, course, group)
        return redirect(reverse_lazy(self.redirect_to, kwargs={"pk":self.kwargs["pk"],"slug":slugify(group.name)}))

class UnattachCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"], platform=platform)
        course = get_object_or_404(Course, pk=request.POST["course"], platform=platform)
        deadline = Deadline.objects.filter(course=course, group=group)
        deadline.delete()
        group.courses.remove(course)
        group.save()
        return redirect(reverse_lazy("platform_admin:edit-student-group", kwargs={"pk":self.kwargs["pk"],"slug":slugify(group.name)}))

class ChangeDeadline(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")
    redirect_to = "platform_admin:edit-student-group"
    redirect_arg = "pk"

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = Course.objects.get(pk=self.kwargs["course"], platform=platform)
        group = StudentGroup.objects.get(pk=self.kwargs["pk"], platform=platform)
        deadline = Deadline.objects.filter(course=course,group=group).first()
        time = request.POST["time"]
        deadline.time = time
        deadline.save()
        return redirect(reverse_lazy(self.redirect_to, kwargs={"pk":self.kwargs[self.redirect_arg],"slug" : slugify(group.name)}))

class GroupReport(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.view_studentgroup")

    class HTML_PDF(FPDF, HTMLMixin):
        pass

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        group = get_object_or_404(StudentGroup, pk=self.kwargs["group"], platform=platform)
        students = sorted(User.objects.filter(studentgroup=group), key= lambda student:student.username)
        course = get_object_or_404(Course, pk=self.kwargs["course"], platform=platform)
        timeover = get_timeover(group, course)
        test_marks = course_mark(course, students, timeover)
        grades_list = course_grades(course, students)
        perc_sign = "%"
        pdf = self.HTML_PDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'static/font/ttf/DejaVuSerif.ttf', uni=True)
        pdf.set_font('DejaVu', '', 20)
        pdf.multi_cell(0, 20, txt = _("Group %(group)s results from %(course)s course") % 
        {"group" : group.name, "course" : course.name}, align = 'C', ln=2)
        pdf.set_font('DejaVu', '', 15)
        pdf.multi_cell(80, 15, txt = _("Student name"), ln=3)
        pdf.multi_cell(80, 15, txt = _("Status"), ln=3)
        if get_grade_data(platform):
            pdf.multi_cell(80, 15, txt = _("Grade"), ln=3)
            perc_sign = ""
        else:
            pdf.multi_cell(80, 15, txt = "%", ln=3)
        pdf.ln(6)
        for index in range(0,len(students)):
            pdf.multi_cell(80, 15, txt = f"{students[index].username}", ln=3)
            pdf.multi_cell(80, 15, txt = f"{test_marks[index]}", ln=3)
            pdf.multi_cell(80, 15, txt = f"{grades_list[index]}{perc_sign}", ln=3)
            pdf.ln(6)
        pdf.output("media/raports/raport.pdf")
        return FileResponse(open("media/raports/raport.pdf", "rb"), content_type="application/pdf")

# views about settings
class SettingsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "settings.html"
    permission_required = ("exam.change_platform")
    form_class = EditPlatformForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        grades = sorted(Grade.objects.filter(platform=platform), key = lambda grade:grade.bar, reverse=True)
        context = {"form" : self.form_class(instance=platform, auto_id="platform_"),
                   "platform" : platform,
                   "grade_form" : GradeForm(initial={"platform":platform}),
                   "grades" : grades,
                   "nav_var" : "settings"}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        form = self.form_class(request.POST, request.FILES, instance=platform)
        if form.is_valid():
            form.save()
            messages.info(request, _("Settings saved"))
        else:
            messages.error(request, _("Incorrect logo"))
        return HttpResponseRedirect(self.request.path_info)

class CreateGradeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.add_grade")
    form_class = GradeForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, _("New grade sucessfully added"))
            return redirect(reverse_lazy("platform_admin:settings"))
        messages.error(request, _("Incorrect grade data"))
        return redirect(reverse_lazy("platform_admin:settings"))

class DeleteGradeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.add_grade")
    form_class = GradeForm

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        grade = get_object_or_404(Grade, pk=self.kwargs["pk"], platform=platform)
        grade.delete()
        messages.info(request, _("Grade deleted"))
        return redirect(reverse_lazy("platform_admin:settings"))

class DefaultGrades(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.add_grade")

    def create_school_grading(self, platform):
        """This function creates standard school grades and adds them
        to the given platform"""
        Grade(name="1", bar=0, platform=platform).save()
        Grade(name="2", bar=40, platform=platform).save()
        Grade(name="3", bar=55, platform=platform).save()
        Grade(name="4", bar=70, platform=platform).save()
        Grade(name="5", bar=84, platform=platform).save()
        Grade(name="6", bar=96, platform=platform).save()
    
    def create_academic_grading(self, platform):
        """This function creates standard university grades and adds them
        to the given platform"""
        Grade(name="2", bar=0, platform=platform).save()
        Grade(name="3", bar=51, platform=platform).save()
        Grade(name="3.5", bar=61, platform=platform).save()
        Grade(name="4", bar=71, platform=platform).save()
        Grade(name="4.5", bar=81, platform=platform).save()
        Grade(name="5", bar=91, platform=platform).save()
    
    def clear_old_grades(self, grades):
        for grade in grades:
            grade.delete()

    def post(self, request, *args, **kwargs):
        grading_system = self.kwargs["grading_sys"]
        platform = Platform.objects.get(users=request.user)
        present_grades = Grade.objects.filter(platform=platform)
        if grading_system == "school":
            self.clear_old_grades(present_grades)
            self.create_school_grading(platform)
            messages.info(request, _("School grading system sucessfully implemented"))
        elif grading_system == "academic":
            self.clear_old_grades(present_grades)
            self.create_academic_grading(platform)
            messages.info(request, _("Academic grading system sucessfully implemented"))
        else:
            messages.error(request, _("Default grade implementation error"))
        return redirect(reverse_lazy("platform_admin:settings"))

# Test views
# Selenium cleans up the database on its own only when models are created with objectModel.create() methods and
# does not clean the database after selenium-created views so I needed a seprate view for tearDown
class Clean_up(View):
    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        while Course.objects.filter(name="Failed", platform=platform).first():
            Course.objects.filter(name="Failed", platform=platform).first().delete()
        while Course.objects.filter(name="Out of time", platform=platform).first():
            Course.objects.filter(name="Out of time", platform=platform).first().delete()
        while Course.objects.filter(name="Test course name", platform=platform).first():
            Course.objects.filter(name="Test course name", platform=platform).first().delete()
        while Course.objects.filter(name="Edited course name", platform=platform).first():
            Course.objects.filter(name="Edited course name", platform=platform).first().delete()
        while StudentGroup.objects.filter(name="Test_Group").first():
            StudentGroup.objects.filter(name="Test_Group").first().delete()
        return redirect(reverse_lazy("exam:home-redirect"))