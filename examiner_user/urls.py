from django.urls import path

from .views import (ExaminerHomepage, CreateStudent,  CreateExaminer, CreateCourse, SearchCourse, DetailCourse, ControlCourse, 
                    CreateQuestion, SearchQuestion, EditQuestion, DeleteQuestion, CreateLesson, DetailLesson, ViewLesson,
                    EditLessonContent, AttachStudent, UnattachStudents, AttachStudentText, EditLessonTopic, StudentView, DetailStudent, 
                    ExaminerResultView, GenralResultView, CourseResults, Clean_up)

app_name="examiner_user"
urlpatterns = [
    path("homepage/", ExaminerHomepage.as_view(), name="homepage"),
    path("create_examiner/", CreateExaminer.as_view(), name = "create-examiner"),
    path("create_student/", CreateStudent.as_view(), name="create-student"),
    path("create_course/", CreateCourse.as_view(), name="create-course"),
    path("search_course/", SearchCourse.as_view(),name="search-course"),
    path("course/<int:pk>/<slug:slug>", DetailCourse.as_view(), name="detail-course"),
    path("course/edit/<int:pk>/<slug:slug>", ControlCourse.as_view(), name="edit-course"),
    path("course/add/question/<int:pk>/<slug:slug>", CreateQuestion.as_view(), name="create-question"),
    path("course/search_question/<int:pk>/<slug:slug>", SearchQuestion.as_view(), name="search-question"),
    path("course/edit/question/<int:pk>/<slug:slug>", EditQuestion.as_view(), name="edit-question"),
    path("course/delete/question/<int:course>/<int:question>/<slug:slug>", DeleteQuestion.as_view(), name="delete-question"),
    path("course/add/lesson/<int:pk>/<slug:slug>", CreateLesson.as_view(), name="create-lesson"),
    path("course/detail/lesson/<int:pk>/<slug:slug>", DetailLesson.as_view(), name="detail-lesson"),
    path("course/view/lesson/<int:pk>/<slug:slug>", ViewLesson.as_view(), name="view-lesson"),
    path("course/edit/lesson/content/<int:pk>/<slug:slug>", EditLessonContent.as_view(), name="edit-lesson-content"),
    path("course/edit/lesson/topic/<int:pk>/<slug:slug>", EditLessonTopic.as_view(), name="edit-lesson-topic"),
    path("attach/student/<int:pk>/", AttachStudent.as_view(), name="attach-student"),
    path("course/list/students/<int:pk>/<slug:slug>", UnattachStudents.as_view(), name="unattach-students"),
    path("attach/student/text/<int:pk>/<slug:slug>", AttachStudentText.as_view(), name="attach-student-text"),
    path("users", StudentView.as_view(), name="students"),
    path("users/detail/<int:pk>", DetailStudent.as_view(), name="detail-student"),
    path("user/course/results/<int:course>/<int:student>", ExaminerResultView.as_view(), name="results-course-student"),
    path("results", GenralResultView.as_view(), name="results"),
    path("results/course/<int:pk>", CourseResults.as_view(), name="course-results"),
    path("test", Clean_up.as_view(), name="test")
]