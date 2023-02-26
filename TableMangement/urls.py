from django.urls import path
from django.urls import path, register_converter
from .converters import DateConverter
from .views import TableAPIView, ReservationAPIView, GetReservationsTodayAPIView
from .views import GetTimeslotsAPIView

app_name = "TableMangement"

register_converter(DateConverter, 'date')



urlpatterns = [
    path('table', TableAPIView.as_view(),name='add_table'),
    path('table', TableAPIView.as_view(), name='get_tables'),
    path('table/<int:table_number>', TableAPIView.as_view(), name='delete_table'),

    path('reservation', ReservationAPIView.as_view()),
    path('reservation/<int:reservation_id>', ReservationAPIView.as_view()),

    

    path('today/reservation', GetReservationsTodayAPIView.as_view()),
    path('today/reservation/timeslots/<int:num_seats>', GetTimeslotsAPIView.as_view()),
    

]