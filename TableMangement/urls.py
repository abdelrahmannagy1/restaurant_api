from django.urls import path
from django.urls import path, register_converter
from .converters import DateConverter
from .views import TableAPIView, ReservationAPIView, GetReservationsTodayAPIView
from .views import GetTimeslotsAPIView

app_name = "TableMangement"

register_converter(DateConverter, 'date')



urlpatterns = [
    path('tables', TableAPIView.as_view(),name='add_table'),
    path('tables', TableAPIView.as_view(), name='get_tables'),
    path('tables/<int:table_number>', TableAPIView.as_view(), name='delete_table'),

    path('reservations', ReservationAPIView.as_view()),
    path('reservations/<int:reservation_id>', ReservationAPIView.as_view()),

    

    path('today/reservations', GetReservationsTodayAPIView.as_view()),
    path('today/reservations/timeslots/<int:num_seats>', GetTimeslotsAPIView.as_view()),
    

]