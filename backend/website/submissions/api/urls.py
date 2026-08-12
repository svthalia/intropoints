from django.urls import path

from submissions.api.views.base import AllAPIView as SubmissionRetrieveAllAPIView
from submissions.api.views.base import ForChallengeAPIView as SubmissionRetrieveForChallengeAPIView
from submissions.api.views.base import ForTeamAPIView as SubmissionRetrieveForTeamAPIView
from submissions.api.views.base import UploadAPIView as SubmissionUploadAPIView
from submissions.api.views.grading import AllAPIView as SubmissionGradingAllAPIView
from submissions.api.views.grading import GradeAPIView as SubmissionGradeAPIView
from submissions.api.views.grading import ReleaseAPIView as SubmissionGradingReleaseAPIView
from submissions.api.views.grading import SelectAPIView as SubmissionGradingSelectAPIView

app_name = "submissions_api"

# Submission endpoints for grading, uploading
# retrieving and viewing submission
#
#
# ``/api/submissions/upload/
#   -> Upload a submission
#
#
# ``/api/submissions/for-team/<str:team_name>/
#   -> Retrieve all submission for a single team
#
# ``/api/submissions/all/
#   -> Retrieve all submissions
#
#
# ``/api/submissions/grade/all/
#   -> Retrieve all gradable submissions
#
# ``/api/submissions/grade/get/<int:id>/
#   -> Retrieve and lock a single submission
#
# ``/api/submissions/release/<int:submission_id>/
#   -> Release a given submission
#
# ``/api/submissions/grade/update/
#   -> Update the points for a given submission

urlpatterns = [
    # Submission upload endpoints
    path(
        "upload/",
        SubmissionUploadAPIView.as_view(),
        name="submission_upload",
    ),
    path(
        "for-team/<str:team_name>/",
        SubmissionRetrieveForTeamAPIView.as_view(),
        name="submission_team_retrieve",
    ),
    path(
        "for-challenge/<slug:slug>/",
        SubmissionRetrieveForChallengeAPIView.as_view(),
        name="submission_team_retrieve",
    ),
    # Submission retrieval endpoints
    path(
        "all/",
        SubmissionRetrieveAllAPIView.as_view(),
        name="submission_all_retrieve",
    ),
    # Submission grading endpoints
    path(
        "grade/get/all/",
        SubmissionGradingAllAPIView.as_view(),
        name="submission_grading_all",
    ),
    path(
        "grade/get/<int:id>/",
        SubmissionGradingSelectAPIView.as_view(),
        name="submission_grading_select",
    ),
    path(
        "grade/release/<int:submission_id>/",
        SubmissionGradingReleaseAPIView.as_view(),
        name="submission_grading_release",
    ),
    path(
        "grade/update/",
        SubmissionGradeAPIView.as_view(),
        name="submission_grading_update",
    ),
]
