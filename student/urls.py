from django.urls import path

from .views import (HomepageView, StudentSearchCourse, StudentDetailCourse, StudentListLesson, StudentAttemptExam, StudentPassExam,
                    StudentQuestion, TestFinish, StudentResultView, StudentResultGeneralView, TestTimeOut, TestDiploma)

app_name="student"
urlpatterns = [
    path("homepage", HomepageView.as_view(), name="homepage"),
    path("course/search", StudentSearchCourse.as_view(), name="student-search-course"),
    path("course/detail/<int:pk>/<slug:slug>", StudentDetailCourse.as_view(), name="student-detail-course"),
    path("lesson/list/<int:pk>/<slug:slug>", StudentListLesson.as_view(), name="student-list-lesson"),
    path("course/exam/<int:pk>/<slug:slug>", StudentAttemptExam.as_view(), name="student-attempt-exam"),
    path("exam/pass/<int:pk>", StudentPassExam.as_view(), name="student-pass-exam"),
    path("exam/question/<int:pk>", StudentQuestion.as_view(), name="student-question"),
    path("exam/finish/<int:pk>", TestFinish.as_view(), name="test-finish"),
    path("exam/finish/timeout/<int:pk>", TestTimeOut.as_view(), name="test-timeout"),
    path("course/results/<int:pk>", StudentResultView.as_view(), name="course-results"),
    path("results/general", StudentResultGeneralView.as_view(), name="results-general"),
    path("diploma/<int:pk>/<int:student>/<slug:slug>", TestDiploma.as_view(), name="diploma")
]