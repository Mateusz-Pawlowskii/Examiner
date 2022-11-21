from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, View, TemplateView
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import FileResponse
from django.http import HttpResponseRedirect
from operator import attrgetter

from .forms import (CourseForm, QuestionForm, QuestionFormMultiple, LessonForm, AttachCourseToGroupForm, AttachStudentTextForm, 
                    LessonRenameForm, LessonEditForm, CourseEditForm, AttachCourseTextForm)
from exam.models import Course, Lesson, Question, Result, Platform, StudentGroup
from student.forms import StudentSearchCourseForm
from exam.functions import test_mark, course_mark
# Create your views here.

class ExaminerHomepage(LoginRequiredMixin, View):
    template_name = "examiner_homepage.html"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var":"homepage",
                   "platform" : platform}
        return render(request, self.template_name, context)

# part about users starts here
class StudentView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "students.html"
    permission_required = ("auth.view_user")

    def get(self, request):
        platform = Platform.objects.get(users=request.user)
        context = {"nav_var" : "users",
                   "object_list" : User.objects.filter(groups=2, platform=platform),
                   "form" : StudentSearchCourseForm(),
                   "platform" : platform}
        return render(request, self.template_name, context)

class DetailStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "detail_student.html"
    permission_required = ("auth.view_user")
    form_class = AttachCourseTextForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        student = get_object_or_404(User, pk=self.kwargs["pk"])
        courses = Course.objects.filter(students=student)
        all_courses = Course.objects.filter(platform=platform)
        test_marks = test_mark(courses, student)
        context = {"student" : student,
                   "courses" : courses,
                   "test_marks" : test_marks,
                   "form" : self.form_class(),
                   "platform" : platform,
                   "all_courses" : all_courses}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, name=request.POST["course"])
        student = get_object_or_404(User, pk=self.kwargs["pk"])
        course.students.add(student)
        course.student_amount += 1
        course.save()
        return redirect(reverse_lazy("examiner_user:detail-student", kwargs={"pk":self.kwargs["pk"]}))

