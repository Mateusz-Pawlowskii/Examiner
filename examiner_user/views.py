from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import FileResponse
from django.http import HttpResponseRedirect
from operator import attrgetter
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from .forms import (CourseForm, QuestionForm, QuestionFormMultiple, LessonForm, AttachCourseToGroupForm, AttachStudentTextForm, 
                    LessonRenameForm, LessonEditForm, CourseEditForm, AttachStudentTextForm)
from exam.models import Course, Lesson, Question, Result, Platform, StudentGroup, Deadline
from student.forms import StudentSearchCourseForm
from platform_admin.views import (PlatformCreateStudent, StudentGroupSearch, CreateStudentGroup, EditStudentGroup, AttachCourse, 
                                  AttachStudent, UnattachStudent, ChangeDeadline, FeedbackView)
from platform_admin.forms import ChangeDeadlineForm
from exam.functions import test_mark, course_mark, get_timeover, student_grades, course_grades, get_grade_data
from .functions import get_maximum_result, initialize_course_information, get_result_data
# Create your views here.

class ExaminerHomepage(LoginRequiredMixin, View):
    template_name = "examiner_homepage.html"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var":"homepage",
                   "platform" : platform}
        return render(request, self.template_name, context)

class ExaminerFeedback(FeedbackView):
    side = "examiner"
    base = "examiner_base.html"

class ExaminerHelp(View):
    def get(self, request, *args, **kwargs):
        return FileResponse(open(f"static/help/examiner_{request.LANGUAGE_CODE}.pdf", "rb"), content_type="application/pdf")

# part about users starts here
class StudentView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "students.html"
    permission_required = ("auth.view_user")
    form_class = StudentSearchCourseForm

    def get(self, request):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var" : "users",
                   "object_list" : User.objects.filter(groups=1, platform=platform),
                   "form" : self.form_class(),
                   "platform" : platform}
        return render(request, self.template_name, context)

class DetailStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "detail_student.html"
    permission_required = ("auth.view_user")
    form_class = AttachStudentTextForm

    def get_course_data(self, groups, student):
        courses = []
        test_marks = []
        course_data = []
        grades_list = []
        for group in groups:
            group_courses = Course.objects.filter(studentgroup=group)
            for group_course in group_courses:
                if group_course not in courses:
                    courses.append(group_course)
        for course in courses:
            course_data.append([course.pk, course.name])
            test_marks.extend(test_mark(courses, student))
            grades_list.extend(student_grades(courses, student))
        return (course_data, test_marks, grades_list)

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        student = get_object_or_404(User, pk=self.kwargs["pk"], platform=platform)
        groups = StudentGroup.objects.filter(students=student)
        course_data = self.get_course_data(groups, student)
        all_groups = StudentGroup.objects.filter(platform=platform)
        context = {"student" : student,
                   "courses" : course_data[0],
                   "test_marks" : course_data[1],
                   "grades_list" : course_data[2],
                   "form" : self.form_class(),
                   "platform" : platform,
                   "groups" : groups,
                   "all_groups" : all_groups,
                   "grades" : get_grade_data(platform)}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        try:
            group = StudentGroup.objects.get(name=request.POST["group"], platform=platform)
        except:
            messages.error(request, _("Student group not found"))
        student = get_object_or_404(User, pk=self.kwargs["pk"], platform=platform)
        group.students.add(student)
        group.save()
        return redirect(reverse_lazy("examiner_user:detail-student", kwargs={"pk":self.kwargs["pk"]}))

class CreateStudent(PlatformCreateStudent):
    redirect = "examiner_user:students"
    base = "examiner_base.html"

