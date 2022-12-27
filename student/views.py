from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.http import FileResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
import random
import datetime
from django.contrib import messages
from fpdf import FPDF
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now as timezone_now
from django.utils.text import slugify

from exam.models import Course, Lesson, Question, Result, Platform, StudentGroup, Deadline
from exam.functions import get_courses_for_student, get_categories, get_timeover, get_grade_data, student_grades
from platform_admin.views import FeedbackView
from .forms import StudentSearchCourseForm, StudentSearchStatusForm

# Create your views here.
class HomepageView(View):
    template_name = "student_homepage.html"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        context= {"nav_var":"homepage",
                  "platform" : platform}
        return render(request, self.template_name, context)

class StudentFeedback(FeedbackView):
    side = "student"
    base = "student_base.html"

class StudentHelp(View):
    def get(self, request, *args, **kwargs):
        return FileResponse(open(f"static/help/student_{request.LANGUAGE_CODE}.pdf", "rb"), content_type="application/pdf")

# Course views start here
class StudentSearchCourse(LoginRequiredMixin, View):
    template_name = "student_search_course.html"
    form_class_1 = StudentSearchCourseForm
    form_class_2 = StudentSearchStatusForm

    def get(self, request, *args, **kwargs):
        student = request.user
        platform = Platform.objects.get(users=student)
        data = get_courses_for_student(student)
        grades_list = student_grades(data[2], student)
        categories = get_categories(data[0])
        context = {"student" : student,
                   "courses" : data[0],
                   "test_marks" : data[1],
                   "nav_var" : "search_course",
                   "form1" : self.form_class_1(),
                   "form2" : self.form_class_2(),
                   "categories" : categories,
                   "grades" : get_grade_data(platform),
                   "grades_list" : grades_list,
                   "platform" : platform}
        return render(request, self.template_name, context)

