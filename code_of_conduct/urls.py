from django.urls import path

# Languages Views
from code_of_conduct.views.languages_view import (LanguagesListCreateView, LanguagesDetailView,)

# Brand Views
from code_of_conduct.views.brand_view import (BrandListCreateView, BrandDetailView,)

# Questions Views
from code_of_conduct.views.questions_view import (QuestionsListCreateView, QuestionsDetailView, QuestionsTypeConstantsView,)

# Quarter Master Views
from code_of_conduct.views.quarter_master_view import (QuarterMasterView, QuarterMasterDetailView,)

# Deposit Agent Upload View
from code_of_conduct.views.deposit_agents_view import (DepositAgentsUploadView, DepositAgentsDataDetailView, SendLink, SendLinkToMobileView)
# 
from code_of_conduct.views.dsa_view import (DsaUploadView, DsaDataDetailView,)
# ras views
from code_of_conduct.views.ras_view import (RasUploadView, RasDataDetailView,)
from code_of_conduct.views.ras_view import RasExportExcelDownload
from code_of_conduct.views.ras_view import RasDownloadTemplate

from code_of_conduct.views.assign_quarter_view import AssignQuarterListView
from code_of_conduct.views.assign_quarter_view import (AssignQuarterCreateView,)    



urlpatterns = [
    # Languages
    path("languages/", LanguagesListCreateView.as_view(), name="languages_list_create"),
    path("languages/<int:pk>/", LanguagesDetailView.as_view(), name="languages_detail"),

    # Brand
    path("brand/", BrandListCreateView.as_view(), name="brand_list_create"),
    path("brand/<int:pk>/", BrandDetailView.as_view(), name="brand_detail"),

    # Questions
    path("questions/", QuestionsListCreateView.as_view(), name="questions_list_create"),
    path("questions/<int:pk>/", QuestionsDetailView.as_view(), name="questions_detail"),
    path('questions/constants/', QuestionsTypeConstantsView.as_view(), name="questions_type_constants"),

    # Quarter Master
    path("quarter_master/", QuarterMasterView.as_view(), name="quarter_master_list_create"),
    path("quarter_master/<int:pk>/", QuarterMasterDetailView.as_view(), name="quarter_master_detail"),

    # Deposit Agent Upload
    path("upload/", DepositAgentsUploadView.as_view(), name="deposit_agents_upload"),
    # path("deposit_agents/", DepositAgentsUploadView.as_view(), name="deposit_agents_list"),
    path("deposit_agents_data/<int:pk>/", DepositAgentsDataDetailView.as_view(), name="deposit_agents_data_detail"),
    path("deposit_agent/send_link/<int:pk>/", SendLink.as_view(), name="deposit_agent_send_link"),
    path("deposit_agent/send_link/", SendLinkToMobileView.as_view(), name="deposit_agent_send_link_to_mobile"),

    # dsa
    path("dsa_upload/", DsaUploadView.as_view(), name="dsa_upload"),
    path("dsa/", DsaUploadView.as_view(), name="dsa_list"),
    path("dsa_data/<int:pk>/", DsaDataDetailView.as_view(), name="dsa_data_detail"),

    # ras
    path("ras_upload/", RasUploadView.as_view(), name="ras_upload"),
    path("ras/", RasUploadView.as_view(), name="ras_list"),
    path("ras_data/<int:pk>/", RasDataDetailView.as_view(),name="ras_data_detail"),
    path('ras_data/data_download_template/', RasExportExcelDownload.as_view(), name='ras_export_excel'),
    path('ras_data/template_download/', RasDownloadTemplate.as_view(), name='ras_template_download'),

    path("assign_quarter/", AssignQuarterListView.as_view(), name="assign_quarter_search"),
    path("assign_quarter_create/", AssignQuarterCreateView.as_view(), name="assign_quarter_create"),



]

# Search Url: http://127.0.0.1:8000/api/code_of_conduct/deposit_agents/?search= 
# SearchDataName: Mark Alexander
# SearchAdharNumber:027142787890