class AttachCourseText(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.change_user")

    def attach_course(self, request, group, course):
        group.courses.add(course)
        group.save()
        Deadline(course=course, group=group, time=request.POST["deadline"]).save()

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        try:
            group = StudentGroup.objects.get(name=request.POST["group"], platform=platform)
        except:
            messages.error(request, _("Student group not found"))
        course = get_object_or_404(Course, pk=self.kwargs["pk"], platform=platform)
        max_amount = platform.course_per_group_limit
        if max_amount != 0:
            if len(Course.objects.filter(studentgroup=group)) >= max_amount:
                context = {"base" : "examiner_base.html",
                           "attach" : "course",
                           "max_amount" : max_amount}
                return render(request, "limit_exceeded.html", context)
        else:
            self.attach_course(request, group, course)
        return redirect(reverse_lazy("examiner_user:edit-course", kwargs={"pk":self.kwargs["pk"],"slug":self.kwargs["slug"]}))

class UnattachGroup(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")
    
    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"], platform=platform)
        group = get_object_or_404(StudentGroup, pk=request.POST["group"], platform=platform)
        group.courses.remove(course)
        group.save()
        return redirect(reverse_lazy("examiner_user:edit-course", kwargs={"pk":self.kwargs["pk"], "slug":self.kwargs["slug"]}))

class UnattachCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=request.POST["course"], platform=platform)
        group = get_object_or_404(StudentGroup, pk=self.kwargs["pk"], platform=platform)
        group.courses.remove(course)
        group.save()
        return redirect(reverse_lazy("examiner_user:examiner-edit-group", kwargs={"pk":self.kwargs["pk"], "slug":slugify(group.name)}))

# part about courses starts here
class CreateCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.add_course")
    template_name="create_course.html"
    form_class = CourseForm

    def create_course(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, _("Course sucessfully created"))
            return redirect(reverse_lazy("examiner_user:search-course"))
        messages.error(request, _("Course creation failed"))

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"form" : self.form_class({"platform" : platform}),
                   "platform" : platform}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        max_amount = platform.course_limit
        if max_amount != 0:
            if len(Course.objects.filter(platform=platform)) >= max_amount:
                context = {"base" : "examiner_base.html",
                           "kind" : _("course"),
                           "max_amount" : max_amount}
                return render(request, "limit_exceeded.html", context)
            else:
                self.create_course(request)
        else:
            self.create_course(request)
        return redirect(reverse_lazy("examiner_user:search-course"))

class SearchCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.view_course")
    template_name="search_course.html"
    form_class = StudentSearchCourseForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        queryset = Course.objects.filter(platform=platform)
        categories = []
        for course in queryset:
            categories.append(course.category)
        categories = set(categories)
        context = {"nav_var":"search_course",
                     "form" : self.form_class(),
                     "categories" : categories,
                     "object_list" : queryset,
                     "platform" : platform}
        return render(request, self.template_name, context)

class DetailCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.view_course")
    queryset = Course.objects.all()
    template_name="detail_course.html"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"], platform=platform)
        allowed_courses = Course.objects.filter(platform=platform)
        context = {"object" : course,
                   "questions" : Question.objects.filter(course=course),
                   "lessons" : Lesson.objects.filter(course=course),
                   "platform" : platform}
        if course in allowed_courses:
            return render(request, self.template_name, context)
        messages.error(request, _("Course not found"))
        return redirect(reverse_lazy("examiner_user:search-course"))

class ControlCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")
    template_name="control_course.html"
    form_class = CourseEditForm

    def get_deadline_data(self, course):
        course_groups = StudentGroup.objects.filter(courses=course)
        deadlines = []
        for group in course_groups:
            deadline_info = []
            deadline = Deadline.objects.filter(group=group,course=course).first()
            deadline_info.append(deadline)
            if get_timeover(group, course):
                deadline_info.append(_("(Deadline expired)"))
            else:
                deadline_info.append(" ")
            deadlines.append(deadline_info)
        return deadlines

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"], platform=platform)
        if course not in Course.objects.filter(platform=platform):
            messages.error(request, _("Lack of permission"))
            return redirect(reverse_lazy("examiner_user:search-course"))
        course_form = self.form_class(instance=course)
        lesson_list = Lesson.objects.filter(course=course)
        context = {"object" : course,
                   "course_form" : course_form,
                   "lesson_form" : LessonForm(initial={"course" : course}),
                   "lesson_list" : lesson_list,
                   "group_form" : AttachCourseToGroupForm(initial={"course" : course}),
                   "student_groups" : StudentGroup.objects.filter(platform=platform),
                   "deadlines" : self.get_deadline_data(course),
                   "deadline_form" : ChangeDeadlineForm(),
                   "platform" : platform
                   }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"], platform=platform)
        if request.POST["multiple_answer_questions"] == "on":
            course.multiple_answer_questions = True
        else:
            course.multiple_answer_questions = False
        form = self.form_class(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("examiner_user:detail-course", kwargs={"pk":course.pk, "slug":self.kwargs["slug"]}))
        else:
            messages.error(request, _("Course data was filled incorrectly"))
            return HttpResponseRedirect(self.request.path_info)

