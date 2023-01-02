from django.urls import path

from .views import (PlatformHomepage, ExaminerSearch, CreateExaminer, EditExaminer, ChangePassword, DeleteUser, StudentSearch,
                    PlatformCreateStudent, EditStudent, StudentGroupSearch, EditStudentGroup, CreateStudentGroup, AttachStudent,
                    UnattachStudent, AttachCourse, UnattachCourse, SettingsView, DeleteGroup, PlatformDetailCourse, ChangeDeadline,
                    CreateGradeView, DeleteGradeView, DefaultGrades, GroupReport, FeedbackView, PlatformHelp, Clean_up)

app_name="platform_admin"
urlpatterns = [
    path("homepage", PlatformHomepage.as_view(), name="homepage"),
    path("examiners", ExaminerSearch.as_view(), name="examiner-search"),
    path("examiners/create", CreateExaminer.as_view(), name="create-examiner"),
    path("examiner/edit/<int:pk>/<slug:slug>", EditExaminer.as_view(), name="edit-examiner"),
    path("change/password/<int:pk>", ChangePassword.as_view(), name="change-password"),
    path("delete/user/<int:pk>", DeleteUser.as_view(), name="delete-user"),
    path("students", StudentSearch.as_view(), name="student-search"),
    path("students/create", PlatformCreateStudent.as_view(), name="create-student"),
    path("students/edit/<int:pk>/<slug:slug>", EditStudent.as_view(), name="edit-student"),
    path("student-group", StudentGroupSearch.as_view(), name="student-group-search"),
    path("student-group/edit/<uuid:pk>/<slug:slug>", EditStudentGroup.as_view(), name="edit-student-group"),
    path("student-group/create", CreateStudentGroup.as_view(), name="create-student-group"),
    path("student-group/attach/student/<uuid:pk>", AttachStudent.as_view(), name="attach-student"),
    path("student-group/unattach/student/<uuid:pk>", UnattachStudent.as_view(), name="unattach-student"),
    path("student-group/attach/course/<uuid:pk>", AttachCourse.as_view(), name="attach-course"),
    path("student-group/unattach/course/<uuid:pk>", UnattachCourse.as_view(), name="unattach-course"),
    path("settings", SettingsView.as_view(), name="settings"),
    path("student-group/delete/<uuid:pk>", DeleteGroup.as_view(), name="delete-group"),
    path("student-group/course/<uuid:group>/<uuid:pk>", PlatformDetailCourse.as_view(), name="platform-detail-course"),
    path("deadline/change/<uuid:pk>/<uuid:course>", ChangeDeadline.as_view(), name="change-deadline"),
    path("settings/grade/create", CreateGradeView.as_view(), name="create-grade"),
    path("settings/grade/delete/<uuid:pk>", DeleteGradeView.as_view(), name="delete-grade"),
    path("settings/grade/default/<str:grading_sys>", DefaultGrades.as_view(), name="default-grades"),
    path("student-group/raport/<uuid:group>/<uuid:course>/<slug:slug>", GroupReport.as_view(), name="group-report"),
    path("feedback", FeedbackView.as_view(), name="platform-feedback"),
    path("help", PlatformHelp.as_view(), name="platform-help"),
    path("test", Clean_up.as_view(), name="test")
]