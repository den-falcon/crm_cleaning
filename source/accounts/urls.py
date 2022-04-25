from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from accounts.views.accounts import (StaffProfileView,
                                     StaffRegisterView,
                                     StaffListView,
                                     StaffEditView,
                                     StaffBlackListView,
                                     StaffEditPhoto,
                                     PasswordChangeView,
                                     StaffDeleteView,
                                     AddToBlackList,
                                     RemoveFromBlackList)

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(template_name="account/login.html"), name='login'),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('register/', StaffRegisterView.as_view(), name='register'),
    path("password_change/", PasswordChangeView.as_view(), name="change_password"),
    path('staff/', StaffListView.as_view(), name='staff-list'),
    path('staff/<int:pk>/', StaffProfileView.as_view(), name='profile'),
    path('staff/edit/<int:pk>/', StaffEditView.as_view(), name='staff-edit'),
    path('staff/edit/photo/<int:pk>/', StaffEditPhoto.as_view(), name='staff-photo'),
    path('delete/staff/<int:pk>/', StaffDeleteView.as_view(), name='staff-delete'),
    path('black_list/', StaffBlackListView.as_view(), name='black-list'),
    path('black_list/add/<int:pk>/', AddToBlackList.as_view(), name='black-list-add'),
    path('black_list/remove/<int:pk>/', RemoveFromBlackList.as_view(), name='black-list-remove'),
]
