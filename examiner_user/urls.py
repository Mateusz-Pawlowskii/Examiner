from django.urls import path

from .views import (ExaminerHomepage, CreateStudent, CreateCourse, SearchCourse, DetailCourse, ControlCourse,  CreateQuestion,
                    SearchQuestion, EditQuestion, DeleteQuestion, CreateLesson, DetailLesson, ViewLesson, EditLessonContent,
                    UnattachGroup, AttachCourseText, EditLessonTopic, StudentView, DetailStudent, ExaminerResultView,
                    GenralResultView, CourseResults, CourseGroupResults, StudentGroupView, ExaminerCreateGroup, ExaminerEditGroup,
                    UnattachCourse, ExaminerAttachCourse, ExaminerAttachStudent, ExaminerUnattachStudent, Clean_up)

app_name="examiner_user"
urlpatterns = [
    path("homepage/", ExaminerHomepage.as_view(), name="homepage"),
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
    path("course/list/group/<int:pk>/<slug:slug>", UnattachGroup.as_view(), name="unattach-group"),
    path("group/course/<int:pk>/", UnattachCourse.as_view(), name="examiner-unattach-course"),
    path("attach/course/text/<int:pk>/<slug:slug>", AttachCourseText.as_view(), name="attach-course-text"),
    path("attach/course/text/<int:pk>/", ExaminerAttachCourse.as_view(), name="examiner-attach-course"),
    path("attach/student/<int:pk>/", ExaminerAttachStudent.as_view(), name="examiner-attach-student"),
    path("unattach/student/<int:pk>/", ExaminerUnattachStudent.as_view(), name="examiner-unattach-student"),
    path("users", StudentView.as_view(), name="students"),
    path("users/detail/<int:pk>", DetailStudent.as_view(), name="detail-student"),
    path("user/course/results/<int:course>/<int:student>", ExaminerResultView.as_view(), name="results-course-student"),
    path("results", GenralResultView.as_view(), name="results"),
    path("results/course/<int:pk>", CourseResults.as_view(), name="course-results"),
    path("results/course/group/<int:group>/<int:course>/", CourseGroupResults.as_view(), name="results-course-group"),
    path("student/group/", StudentGroupView.as_view(), name="student-group"),
    path("student/group/create/", ExaminerCreateGroup.as_view(), name="examiner-create-group"),
    path("student/group/edit/<int:pk>", ExaminerEditGroup.as_view(), name="examiner-edit-group"),
    path("test", Clean_up.as_view(), name="test")
]