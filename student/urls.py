from django.urls import path

from .views import (HomepageView, StudentSearchCourse, StudentDetailCourse, StudentListLesson, StudentAttemptExam,
                    StudentPassExam, StudentQuestion, TestFinish, StudentResultView, StudentResultGeneralView,
                    TestTimeOut, TestDiploma, StudentFeedback, StudentHelp)

app_name="student"
urlpatterns = [
    path("homepage", HomepageView.as_view(), name="homepage"),
    path("course/search", StudentSearchCourse.as_view(), name="student-search-course"),
    path("course/detail/<uuid:pk>/<slug:slug>", StudentDetailCourse.as_view(), name="student-detail-course"),
    path("lesson/list/<uuid:pk>/<slug:slug>", StudentListLesson.as_view(), name="student-list-lesson"),
    path("course/exam/<uuid:pk>/<slug:slug>", StudentAttemptExam.as_view(), name="student-attempt-exam"),
    path("exam/pass/<uuid:pk>", StudentPassExam.as_view(), name="student-pass-exam"),
    path("exam/question/<uuid:pk>", StudentQuestion.as_view(), name="student-question"),
    path("exam/finish/<uuid:pk>", TestFinish.as_view(), name="test-finish"),
    path("exam/finish/timeout/<uuid:pk>", TestTimeOut.as_view(), name="test-timeout"),
    path("course/results/<uuid:pk>", StudentResultView.as_view(), name="course-results"),
    path("results/general", StudentResultGeneralView.as_view(), name="results-general"),
    path("diploma/<uuid:pk>/<int:student>/<slug:slug>", TestDiploma.as_view(), name="diploma"),
    path("feedback", StudentFeedback.as_view(), name="student-feedback"),
    path("help", StudentHelp.as_view(), name="student-help")
]