class StudentDetailCourse(LoginRequiredMixin, View):
    template_name = "student_detail_course.html"

    def get_deadline(self, request, course):
        user = request.user
        deadlines = []
        groups = StudentGroup.objects.filter(students=user, courses=course)
        for group in groups:
            deadlines.append(Deadline.objects.filter(group=group, course=course).first())
        deadline = sorted(deadlines, key = lambda deadline:deadline.time)[-1]
        if deadline.time < timezone_now():
            timeover = True
        else:
            timeover = False
        return (deadline.time, timeover)

    def check_passed(self, request, course):
        """this code checks if the student passed in order to display them diploma link"""
        user = request.user
        results = Result.objects.filter(student = user, course = course)
        for result in results:
            if result.passed == True:
                return True
        return False

    def get(self, request, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        deadline = self.get_deadline(request, course)
        context = {"course":course,
                   "student": request.user,
                   "deadline" : deadline,
                   "platform" : platform}
        context["passed"] = self.check_passed(request, course)
        return render(request, self.template_name, context)

class StudentListLesson(LoginRequiredMixin, View):
    template_name = "student_list_lesson.html"

    def get(self, request, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        lessons = Lesson.objects.filter(course=course)
        context = {"lessons" : lessons,
                   "platform" : platform}
        return render(request, self.template_name, context)

# Part about Examination starts here
class StudentAttemptExam(LoginRequiredMixin, View):
    template_name = "student_attempt_exam.html"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        results = Result.objects.filter(course=course, student=request.user)
        used_attempts = len(results)
        total_attempts = course.attempt_amount
        remaining_attempts = total_attempts - used_attempts
        context = {"course" : course,
                   "total_attempts" : total_attempts,
                   "remaining_attempts" : remaining_attempts,
                   "platform" : platform}
        return render(request, self.template_name, context)

class StudentPassExam(LoginRequiredMixin, View):
    template_name = "student_pass_exam.html"

    def get(self, request, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        student_results = Result.objects.filter(student = request.user, course=course)
        for result in student_results:
            if result.finished is False:
                return redirect(reverse_lazy("student:student-question", kwargs={"pk":result.pk}))
        return redirect(reverse_lazy("student:student-attempt-exam", kwargs={"pk":course.pk}))

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        questions = Question.objects.filter(course=course)
        raw_question_amount = len(questions)
        stated_question_amount = course.question_amount
        # safety measure to prevent starting tests which have less questions prepered than questions for display or when there are
        # no questions to display
        if stated_question_amount > raw_question_amount or stated_question_amount == 0 or course.test_ready == False:
            messages.error(request, _("Course isn't ready"))
            return redirect(reverse_lazy("student:student-attempt-exam", kwargs={"pk":course.pk, "slug" : slugify(course.name)}))
        student_results = Result.objects.filter(student = request.user, course=course)
        for result in student_results:
            if result.finished is False:
                return redirect(reverse_lazy("student:student-question", kwargs={"pk":result.pk}))
        question_order = []
        while stated_question_amount > len(question_order):
            num = random.randint(1,raw_question_amount)
            if num not in question_order:
                question_order.append(num)
        result = Result(course = course,
                        student = request.user)
        result.set_order(question_order)
        result.end_time = timezone_now() + datetime.timedelta(minutes=course.time)
        result.save()
        return redirect(reverse_lazy("student:student-question", kwargs={"pk":result.pk}))

class StudentQuestion(LoginRequiredMixin, View):
    template_name = "student_question.html"

    def end_time(self, context, result):
        """It gives information about finish time to page"""
        end_time = result.end_time.strftime("%m/%d/%Y, %H:%M:%S")
        context["end_time"] = end_time
        context["now"] = timezone_now().strftime("%m/%d/%Y, %H:%M:%S")
        return context

    def evaluate_answer(self, request, course, question):
        """Checks if the answer is correct and returns 1 when it is and 0 when not"""
        if course.multiple_answer_questions == False:
            if question.correct_answers == request.POST.get("correct_answers"):
                return 1
            return 0
        else:
            score_bar = len(question.correct_answers)
            internal_points = 0
            wrong_answer = False
            for n in range(1,6):
                if f"che{n}" in request.POST:
                    if request.POST.get(f"che{n}") in question.correct_answers:
                        internal_points += 1
                    else:
                        wrong_answer = True
            if wrong_answer == False and score_bar == internal_points:
                return 1
            return 0

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        result = get_object_or_404(Result, pk=self.kwargs["pk"])
        course = result.course
        questions = Question.objects.filter(course=course)
        question = questions[result.get_order()[result.current_question-1]-1]
        context = {"question" : question,
                   "result" : result,
                   "platform" : platform}
        if course.time > 0:
            context = self.end_time(context, result)
        if course.multiple_answer_questions == True:
            return render(request, "student_multiple_question.html", context)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        result = get_object_or_404(Result, pk=self.kwargs["pk"])
        course = result.course
        questions = Question.objects.filter(course=course)
        question = questions[result.get_order()[result.current_question-1]-1]
        result.current_score += self.evaluate_answer(request, course, question)
        result.current_question += 1
        result.save()
        if result.current_question > course.question_amount:
            return redirect(reverse_lazy("student:test-finish", kwargs={"pk":result.pk}))
        return redirect(reverse_lazy("student:student-question", kwargs={"pk":result.pk}))

class TestFinish(LoginRequiredMixin, View):
    template_name = "student_test_finished.html"
    timeout = False

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        result = get_object_or_404(Result, pk=self.kwargs["pk"])
        result.finished = True
        result.save()
        course = result.course
        max_score = course.question_amount
        if result.current_score >= course.passing_score:
            result.passed = True
            result.save()
        context = {"result" : result,
                   "max_score" : max_score,
                   "timeout" : self.timeout,
                   "perc" : round((result.current_score/max_score)*100),
                   "platform" : platform}
        return render(request, self.template_name, context)

class TestTimeOut(TestFinish):
    timeout = True

class TestDiploma(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        user = get_object_or_404(User, pk=self.kwargs["student"])
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        results = Result.objects.filter(course = course, student = user)
        best_result = max(results, key = lambda x : x.current_score)
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'static/font/ttf/DejaVuSerif.ttf', uni=True)
        pdf.set_font('DejaVu', '', 50)
        pdf.image("static/img/diploma.png",0,0,210,297)
        print("platform logo is ->", platform.logo)
        if platform.logo:
            pdf.image(f"media/logos/{platform.logo}",65,20,80,40)
        else:
            pdf.image("static/img/logo_dip.png",60,20,100,25)
        pdf.cell(0, 50, txt = "", ln = 1, align = 'C')
        pdf.cell(0, 30, txt = _("Diploma"), ln = 1, align = 'C')
        pdf.set_font('DejaVu', '', 17)
        pdf.cell(0, 20, txt = f"{user.username}", ln = 1, align = 'C')
        pdf.cell(0, 15, txt = _("finished course"), ln = 1, align = 'C')
        pdf.cell(0, 15, txt = f"{course.name}", ln = 1, align = 'C')
        pdf.cell(0, 15, txt = _("with passing result"), ln = 1, align = 'C')
        perc = round((best_result.current_score/course.question_amount)*100)
        pdf.cell(0, 15, txt = _("achieving %(perc)s percent") % {"perc" : perc}, ln = 1, align = 'C')
        pdf.cell(0, 15, txt = _("by getting %(result)s out of %(max_score)s points") % 
        {"result" : best_result.current_score, "max_score" : course.question_amount}, ln = 1, align = 'C')
        pdf.cell(0, 50, txt = _("Congratualtions, we wish further successes in studies"), ln = 1, align = 'C')
        pdf.output("media/diploma/diploma.pdf")
        return FileResponse(open("media/diploma/diploma.pdf", "rb"), content_type="application/pdf")
    
# part about results starts here
class StudentResultView(LoginRequiredMixin, View):
    template_name = "student_result_view.html"

    def get(self, request, *args, **kwargs):
        platform = Platform.objects.get(users=request.user)
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        results = Result.objects.filter(course=course, student=request.user)
        perc = []
        for result in results:
            perc.append(round(100*result.current_score/course.question_amount))
        context = {"course" : course,
                   "results" : zip(results, perc),
                   "platform" : platform}
        return render(request, self.template_name, context)

class StudentResultGeneralView(LoginRequiredMixin, View):
    queryset = Course.objects.all()
    template_name="student_results_general.html"
    form_class_1 = StudentSearchCourseForm
    form_class_2 = StudentSearchStatusForm

    def get(self, request, *args, **kwargs):
        student = request.user
        platform = Platform.objects.get(users=student)
        data = get_courses_for_student(student)
        grades_list = student_grades(data[2], student)
        categories = get_categories(data[0])
        context = {"nav_var": "results",
                   "courses": data[0],
                   "marks" : data[1],
                   "form1" : self.form_class_1(),
                   "form2" : self.form_class_2(),
                   "categories" : categories,
                   "grades" : get_grade_data(platform),
                   "grades_list" : grades_list,
                   "platform" : platform}
        return render(request, self.template_name, context)