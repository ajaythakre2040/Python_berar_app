from django.urls import path
from rest_framework.routers import DefaultRouter

from ems.views.branch_view import TblBranchListCreateView, TblBranchDetailView
from ems.views.city_master import CityMasterDetailAPIView, CityMasterListCreateAPIView
from ems.views.dealer_view import DealerDetailView, DealerListCreateView
from ems.views.department_view import (
    TblDepartmentListCreateView,
    TblDepartmentDetailView,
)
from ems.views.designation_view import (
    ParentDesignationsView,
    TblDesignationListCreateView,
    TblDesignationDetailView,
)

from ems.views.import_emp_csv_view import UploadCSVView
from ems.views.menu_view import (
    MenuListCreateView,
    MenuDetailView,
    GetAllParentMenuView,
    GetMenuByPortalIdView,
)
from ems.views.portal_view import PortalListCreateView, PortalDetailView
from ems.views.emp_basic_profile_views import (
    EmpBasicProfileListCreateView,
    EmpBasicProfileDetailView,
)
from ems.views.emp_address_details_views import (
    EmpAddressDetailsListCreateView,
    EmpAddressDetailsDetailView,
)
from ems.views.emp_bank_details_views import (
    EmpBankDetailsListCreateView,
    EmpBankDetailsDetailView,
)
from ems.views.emp_nominee_views import (
    EmpNomineeDetailsListCreateView,
    EmpNomineeDetailsDetailView,
)
from ems.views.emp_official_information_view import EmpOfficialInfoView, EmpOfficialInfoDetailView

from ems.views.role_permission_view import RolePermissionDetailView, RolePermissionListCreateView
from ems.views.role_view import RoleDetailView, RoleListCreateView
from ems.views.state_master import StateDetailAPIView, StateListCreateAPIView
from ems.views.subdealer_view import SubDealerDetailView, SubDealerListCreateView


urlpatterns = [
    path("branch/", TblBranchListCreateView.as_view(), name="branch-list-create"),
    path("branch/<int:pk>/", TblBranchDetailView.as_view(), name="branch-detail"),
    path(
        "departments/",
        TblDepartmentListCreateView.as_view(),
        name="department-list-create",
    ),
    path(
        "departments/<int:pk>/",
        TblDepartmentDetailView.as_view(),
        name="department-detail",
    ),
    path(
        "designations/",
        TblDesignationListCreateView.as_view(),
        name="designation-list-create",
    ),
    path(
        "designations/<int:pk>/",
        TblDesignationDetailView.as_view(),
        name="designation-detail",
    ),
    path(
        "designations/parents/",
        ParentDesignationsView.as_view(),
        name="parent-designations",
    ),
    path("menus/", MenuListCreateView.as_view(), name="menu-list-create"),
    path("menus/<int:pk>/", MenuDetailView.as_view(), name="menu-detail"),
    path("menus/parents/", GetAllParentMenuView.as_view(), name="menu-parent-list"),
    path(
        "menus/portal/<int:portal_id>/",
        GetMenuByPortalIdView.as_view(),
        name="menu-by-portal",
    ),
    path("portals/", PortalListCreateView.as_view(), name="portal-list-create"),
    path("portals/<int:pk>/", PortalDetailView.as_view(), name="portal-detail"),
    path(
        "emp-basic-profiles/",
        EmpBasicProfileListCreateView.as_view(),
        name="emp-basic-profile-list-create",
    ),
    path(
        "emp-basic-profiles/<int:pk>/",
        EmpBasicProfileDetailView.as_view(),
        name="emp-basic-profile-detail",
    ),
    path(
        "emp-address-details/",
        EmpAddressDetailsListCreateView.as_view(),
        name="emp-address-list-create",
    ),
    path(
        "emp-address-details/<int:employee_id>/",
        EmpAddressDetailsDetailView.as_view(),
        name="emp-address-detail",
    ),
    path(
        "emp-bank-details/",
        EmpBankDetailsListCreateView.as_view(),
        name="emp-bank-list-create",
    ),
    path(
        "emp-bank-details/<int:employee_id>/",
        EmpBankDetailsDetailView.as_view(),
        name="emp-bank-detail",
    ),
    path(
        "emp-nominee-details/",
        EmpNomineeDetailsListCreateView.as_view(),
        name="emp-nominee-list-create",
    ),
    path(
        "emp-nominee-details/<int:employee_id>/",
        EmpNomineeDetailsDetailView.as_view(),
        name="emp-nominee-detail",
    ),
    path("emp-official-info/", EmpOfficialInfoView.as_view()),
    path("emp-official-info/<int:employee_id>/", EmpOfficialInfoDetailView.as_view()),
    path("roles/", RoleListCreateView.as_view(), name="role-list-create"),
    path("roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
    path(
        "role-permissions/",
        RolePermissionListCreateView.as_view(),
        name="role-permission-list-create",
    ),
    path(
        "role-permissions/<int:pk>/",
        RolePermissionDetailView.as_view(),
        name="role-permission-detail",
    ),
    path("dealers/", DealerListCreateView.as_view(), name="dealer-list-create"),
    path("dealers/<int:pk>/", DealerDetailView.as_view(), name="dealer-detail"),
    path(
        "subdealers/", SubDealerListCreateView.as_view(), name="subdealer-list-create"
    ),
    path(
        "subdealers/<int:pk>/", SubDealerDetailView.as_view(), name="subdealer-detail"
    ),
    path(
        "cities/", CityMasterListCreateAPIView.as_view(), name="citymaster-list-create"
    ),
    path(
        "cities/<int:pk>/", CityMasterDetailAPIView.as_view(), name="citymaster-detail"
    ),
    path("states/", StateListCreateAPIView.as_view(), name="state-list-create"),
    path("states/<int:pk>/", StateDetailAPIView.as_view(), name="state-detail"),
    path("upload-Empcsv/", UploadCSVView.as_view(), name="upload-csv"),
]


urlpatterns 
