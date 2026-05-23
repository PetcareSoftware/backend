from django.urls import path
from .views import RecepcionistaTestView, LogEntryListView

urlpatterns = [
    path('test-recepcionista/', RecepcionistaTestView.as_view(), name='test-recepcionista'),
    path('test-recepcionista/', RecepcionistaTestView.as_view(), name='test-recepcionista'),
    path('logs/', LogEntryListView.as_view(), name='log_entry_list'),   # ← nueva línea
]   