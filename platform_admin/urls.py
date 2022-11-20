from django.urls import path

from .views import (PlatformHomepage, ExaminerSearch, CreateExaminer, EditExaminer, ChangePassword, DeleteUser, StudentSearch,
                    PlatformCreateStudent, EditStudent, StudentGroupSearch, EditStudentGroup, CreateStudentGroup, AttachStudent,
                    UnattachStudent, AttachCourse, UnattachCourse, SettingsView)

app_name="platform_admin"
urlpatterns = [
    path("homepage/", PlatformHomepage.as_view(), name="homepage"),
    path("examiners/", ExaminerSearch.as_view(), name="examiner-search"),
    path("examiners/create/", CreateExaminer.as_view(), name="create-examiner"),
    path("examiner/edit/<int:pk>/", EditExaminer.as_view(), name="edit-examiner"),
    path("change/password/<int:pk>/", ChangePassword.as_view(), name="change-password"),
    path("delete/user/<int:pk>/", DeleteUser.as_view(), name="delete-user"),
    path("students/", StudentSearch.as_view(), name="student-search"),
    path("students/create", PlatformCreateStudent.as_view(), name="create-student"),
    path("students/edit/<int:pk>/", EditStudent.as_view(), name="edit-student"),
    path("student-group/", StudentGroupSearch.as_view(), name="student-group-search"),
    path("student-group/edit/<int:pk>", EditStudentGroup.as_view(), name="edit-student-group"),
    path("student-group/create/", CreateStudentGroup.as_view(), name="create-student-group"),
    path("student-group/attach/student/<int:pk>/", AttachStudent.as_view(), name="attach-student"),
    path("student-group/unattach/student/<int:pk>/", UnattachStudent.as_view(), name="unattach-student"),
    path("student-group/attach/course/<int:pk>/", AttachCourse.as_view(), name="attach-course"),
    path("student-group/unattach/course/<int:pk>/", UnattachCourse.as_view(), name="unattach-course"),
    path("settings/", SettingsView.as_view(), name="settings")
]