# part about questions starts here
class CreateQuestion(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.add_question")
    queryset = Course.objects.all()
    template_name="create_question.html" 
    form_class = QuestionForm

    def create_question(self, request, course_):
        form = self.form_class(request.POST)
        if course_.multiple_answer_questions is True:
            data = request.POST.copy()
            correct_string = ""
            for n in range(1,6):
                if f"che{n}" in request.POST:
                    correct_string += str(n)
            data["correct_answers"] = correct_string
            form = QuestionFormMultiple(data)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, _("Correct answer was incorrectly marked"))
        
    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        pk = self.kwargs["pk"]
        course_=get_object_or_404(Course, pk=pk, platform=platform)
        form = self.form_class(initial={"course":course_})
        question_amount = len(Question.objects.filter(course=course_))
        context = {"form" : form,
                   "course" : course_,
                   "question_amount" : question_amount,
                   "platform" : platform}
        if course_.multiple_answer_questions is True:
            context["form"] = QuestionFormMultiple(initial={"course":course_})
            return render(request, "mulitple_create_question.html", context)
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        pk = self.kwargs["pk"]
        course_=get_object_or_404(Course, pk=pk, platform=platform)
        max_amount = platform.question_per_course_limit
        if max_amount != 0:
            if len(Question.objects.filter(course=course_)) >= max_amount:
                context = {"base" : "examiner_base.html",
                           "attach" : "question",
                           "max_amount" : max_amount}
                return render(request, "limit_exceeded.html", context)
            else:
                self.create_question(request, course_)
        else:
            self.create_question(request, course_)
        return HttpResponseRedirect(self.request.path_info)