class CreateStudent(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "create_student.html"
    permission_required = ("auth.add_user")
    redirect = "examiner_user:students"

    def get(self, request):
        platform = Platform.objects.get(users=request.user)
        form = UserCreationForm()
        context = {"form" : form,
                   "platform" : platform}
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            group = get_object_or_404(Group, name="Student")
            platform = Platform.objects.get(users=request.user)
            users = User.objects.all()
            user = users.order_by('-date_joined').first()
            group.user_set.add(user)
            platform.users.add(user)
            user.save()
        else:
            messages.error(request, "Niepoprawne dane")
        return redirect(reverse_lazy(self.redirect))

class AttachCourseText(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("auth.change_user")
    form_class = AttachStudentTextForm

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(StudentGroup, name=request.POST["group"])
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        group.courses.add(course)
        group.save()
        return redirect(reverse_lazy("examiner_user:edit-course", kwargs={"pk":self.kwargs["pk"],"slug":self.kwargs["slug"]}))

class UnattachGroup(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")
    
    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        group = get_object_or_404(StudentGroup, pk=request.POST["group"])
        group.courses.remove(course)
        group.save()
        return redirect(reverse_lazy("examiner_user:edit-course", kwargs={"pk":self.kwargs["pk"], "slug":self.kwargs["slug"]}))

# part about courses starts here
class CreateCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.add_course")
    template_name="create_course.html"
    form_class = CourseForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context = {"form" : self.form_class(),
                   "platform" : platform}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            platform = Platform.objects.get(users=request.user)
            courses = Course.objects.all()
            course = courses.last()
            platform.course_set.add(course)
            course.save()
            messages.info(request, "Kurs został pomyślnie utworzony")
            return redirect(reverse_lazy("examiner_user:search-course"))
        messages.error(request, "Nie udało się stworzyć kursu")
        return HttpResponseRedirect(self.request.path_info)

class SearchCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.view_course")
    template_name="search_course.html"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        queryset = Course.objects.filter(platform=platform)
        categories = []
        for course in queryset:
            categories.append(course.category)
        categories = set(categories)
        context = {"nav_var":"search_course",
                     "form" : StudentSearchCourseForm(),
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
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        allowed_courses = Course.objects.filter(platform=platform)
        context = {"object" : course,
                   "questions" : Question.objects.filter(course=course),
                   "lessons" : Lesson.objects.filter(course=course),
                   "students" : User.objects.filter(course=course),
                   "platform" : platform}
        if course in allowed_courses:
            return render(request, self.template_name, context)
        messages.error(request, "Nie udało się odnaleźc kursu kursu")
        return redirect(reverse_lazy("examiner_user:search-course"))

class ControlCourse(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.change_course")
    template_name="control_course.html"
    form_class = CourseEditForm

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        if course not in Course.objects.filter(platform=platform):
            messages.error(request, "Brak uprawnień")
            return redirect(reverse_lazy("examiner_user:search-course"))
        course_form = self.form_class(instance=course)
        lesson_list = Lesson.objects.filter(course=course)
        context = {"object" : course,
                   "course_form" : course_form,
                   "lesson_form" : LessonForm(initial={"course" : course}),
                   "lesson_list" : lesson_list,
                   "group_form" : AttachCourseToGroupForm(initial={"course" : course}),
                   "student_groups" : StudentGroup.objects.filter(platform=platform),
                   "platform" : platform
                   }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        if request.POST["multiple_answer_questions"] == "on":
            course.multiple_answer_questions = True
        else:
            course.multiple_answer_questions = False
        form = self.form_class(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("examiner_user:detail-course", kwargs={"pk":course.pk, "slug":self.kwargs["slug"]}))
        else:
            messages.error(request, "Informacje dotyczące kursu zostały niepoprawnie wypełnione")
            return HttpResponseRedirect(self.request.path_info)

# part about questions starts here
class CreateQuestion(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ("exam.add_question")
    queryset = Course.objects.all()
    template_name="create_question.html" 
    form_class = QuestionForm
        
    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        pk = self.kwargs["pk"]
        course_=get_object_or_404(Course, pk=pk)
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
        pk = self.kwargs["pk"]
        course_=get_object_or_404(Course, pk=pk)
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
            messages.error(request, "Poprawna odpowiedź została źle zaznaczona")
        return HttpResponseRedirect(self.request.path_info)

class SearchQuestion(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "search_question.html"
    permission_required = ("exam.view_question")

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course_pk = self.kwargs["pk"]
        course_ = get_object_or_404(Course, pk=course_pk)
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

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(Question, pk=pk)

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        question = self.get_object()
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
            messages.error(request, "Poprawna odpowiedź została źle zaznaczona")
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

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course_ = get_object_or_404(Course, pk=self.kwargs["pk"])
        form = self.form_class(initial={"course":course_})
        context = {"form" : form,
                   "course" : course_,
                   "platform" : platform}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        course_ = get_object_or_404(Course, pk=self.kwargs["pk"])
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            course_.lesson_amount += 1
            course_.save()
        else:
            messages.error(request, "Niepoprawny plik")
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
            return FileResponse(open(f"media/{lesson.material}", "rb"), content_type="application/pdf")
        else:
            return FileResponse(open(f"media/{lesson.material}", "rb"), as_attachment=True)

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
            messages.error(request, "Należy podać nowy maretiał przy zmianie materiału")
            return redirect(reverse_lazy("examiner_user:detail-lesson", kwargs={"pk":self.kwargs["pk"]}))
        if self.allowed_file(file.name):
            if form.is_valid():
                lesson.material.delete(lesson.material.name)
                form.save()
        else:
            messages.error(request, "Niepoprawne rozszerzenie pliku")
        return redirect(reverse_lazy("examiner_user:detail-lesson", kwargs={"pk":self.kwargs["pk"]}))

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
            messages.error(request, "Niepoprawna nazwa tematu lekcji")
        return redirect(reverse_lazy("examiner_user:detail-lesson", kwargs={"pk":self.kwargs["pk"]}))

# Result views
class GenralResultView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "results.html"
    permission_required = ("exam.view_result")

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        courses = Course.objects.all()
        context = {"course_data" : courses,
                   "nav_var" : "results",
                   "form" : StudentSearchCourseForm(),
                   "platform" : platform}
        return render(request, self.template_name, context)

class ExaminerResultView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "results_course_student.html"
    permission_required = ("auth.view_user")

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["course"])
        student = get_object_or_404(User, pk=self.kwargs["student"])
        results = Result.objects.filter(course=course, student=student)
        perc = []
        for result in results:
            perc.append(round(100*result.current_score/course.question_amount))
        context = {"course" : course,
                   "results" : zip(results , perc),
                   "student" : student,
                   "platform" : platform}
        return render(request, self.template_name, context)

class CourseResults(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "course_results.html"
    permission_required = ("auth.view_user")

    def get_maximum_result(self, student, course):
        results = Result.objects.filter(course=course, student=student)
        if results:
            result = max(results, key=attrgetter("current_score")).current_score
            return result
        return 0

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        students = User.objects.filter(course=course)
        context = {"course" : course,
                   "students" : students,
                   "platform" : platform}
        context["questions"] = Question.objects.filter(course=course)
        context["lessons"] = Lesson.objects.filter(course=course)
        context["students"] = User.objects.filter(course=course)
        course_information = {"pk" : course.pk,
                                "name" : course.name,
                                "passed_students" : 0,
                                "failed_students" : 0,
                                "current_students" : 0,
                                "passed_results" : 0,
                                "failed_results" : 0
                                }
        for student in User.objects.filter(groups=2, course=course):
            if test_mark([course], student)[0] == "Zaliczony":
                course_information["passed_students"] += 1
            elif test_mark([course], student)[0] == "Niezaliczony":
                course_information["failed_students"] += 1
            else:
                course_information["current_students"] += 1
            results = Result.objects.filter(course=course)
            for result in results:
                if result.passed == True:
                    course_information["passed_results"] += 1
                else:
                    course_information["failed_results"] += 1
        context["course_information"] = course_information
        context["test_marks"] = course_mark(course, students)
        # Part for graphs starts here
        passed_no = context["test_marks"].count("Zaliczony")
        failed_no = context["test_marks"].count("Niezaliczony")
        not_yet_mark_no = context["test_marks"].count("Jeszcze nie ukończony")
        context["pass_list"] = [ "Zaliczony", "Niezaliczony", "Jeszcze nie ukończony"]
        context["pass_no"] = [passed_no, failed_no, not_yet_mark_no]
        student_list = []
        student_no = []
        students = sorted(students, key = lambda student: self.get_maximum_result(student, course), reverse=True)
        for student in students:
            results = Result.objects.filter(course=course, student=student)
            if results:
                result = max(results, key=attrgetter("current_score"))
                student_no.append(100 * result.current_score/course.question_amount)
                student_list.append(student.username)
        context["student_list"] = student_list
        context["student_no"] = student_no
        return render(request, self.template_name, context)

# Test views
# Selenium cleans up the database on its own only when models are created with objectModel.create() methods and
# does not clean the database after selenium-created views so I needed a seprate view for tearDown
class Clean_up(View):
    def get(self, request, *args, **kwargs):
        while Course.objects.filter(name="Niezaliczony").first():
            Course.objects.filter(name="Niezaliczony").first().delete()
        while Course.objects.filter(name="Brak czasu").first():
            Course.objects.filter(name="Brak czasu").first().delete()
        while Course.objects.filter(name="Testowa nazwa kursu").first():
            Course.objects.filter(name="Testowa nazwa kursu").first().delete()
        if Course.objects.filter(name="Edytowana nazwa kursu").first():
            Course.objects.filter(name="Edytowana nazwa kursu").first().delete()
        if User.objects.filter(username="testowyStudent").first():
            User.objects.filter(username="testowyStudent").first().delete()
        return redirect(reverse_lazy("exam:home-redirect"))