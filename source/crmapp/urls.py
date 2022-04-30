from django.urls import path, include

from crmapp.views.client_views import ClientCreateView, ClientListView, ClientUpdateView
from crmapp.views.manager_report import ManagerReportCreateView, ManagerReportListView

from crmapp.views.service_views import ServiceListView, ServiceCreateView, ServiceUpdateView, ServiceDeleteView

from crmapp.views.consumables import InventoryListView, InventoryCreateView, InventoryUpdateView, InventoryDeleteView, \
    CleanserListView, CleanserCreateView, CleanserUpdateView, CleanserDeleteView

from crmapp.views.service_order_views import ServiceOrderListView, ServiceOrderDetailView, ServiceOrderCreateView, \
    ServiceOrderUpdateView, ServiceOrderDeleteView

app_name = 'crmapp'

client_urlpatterns = [
    path('all/', ClientListView.as_view(), name='client_index'),
    path('create/', ClientCreateView.as_view(), name='client_create'),
    path('up/<int:pk>', ClientUpdateView.as_view(), name='client_update')
]

service_urlpatterns = [
    path('list/', ServiceListView.as_view(), name='service_list'),
    path('create/', ServiceCreateView.as_view(), name='service_create'),
    path('update/<int:pk>/', ServiceUpdateView.as_view(), name='service_update'),
    path('delete/<int:pk>/', ServiceDeleteView.as_view(), name='service_delete'),
]

consumables_urlpatterns = [
    path('inventory/all/', InventoryListView.as_view(), name='inventory_index'),
    path('inventory/create/', InventoryCreateView.as_view(), name='inventory_create'),
    path('inventory/up/<int:pk>/', InventoryUpdateView.as_view(), name='inventory_update'),
    path('inventory/delete/<int:pk>/', InventoryDeleteView.as_view(), name='inventory_delete'),

    path('cleanser/all/', CleanserListView.as_view(), name='cleanser_index'),
    path('cleanser/create/', CleanserCreateView.as_view(), name='cleanser_create'),
    path('cleanser/up/<int:pk>/', CleanserUpdateView.as_view(), name='cleanser_update'),
    path('cleanser/delete/<int:pk>/', CleanserDeleteView.as_view(), name='cleanser_delete')
]

service_order_urlpatterns = [
    path("", ServiceOrderListView.as_view(), name="service_order_list"),
    path("detail/<int:pk>/", ServiceOrderDetailView.as_view(), name="service_order_detail"),
    path("create/", ServiceOrderCreateView.as_view(), name="service_order_create"),
    path("update/<int:pk>/", ServiceOrderUpdateView.as_view(), name="service_order_update"),
    path("delete/<int:pk>/", ServiceOrderDeleteView.as_view(), name="service_order_delete"),
]

manager_report_urlpatterns = [
    path('order/<int:pk>/manager_report/create/', ManagerReportCreateView.as_view(), name='manager_report_create'),
    path('manager_report/all/', ManagerReportListView.as_view(), name='manager_report_list'),
]

urlpatterns = [
    path('client/', include(client_urlpatterns)),
    path('service/', include(service_urlpatterns)),
    path('service_order/', include(service_order_urlpatterns)),
    path('consumables/', include(consumables_urlpatterns)),
    path('', include(manager_report_urlpatterns))
]