class SearchQuestion(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "search_question.html"
    permission_required = ("exam.view_question")

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course_pk = self.kwargs["pk"]
        course_ = get_object_or_404(Course, pk=course_pk, platform=platform)
        questions = Question.objects.filter(course=course_)
        context = {"questions" : questions,
                   "course" : course_,
                   "platform" : platform}
        return render(request, self.template_name, context)

class EditQuestion(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_question")
    queryset = Course.objects.all()
    template_name="edit_question.html" 
    form_class = QuestionForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        question = get_object_or_404(Question, pk=self.kwargs["pk"])
        course_ = question.course
        form = self.form_class(instance=question)
        question_amount = len(Question.objects.filter(course=course_))
        context = {"form" : form,
                   "course" : course_,
                   "question" : question,
                   "question_amount" : question_amount,
                   "platform" : platform}
        if course_.multiple_answer_questions is True:
            context["form"] = QuestionFormMultiple(instance=question)
            return render(request, "mulitple_edit_question.html", context)
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        question = get_object_or_404(Question, pk=pk)
        course_ = question.course
        form = self.form_class(request.POST)
        data = request.POST.copy()
        data['course'] = course_
        if course_.multiple_answer_questions is True:
            correct_string = ""
            for n in range(1,6):
                if f"che{n}" in request.POST:
                    correct_string += str(n)
            data["correct_answers"] = correct_string
            form = QuestionFormMultiple(data, instance=question)
        else:
            form = self.form_class(data, instance=question)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, _("Correct answer was incorrectly marked"))
        return redirect(reverse_lazy("examiner_user:search-question", 
        kwargs={"pk":course_.pk, "slug":self.kwargs["slug"]}))

class DeleteQuestion(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.delete_question")

    def post(self, request, *args, **kwargs):
        question = get_object_or_404(Question, pk=self.kwargs["question"])
        question.delete()
        return redirect(reverse_lazy("examiner_user:search-question",
         kwargs={"pk":self.kwargs["course"],"slug":self.kwargs["slug"]}))

# part about lessons starts here
class CreateLesson(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.add_lesson")
    template_name = "create_lesson.html"
    form_class = LessonForm

    def create_lesson(self, request, course_):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            course_.lesson_amount += 1
            course_.save()
        else:
            messages.error(request, _("Wrong file"))

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course_ = get_object_or_404(Course, pk=self.kwargs["pk"], platform=platform)
        form = self.form_class(initial={"course":course_})
        context = {"form" : form,
                   "course" : course_,
                   "platform" : platform}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course_ = get_object_or_404(Course, pk=self.kwargs["pk"], platform=platform)
        max_amount = platform.lesson_per_course_limit
        if max_amount != 0:
            if len(Lesson.objects.filter(course=course_)) >= max_amount:
                context = {"base" : "examiner_base.html",
                           "attach" : "lesson",
                           "max_amount" : max_amount}
                return render(request, "limit_exceeded.html", context)
            else:
                self.create_lesson(request, course_)
        else:
            self.create_lesson(request, course_)
        return redirect(reverse_lazy("examiner_user:edit-course", kwargs={"pk":course_.pk, "slug":self.kwargs["slug"]}))

class DetailLesson(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.view_lesson")
    template_name="detail_lesson.html" 
    queryset = Lesson.objects.all()

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        lesson = get_object_or_404(Lesson, pk=self.kwargs["pk"])
        context = {"lesson":lesson,
                   "course_pk":lesson.course.pk,
                   "slug" : self.kwargs["slug"],
                   "platform" : platform}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=self.kwargs["pk"])
        course = lesson.course
        lesson.delete()
        course.lesson_amount -= 1
        course.save()
        return redirect(reverse_lazy("examiner_user:edit-course", kwargs={"pk":course.pk, "slug":self.kwargs["slug"]}))

class ViewLesson(LoginRequiredMixin, View):

    def check_file(self, filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {"pdf"}

    def get(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=self.kwargs["pk"])
        if self.check_file(str(lesson.material)):
            return FileResponse(open(f"https://examiner-mp.s3.eu-central-1.amazonaws.com/media/lessons/{lesson.material}", "rb"), content_type="application/pdf")
        else:
            return FileResponse(open(f"https://examiner-mp.s3.eu-central-1.amazonaws.com/media/lessons/{lesson.material}", "rb"), as_attachment=True)

class EditLessonContent(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_lesson")
    template_name = "edit_lesson_content.html"
    form_class = LessonEditForm

    def allowed_file(self, filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {"pdf"}

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        lesson = get_object_or_404(Lesson, pk=self.kwargs["pk"])
        course_ = lesson.course
        form = self.form_class(instance=lesson)
        context = {"form":form,
                   "course":course_,
                   "platform" : platform}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=self.kwargs["pk"])
        form = self.form_class(request.POST, request.FILES, instance=lesson)
        try:
            file = request.FILES["material"]
        except:
            messages.error(request, _("New resource should be given during learning resource change"))
            return redirect(reverse_lazy("examiner_user:detail-lesson",
                    kwargs={"pk":lesson.pk,"slug":slugify(lesson.topic)}))
        if self.allowed_file(file.name):
            if form.is_valid():
                form.save()
        else:
            messages.error(request, _("Wrong file extension"))
        return redirect(reverse_lazy("examiner_user:detail-lesson",
                kwargs={"pk":lesson.pk,"slug":slugify(lesson.topic)}))

class EditLessonTopic(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_lesson")
    template_name = "edit_lesson_topic.html"
    form_class = LessonRenameForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        lesson = get_object_or_404(Lesson, pk=self.kwargs["pk"])
        course_=lesson.course
        form = self.form_class(instance=lesson)
        context = {"form":form,
                   "course":course_,
                   "platform" : platform}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=self.kwargs["pk"])
        form = self.form_class(request.POST,instance=lesson)
        if form.is_valid():
                form.save()
        else:
            messages.error(request, _("Incorrect lesson topic"))
        return redirect(reverse_lazy("examiner_user:detail-lesson", kwargs={"pk":self.kwargs["pk"],"slug":slugify(lesson.topic)}))

# Result views
class GenralResultView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "results.html"
    permission_required = ("exam.view_result")
    form_class = StudentSearchCourseForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        courses = Course.objects.filter(platform=platform)
        context = {"course_data" : courses,
                   "nav_var" : "results",
                   "form" : self.form_class(),
                   "platform" : platform}
        return render(request, self.template_name, context)

class ExaminerResultView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "results_course_student.html"
    permission_required = ("auth.view_user")

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["course"], platform=platform)
        student = get_object_or_404(User, pk=self.kwargs["student"], platform=platform)
        results = Result.objects.filter(course=course, student=student)
        perc = []
        for result in results:
            perc.append(round(100*result.current_score/course.question_amount))
        context = {"course" : course,
                   "results" : zip(results , perc),
                   "student" : student,
                   "platform" : platform}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        result = Result.objects.get(pk=request.POST["result"])
        result.delete()
        return HttpResponseRedirect(self.request.path_info)
        
class CourseResults(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "course_results.html"
    permission_required = ("auth.view_user")

    def remove_repeating_students(self, students):
        students = set(students)
        students = list(students)
        return sorted(students, key = lambda student: student[3])

    def update_context(self, context, student_list, student_no, passed_no, failed_no,
                       not_yet_mark_no, course_information, test_marks, grades_list):
        context["student_list"] = student_list
        context["student_no"] = student_no
        context["pass_no"] = [passed_no, failed_no, not_yet_mark_no]
        context["course_information"] = course_information
        context["pass_list"] = [ _("Passed"), _("Failed"), _("Unfinished")]
        context["test_marks"] = test_marks
        context["grades_list"] = grades_list
        return context

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"], platform=platform)
        groups = StudentGroup.objects.filter(courses=course, platform=platform)
        deadlines = []
        for group in groups:
            deadlines.append(Deadline.objects.filter(group=group.pk).first().time)
        # expression below sorts groups so that the ones with further deadline are processed first
        # it makes it so that one student connected to one course through two groups with
        # different deadlines would work correctly
        sorted_groups = list(map(lambda pair:pair[0],(sorted(list(map(lambda x, y:(x,y), groups, deadlines)),
                        key = lambda pair:pair[1], reverse = True))))
        context = {"course" : course,
                   "groups" : sorted_groups,
                   "grades" : get_grade_data(platform),
                   "platform" : platform
                   }
        context["questions"] = Question.objects.filter(course=course)
        context["lessons"] = Lesson.objects.filter(course=course)
        course_information = initialize_course_information(course)
        students = []
        unique_students = []
        test_marks = []
        grades_list = []
        for group in sorted_groups:
            not_repeating_students = []
            group_students = User.objects.filter(studentgroup=group, platform=platform)
            for student in group_students:
                if student not in unique_students:
                    not_repeating_students.append(student)
            timeover = get_timeover(group, course)
            test_marks.extend(course_mark(course, not_repeating_students, timeover))
            grades_list.extend(course_grades(course, not_repeating_students))
            for student in not_repeating_students:
                students.append((student.pk,student.username, get_maximum_result(student, course),
                course_information["student_amount"]))
                course_information["student_amount"] += 1
                if test_mark([course], student)[0] == _("Passed"):
                    course_information["passed_students"] += 1
                elif test_mark([course], student)[0] == _("Failed"):
                    course_information["failed_students"] += 1
                else:
                    course_information["current_students"] += 1
            unique_students.extend(not_repeating_students)
        context["students"] = self.remove_repeating_students(students)
        # Part for graphs starts here
        students = sorted(context["students"], key = lambda student: student[2], reverse=True)
        student_no = []
        student_list = []
        for student in students:
            results = Result.objects.filter(course=course, student=User.objects.get(pk=student[0]))
            if results:
                result = max(results, key=attrgetter("current_score"))
                student_no.append(round(100 * result.current_score/course.question_amount))
                student_list.append(student[1])
        course_information = get_result_data(course_information, course)
        passed_no = test_marks.count(_("Passed"))
        failed_no = test_marks.count(_("Failed"))
        not_yet_mark_no = test_marks.count(_("Unfinished"))
        # Part for graphs ends here
        context = self.update_context(context, student_list, student_no, passed_no, failed_no,
                                      not_yet_mark_no, course_information, test_marks, grades_list)
        return render(request, self.template_name, context)

class CourseGroupResults(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "course_group_results.html"
    permission_required = ("exam.view_result")

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["course"], platform=platform)
        group = get_object_or_404(StudentGroup, pk=self.kwargs["group"], platform=platform)
        students = User.objects.filter(studentgroup=group)
        context = {"course" : course,
                   "students" : students,
                   "group" : group,
                   "grades" : get_grade_data(platform),
                   "platform" : platform}
        course_information = initialize_course_information(course)
        for student in User.objects.filter(studentgroup=group):
            if test_mark([course], student)[0] == _("Passed"):
                course_information["passed_students"] += 1
            elif test_mark([course], student)[0] == _("Failed"):
                course_information["failed_students"] += 1
            else:
                course_information["current_students"] += 1
        course_information = get_result_data(course_information, course)
        context["course_information"] = course_information
        timeover = get_timeover(group, course)
        test_marks = course_mark(course, students, timeover)
        grades_list = course_grades(course, students)
        # Part for graphs starts here
        passed_no = test_marks.count(_("Passed"))
        failed_no = test_marks.count(_("Failed"))
        not_yet_mark_no = test_marks.count(_("Unfinished"))
        context["pass_list"] = [ _("Passed"), _("Failed"), _("Unfinished")]
        context["pass_no"] = [passed_no, failed_no, not_yet_mark_no]
        student_list = []
        student_no = []
        students = sorted(students, key = lambda student: get_maximum_result(student, course), reverse=True)
        for student in students:
            results = Result.objects.filter(course=course, student=student)
            if results:
                result = max(results, key=attrgetter("current_score"))
                student_no.append(round(100 * result.current_score/course.question_amount))
                student_list.append(student.username)
        # Part for graphs ends here
        context["student_list"] = student_list
        context["student_no"] = student_no
        context["test_marks"] = test_marks
        context["grades_list"] = grades_list
        return render(request, self.template_name, context)

# Student group views
class StudentGroupView(StudentGroupSearch):
    side = "examiner"
    base = "examiner_base.html"

class ExaminerCreateGroup(CreateStudentGroup):
    side = "examiner"
    base = "examiner_base.html"
    redirect_to = "examiner_user:student-group"

class ExaminerEditGroup(EditStudentGroup):
    side = "examiner"
    base = "examiner_base.html"
    redirect_to = "examiner_user:student-group"

class ExaminerAttachCourse(AttachCourse):
    redirect_to = "examiner_user:examiner-edit-group"
    base = "examiner_base.html"

class ExaminerAttachStudent(AttachStudent):
    redirect_to = "examiner_user:examiner-edit-group"
    base = "examiner_base.html"

class ExaminerUnattachStudent(UnattachStudent):
    redirect_to = "examiner_user:examiner-edit-group"

class ExaminerChangeDeadline(ChangeDeadline):
    redirect_to = "examiner_user:examiner-edit-group"

class ExaminerChangeDeadlineCourse(ChangeDeadline):
    redirect_to = "examiner_user:edit-course"
    redirect_arg = "course"

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