from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.http import FileResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
import random
import datetime
from django.contrib import messages
from fpdf import FPDF

from exam.models import Course, Lesson, Question, Result
from exam.functions import test_mark
from .forms import StudentSearchCourseForm, StudentSearchStatusForm


# Create your views here.
class HomepageView(TemplateView):
    template_name = "student_homepage.html"
    extra_context= {"nav_var":"homepage"}

class StudentSearchCourse(LoginRequiredMixin, View):
    template_name = "student_search_course.html"

    def get(self, request, *args, **kwargs):
        student = request.user
        courses = Course.objects.filter(students=student)
        test_marks = test_mark(courses, student)
        categories = []
        for course in courses:
            categories.append(course.category)
        categories = set(categories)
        context = {"student" : student,
                   "courses" : courses,
                   "test_marks" : test_marks,
                   "nav_var" : "search_course",
                   "form1" : StudentSearchCourseForm(),
                   "form2" : StudentSearchStatusForm(),
                   "categories" : categories}
        return render(request, self.template_name, context)

class StudentDetailCourse(LoginRequiredMixin, View):
    template_name = "student_detail_course.html"

    def get(self, request, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        context = {"course":course,
                   "student": request.user}
        # this code is related to diploma feature and I don't know if it should exist
        user = request.user
        results = Result.objects.filter(student = user, course = course)
        for result in results:
            if result.passed == True:
                context["passed"] = True
                break
        return render(request, self.template_name, context)

class StudentListLesson(LoginRequiredMixin, View):
    template_name = "student_list_lesson.html"

    def get(self, request, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        lessons = Lesson.objects.filter(course=course)
        context = {"lessons" : lessons}
        return render(request, self.template_name, context)

# Part about Examination starts here
class StudentAttemptExam(LoginRequiredMixin, View):
    template_name = "student_attempt_exam.html"

    def get(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        results = Result.objects.filter(course=course, student=request.user)
        used_attempts = len(results)
        total_attempts = course.attempt_amount
        remaining_attempts = total_attempts - used_attempts
        context = {"course" : course,
                   "total_attempts" : total_attempts,
                   "remaining_attempts" : remaining_attempts}
        return render(request, self.template_name, context)

class StudentPassExam(LoginRequiredMixin, View):
    template_name = "student_pass_exam.html"

    def get(self, request, **kwargs):
        student_results = Result.objects.filter(student = request.user)
        for result in student_results:
            if result.finished is False:
                return redirect(reverse_lazy("student:student-question", kwargs={"pk":result.pk}))
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        return redirect(reverse_lazy("student:student-attempt-exam", kwargs={"pk":course.pk}))

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        questions = Question.objects.filter(course=course)
        raw_question_amount = len(questions)
        stated_question_amount = course.question_amount
        # safety measure to prevent starting tests which have less questions prepered than questions for display or when there are
        # no questions to display
        if stated_question_amount > raw_question_amount or stated_question_amount == 0 or course.test_ready == False:
            messages.error(request, "Kurs nie jest gotowy")
            return redirect(reverse_lazy("student:student-attempt-exam", kwargs={"pk":course.pk}))
        student_results = Result.objects.filter(student = request.user)
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
        result.end_time = datetime.datetime.now() + datetime.timedelta(minutes=course.time)
        result.save()
        return redirect(reverse_lazy("student:student-question", kwargs={"pk":result.pk}))

class StudentQuestion(LoginRequiredMixin, View):
    template_name = "student_question.html"

    def get(self, request, *args, **kwargs):
        result = get_object_or_404(Result, pk=self.kwargs["pk"])
        course = result.course
        questions = Question.objects.filter(course=course)
        question = questions[result.get_order()[result.current_question-1]-1]
        context = {"question" : question,
                   "result" : result}
        if course.time > 0:
            end_time = result.end_time.strftime("%m/%d/%Y, %H:%M:%S")
            context["end_time"] = end_time
            context["now"] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        if course.multiple_answer_questions == True:
            return render(request, "student_multiple_question.html", context)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        result = get_object_or_404(Result, pk=self.kwargs["pk"])
        course = result.course
        questions = Question.objects.filter(course=course)
        question = questions[result.get_order()[result.current_question-1]-1]
        if course.multiple_answer_questions == False:
            if question.correct_answers == request.POST.get("correct_answers"):
                result.current_score += 1
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
                result.current_score += 1
        result.current_question += 1
        result.save()
        if result.current_question > course.question_amount:
            return redirect(reverse_lazy("student:test-finish", kwargs={"pk":result.pk}))
        return redirect(reverse_lazy("student:student-question", kwargs={"pk":result.pk}))

class TestFinish(LoginRequiredMixin, View):
    template_name = "student_test_finished.html"
    timeout = False

    def get(self, request, *args, **kwargs):
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
                   "timeout" : self.timeout}
        return render(request, self.template_name, context)

class TestTimeOut(TestFinish):
    timeout = True

# This code is related to diploma feature, I don't know if it's a good idea to use
class TestDiploma(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs["student"])
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        results = Result.objects.filter(course = course, student = user)
        best_result = max(results, key = lambda x : x.current_score)
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'font/ttf/DejaVuSerif.ttf', uni=True)
        pdf.set_font('DejaVu', '', 50)
        pdf.image("static/img/diploma.png",0,0,210,297)
        pdf.image("static/img/logo_dip.png",60,20,100,25)
        pdf.cell(0, 50, txt = "", ln = 1, align = 'C')
        pdf.cell(0, 20, txt = "Dyplom", ln = 1, align = 'C')
        pdf.set_font('DejaVu', '', 17)
        pdf.cell(0, 20, txt = f"{user.username}", ln = 1, align = 'C')
        pdf.set_font('DejaVu', '', 17)
        pdf.cell(0, 15, txt = "ukończył kurs", ln = 1, align = 'C')
        pdf.set_font('DejaVu', '', 17)
        pdf.cell(0, 15, txt = f"{course.name}", ln = 1, align = 'C')
        pdf.set_font('DejaVu', '', 17)
        pdf.cell(0, 15, txt = "z wynikiem pozytywnym", ln = 1, align = 'C')
        pdf.cell(0, 15, txt = f"uzyskując {best_result.current_score} na {course.question_amount} możliwych punktów", ln = 1, align = 'C')
        # pdf.cell(0, 5, txt = f"Dyplom zaliczenia kursu {course.name}", ln = 1, align = 'C')
        # pdf.cell(0, 10, txt = f"z wynikiem {best_result.current_score} na {course.question_amount} przez studenta {user.username}", ln = 1, align = 'C')
        pdf.cell(0, 50, txt = "Gratulujemy i życzymy dlaszego powodzenia w nauce", ln = 1, align = 'C')
        pdf.output(f"media/diploma/{course.name}_{user.username}.pdf")
        return FileResponse(open(f"media/diploma/{course.name}_{user.username}.pdf", "rb"), content_type="application/pdf")
    
# part about results starts here
class StudentResultView(LoginRequiredMixin, View):
    template_name = "student_result_view.html"

    def get(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        results = Result.objects.filter(course=course, student=request.user)
        perc = []
        for result in results:
            perc.append(round(100*result.current_score/course.question_amount))
        context = {"course" : course,
                   "results" : zip(results, perc)}
        return render(request, self.template_name, context)

class StudentResultGeneralView(LoginRequiredMixin, View):
    queryset = Course.objects.all()
    template_name="student_results_general.html"

    def get(self, request, *args, **kwargs):
        student_courses = Course.objects.filter(students = request.user)
        student_marks = test_mark(student_courses, request.user)
        categories = []
        for course in student_courses:
            categories.append(course.category)
        categories = set(categories)
        context = {"nav_var": "results",
                   "courses": student_courses,
                   "marks" : student_marks,
                   "form1" : StudentSearchCourseForm(),
                   "form2" : StudentSearchStatusForm(),
                   "categories" : categories
                   }
        return render(request, self.template_name, context)