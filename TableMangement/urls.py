from django.urls import path
from django.urls import path, register_converter
from .converters import DateConverter
from .views import TableAPIView, ReservationAPIView, GetAllReservationsAPIView, GetReservationsTodayAPIView
from .views import GetTimeslotsAPIView, GetReservationsTodayWithOrderAPIView, GetAllReservationsFromDateAPIView

app_name = "TableMangement"

register_converter(DateConverter, 'date')

# urlpatterns = [
#     path('table/addtable', AddTableAPIView.as_view(),name='add_table'),
#     path('table/gettables', GetTablesAPIView.as_view(), name='get_tables'),
#     path('table/deletetable/<int:table_number>', DeleteTableAPIView.as_view(), name='delete_table'),

#     path('reservation/setreservation', SetReservationAPIView.as_view()),
#     path('reservation/getallreservations', GetAllReservationsAPIView.as_view()),
#     path('reservation/deletereservation/<int:reservation_id>', DeleteReservationAPIView.as_view()),
#     path('reservation/getallreservationstoday', GetReservationsTodayAPIView.as_view()),
#     path('reservation/getallreservationstoday/<str:order>', GetReservationsTodayWithOrderAPIView.as_view()),
#     path('reservation/gettimeslots/<int:num_seats>', GetTimeslotsAPIView.as_view()),
#     path('reservation/getallreservationsfromdate/<date:start>/<date:end>', GetAllReservationsFromDateAPIView.as_view()),

# ]

urlpatterns = [
    path('table', TableAPIView.as_view(),name='add_table'),
    path('table', TableAPIView.as_view(), name='get_tables'),
    path('table/<int:table_number>', TableAPIView.as_view(), name='delete_table'),

    path('reservation', ReservationAPIView.as_view()),
    path('reservation/<int:reservation_id>', ReservationAPIView.as_view()),

    path('reservation/all', GetAllReservationsAPIView.as_view()),
    path('reservation/all/<date:start>/<date:end>', GetAllReservationsFromDateAPIView.as_view()),
    
    


    path('reservation/today', GetReservationsTodayAPIView.as_view()),
    path('reservation/today/<str:order>', GetReservationsTodayWithOrderAPIView.as_view()),

    path('reservation/timeslots/<int:num_seats>', GetTimeslotsAPIView.as_view()),
    

]