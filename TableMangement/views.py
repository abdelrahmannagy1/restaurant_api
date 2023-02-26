from rest_framework.views import APIView
from rest_framework import exceptions
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from .models import Table, Reservation
from .serializers import TableSerializer, SetReservationSerializer, ReservationSerializer
from rest_framework import status
from datetime import datetime, timedelta, time
from .paginations import CustomPagination
from rest_framework.pagination import LimitOffsetPagination
from django.utils import timezone
from django.db.models import Max
from django.db.models import Q

# class GetTablesAPIView(APIView):
#     permission_classes = (IsAuthenticated,)

#     def get(self, request, format=None):
#         if not request.user.role == 'Admin': 
#             raise exceptions.NotAuthenticated("Not an admin User")

#         tables = [table.table_number for table in Table.objects.all()]
#         return Response({"tables":tables},status=status.HTTP_200_OK)

class TableAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TableSerializer

    def get(self, request, format=None):
        if not request.user.role == 'Admin': 
            raise exceptions.NotAuthenticated("Not an admin User")

        tables = [table.table_number for table in Table.objects.all()]
        return Response({"tables":tables},status=status.HTTP_200_OK)

    def post(self, request, format=None):
        if not request.user.role == 'Admin': 
            raise exceptions.NotAuthenticated("Not an admin User")

        table = request.data.get('table', {})
        serializer = self.serializer_class(data=table)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def delete(self, request, table_number=None, format=None):
        if not request.user.role == 'Admin': 
            raise exceptions.NotAuthenticated("Not an admin User")
        if not table_number:
            return Response({"error": "please specify the table number"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        table = Table.objects.get(table_number=table_number)
        if not table:
            return Response({"error": "no table with that number"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            table.delete()
        except:
            return Response({"error": "Table already has reservations"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response({"success": "table deleted"}, status=status.HTTP_200_OK)





class ReservationAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SetReservationSerializer
    pagination_class = CustomPagination

    

    def post(self, request, format=None):
        

        OPEN_TIME = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 12, 00).time()
        CLOSE_TIME = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 23, 59).time()

        reservation = request.data.get('reservation', {})

        req_start_time = datetime.strptime(reservation['start_time'],'%Y-%m-%d %H:%M:%S')
        req_end_time = datetime.strptime(reservation['end_time'],'%Y-%m-%d %H:%M:%S')

        if not reservation:
            return Response("Bad Request",status=status.HTTP_204_NO_CONTENT)

        if req_start_time.time() < OPEN_TIME or req_end_time.time() > CLOSE_TIME :
            return Response({"error": "Reservation outside working hours"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = self.serializer_class(data=reservation)
        serializer.is_valid(raise_exception=True)


        #get reservations for the day
        reservation_date = datetime.strptime(reservation['start_time'], '%Y-%m-%d %H:%M:%S').date()
       
        reservations = Reservation.objects.filter(start_time__date=reservation_date).order_by('start_time')

        for r in reservations:
            # print(r.start_time.time().replace(tzinfo=None))
            # print(r.end_time.time().replace(tzinfo=None))
            # print("************")
            # print(req_start_time.time())
            # print(req_end_time.time())
            if (req_start_time.time() >= r.start_time.time().replace(tzinfo=None) and req_start_time.time() <= r.end_time.time().replace(tzinfo=None)) or (req_end_time.time() >= r.start_time.time().replace(tzinfo=None) and req_end_time.time() <= r.end_time.time().replace(tzinfo=None)):
                  return Response({"error": "Conflicting Reservation"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def delete(self, request, reservation_id, format=None):
        current_date = datetime.now()
        try:
            reservation = Reservation.objects.get(pk=reservation_id)
        except:
            return Response({"error": "No reservation Number matching"}, status=status.HTTP_400_BAD_REQUEST)

        if reservation.start_time.replace(tzinfo=None) < current_date:
            return Response({"error": "Cannot delete reservations in the past"}, status=status.HTTP_400_BAD_REQUEST)

        reservation.delete()
        return Response("Object deleted", status=status.HTTP_200_OK)





class GetAllReservationsAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination
    serializer_class = ReservationSerializer

    def get(self, request, format=None):
        if not request.user.role == 'Admin': 
            raise exceptions.NotAuthenticated("Not an admin User")

        paginator = CustomPagination()
        reservations_qs = Reservation.objects.all()
        res = paginator.paginate_queryset(reservations_qs, request, view=self)
        serializer = self.serializer_class(res, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request, format=None):
        if not request.user.role == 'Admin': 
            raise exceptions.NotAuthenticated("Not an admin User")

        paginator = CustomPagination()
        tables = request.data.get('tables', {})
        
        reservations_qs = Reservation.objects.filter(table__table_number__in=tables)
        res = paginator.paginate_queryset(reservations_qs, request, view=self)
        serializer = self.serializer_class(res, many=True)
        
        return paginator.get_paginated_response(serializer.data)


class GetAllReservationsFromDateAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination
    serializer_class = ReservationSerializer

    def get(self, request, start=None, end=None, format=None):
        if not request.user.role == 'Admin': 
            raise exceptions.NotAuthenticated("Not an admin User")

        if start > end:
            return Response({"error": "Reservation outside working hours"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        paginator = CustomPagination()
        reservations_qs = Reservation.objects.filter(start_time__date__gte=start, start_time__date__lte=end)
        res = paginator.paginate_queryset(reservations_qs, request, view=self)
        serializer = self.serializer_class(res, many=True)
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, start=None, end=None, format=None):
        if not request.user.role == 'Admin': 
            raise exceptions.NotAuthenticated("Not an admin User")

        if start > end:
            return Response({"error": "Reservation outside working hours"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        paginator = CustomPagination()
        tables = request.data.get('tables', {})
        
        reservations_qs = Reservation.objects.filter(start_time__date__gte=start, start_time__date__lte=end, table__table_number__in=tables)
        res = paginator.paginate_queryset(reservations_qs, request, view=self)
        serializer = self.serializer_class(res, many=True)
        
        return paginator.get_paginated_response(serializer.data)

        

        


class GetTimeslotsAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    

    def get(self, request, num_seats, format=None):
        # get all tables that satisfy the min number of seats where there are no reservations for today
        # or has resevations after the current time
        MAX_SEATS = Table.objects.aggregate(Max('num_seats'))
        
        if num_seats > MAX_SEATS['num_seats__max']:
            return Response({"error": "No tables can hold that many seats currently"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        OPEN_TIME = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 12, 00)
        CLOSE_TIME = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 23, 59)

        #tables that has reservations
        current_time = datetime.now()
        reservations = Reservation.objects.filter(start_time__gte=current_time).exclude(table__num_seats__lt=num_seats).order_by('table__num_seats')
        #print(reservations)


        #print(reservations.values_list('table__pk',flat=True))
        

        #tables that dont have reservations for today
        free_tables = Table.objects.exclude(Q(pk__in=reservations.values_list('table__pk',flat=True)) | Q(num_seats__lt=num_seats)).order_by('num_seats')
        #print(free_tables)


        #tables that fit the criteria
        ok_tables = []
        i = 0 
        
        while(True):
            if(i == len(free_tables)):
                break
            
            ok_tables.append(free_tables[i])
            if(free_tables[i].num_seats > num_seats and i < (len(free_tables)-1) and free_tables[i].num_seats != free_tables[i+1].num_seats):
                break
            i+=1

        i = 0 
        while(True):
            if(i == len(reservations)):
                break
            ok_tables.append(reservations[i].table)
            if(reservations[i].table.num_seats > num_seats and i < len(reservations)-1 and reservations[i].table.num_seats != reservations[i+1].table.num_seats):
                break
            i+=1
        #print(ok_tables)


        res = []
        curr_time = datetime.now()
        for i in range(len(ok_tables)):
            table_reservations = ok_tables[i].reservation_set.filter(start_time__gte=current_time).exclude(table__num_seats__lt=num_seats).order_by('start_time')

            #if it has no reservations then it is available for the whole day
            if not table_reservations:
                res.append([datetime.now(),CLOSE_TIME])
                continue

            for r in table_reservations:
                res.append([curr_time, r.start_time])
                curr_time = r.end_time
        
        res.append([curr_time, CLOSE_TIME])

        if not res:
            return Response({"error": "no tables available"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'timeslots' : res})



class GetReservationsTodayAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReservationSerializer
   
    def get(self, request, format=None):
        paginator = CustomPagination()
        current_date = datetime.now().date()
        reservations_qs = Reservation.objects.filter(start_time__date=current_date)
        # print("*************")
        # print(len(reservations_qs))
        # print("*************")
        res = paginator.paginate_queryset(reservations_qs, request, view=self)
        serializer = self.serializer_class(res, many=True)
        # print("*************")
        # print(serializer.data)
        # print("*************")
        return paginator.get_paginated_response(serializer.data)

class GetReservationsTodayWithOrderAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReservationSerializer
   
    def get(self, request, order=None, format=None):
        if order != 'asc' and order != 'desc':
            return Response({"error": "order parameter should be asc or desc"}, status=status.HTTP_400_BAD_REQUEST)

        paginator = CustomPagination()
        current_date = datetime.now().date()
        if order == 'asc':
            reservations_qs = Reservation.objects.filter(start_time__date=current_date).order_by('start_time')
        elif order == 'desc':
            reservations_qs = Reservation.objects.filter(start_time__date=current_date).order_by('-start_time')

        
        res = paginator.paginate_queryset(reservations_qs, request, view=self)
        serializer = self.serializer_class(res, many=True)
        
        return paginator.get_paginated_response(serializer.data)



        

        


