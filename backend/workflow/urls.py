"""URL routes for the workflow REST API under ``/api/``."""

from django.urls import path

from workflow import views

urlpatterns = [
    path("auth/login", views.LoginView.as_view(), name="auth-login"),
    path("requests/pending", views.BillingRequestPendingView.as_view(), name="requests-pending"),
    path("requests/<int:pk>", views.BillingRequestDetailView.as_view(), name="request-detail"),
    path("requests", views.BillingRequestListCreateView.as_view(), name="requests"),
    path("reviews/<int:request_id>/approve", views.ReviewApproveView.as_view(), name="review-approve"),
    path("reviews/<int:request_id>/reject", views.ReviewRejectView.as_view(), name="review-reject"),
    path("invoices/metrics", views.InvoiceMetricsView.as_view(), name="invoice-metrics"),
    path("invoices/<int:pk>", views.InvoiceDetailView.as_view(), name="invoice-detail"),
    path("invoices", views.InvoiceListView.as_view(), name="invoices"),
    path(
        "audit/<str:entity_type>/<int:entity_id>",
        views.AuditTrailView.as_view(),
        name="audit-trail",
    ),
]
