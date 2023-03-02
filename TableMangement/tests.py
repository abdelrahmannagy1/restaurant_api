from django.test import TestCase
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from .models import Table,Reservation
from Authentication.models import User
from django.urls import reverse
import json
from datetime import datetime, timedelta





class ReservationTestCase(APITestCase):
    def test_register_not_admin(self):
        """
            not admin registration
        """
        user = User.objects.create_user("test_admin","9999","Employee","testpassword")

        resp = self.client.get('/api/users/register', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
       
        self.assertEquals(resp.status_code,405)

    def test_delete_table_not_admin(self):
        """
            delete table
        """
        user = User.objects.create_user("test_admin","9999","Employee","testpassword")

        resp = self.client.delete('/api/tables/2', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
       
        self.assertEquals(resp.status_code,403)

    def test_get_tables_not_admin(self):
        """
            get tables while not admin
        """
        user = User.objects.create_user("test_admin","9999","Employee","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        
        
        #create one in the past
        reservation = Reservation.objects.create(start_time=datetime.now()-timedelta(days=1), end_time=datetime.now()-timedelta(days=1), table=table)

        resp = self.client.get('/api/tables', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation.delete()
        
        table.delete()
        
        #print(resp.json())
        self.assertEquals(resp.status_code,403)

    def test_get_tables_admin(self):
        """
            get tables while admin
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        
        
        #create one in the past
        reservation = Reservation.objects.create(start_time=datetime.now()-timedelta(days=1), end_time=datetime.now()-timedelta(days=1), table=table)

        resp = self.client.get('/api/tables', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation.delete()
        
        table.delete()
        
        #print(resp.json())
        self.assertEquals(resp.status_code,200)

    def test_get_reservations_today_order_asc(self):
        """
            test the get reservations today order ascending
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        
        
        reservation1 = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=1), end_time=datetime.now()+timedelta(hours=2), table=table)
        reservation1_date =(datetime.now()+timedelta(hours=1))

        reservation2 = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=2), end_time=datetime.now()+timedelta(hours=3), table=table)

        resp = self.client.get('/api/today/reservations?order=asc', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        
        reservation1.delete()
        reservation2.delete()
        
        table.delete()
        
        resp_date_hour = resp.json()['results'][0]['start_time'][11:13] # get the hour from the string
        
        self.assertEquals(resp_date_hour,reservation1_date.strftime("%H"))

    def test_get_reservations_today_order_desc(self):
        """
            test the get reservations today order descending
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        
        
        reservation1 = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=1), end_time=datetime.now()+timedelta(hours=2), table=table)

        reservation2 = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=2), end_time=datetime.now()+timedelta(hours=3), table=table)
        reservation2_date =(datetime.now()+timedelta(hours=2))

        resp = self.client.get('/api/today/reservations?order=desc', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        
        reservation1.delete()
        reservation2.delete()
        
        table.delete()
        
        resp_date_hour = resp.json()['results'][0]['start_time'][11:13] # get the hour from the string
        
        self.assertEquals(resp_date_hour,reservation2_date.strftime("%H"))
       
    def test_set_reservation_conflicting(self):
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=1 )[0]
        
        reservation = Reservation.objects.create(start_time=datetime.now(), end_time=datetime.now()+timedelta(hours=1), table=table)
        data = {
            "reservation": {
            "start_time" : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": (datetime.now()+timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "table_number": table.table_number
            }
        }
        resp = self.client.post('/api/reservations',data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        
        reservation.delete()
        table.delete()
        self.assertEquals(resp.status_code,406)

    def test_set_reservation_accepted(self):
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=1 )[0]
        
        reservation = Reservation.objects.create(start_time=datetime(year=2023,month=2,day=23,hour=13,minute=0), end_time=datetime(year=2023,month=2,day=23,hour=14,minute=0), table=table)
        data = {
            "reservation": {
            "start_time" : (datetime(year=2023,month=2,day=23,hour=15,minute=0)).strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": (datetime(year=2023,month=2,day=23,hour=16,minute=0)).strftime("%Y-%m-%d %H:%M:%S"),
            "table_number": table.table_number
            }
        }
        resp = self.client.post('/api/reservations',data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        
        self.client.delete('/api/tables/1', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)

        reservation.delete()
        #table.delete()
        self.assertEquals(resp.status_code,201)

    def test_get_reservations_today(self):
        """
            get reservations today 
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        
        reservation1 = Reservation.objects.create(start_time=datetime.now(), end_time=datetime.now()+timedelta(hours=1), table=table)
        
        #create one in a different day
        reservation2 = Reservation.objects.create(start_time=datetime.now()+timedelta(days=1), end_time=datetime.now()+timedelta(days=1), table=table)

        resp = self.client.get('/api/today/reservations', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation1.delete()
        reservation2.delete()
        table.delete()
        
        #print(resp.json())
        self.assertEqual(resp.json()['count'],1)

    def test_get_reservations_filter_by_table(self):
        """
            get all reservations and filter by table
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table1 = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        table2 = Table.objects.get_or_create(table_number=2, num_seats=2 )[0]
        
        reservation1 = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=5), end_time=datetime.now()+timedelta(hours=6), table=table1)
        
        #create one in a different day
        reservation2 = Reservation.objects.create(start_time=datetime.now()+timedelta(days=1), end_time=datetime.now()+timedelta(days=1), table=table2)

        # data = {"tables":[1]}
        resp = self.client.get('/api/reservations?tables[]=1', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation1.delete()
        reservation2.delete()
        table1.delete()
        table2.delete()
        
        #print(resp.json())
        self.assertEqual(resp.json()['count'],1)
    def test_get_reservations(self):
        """
            get all reservations  
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table1 = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        
        
        reservation1 = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=5), end_time=datetime.now()+timedelta(hours=6), table=table1)
        
        #create one in a different day
        reservation2 = Reservation.objects.create(start_time=datetime.now()+timedelta(days=1), end_time=datetime.now()+timedelta(days=1), table=table1)

        
        resp = self.client.get('/api/reservations', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation1.delete()
        reservation2.delete()
        table1.delete()
        
        
        #print(resp.json())
        self.assertEqual(resp.json()['count'],2)
    def test_get_reservations_date_range(self):
        """
            get all reservations by date range 
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        
        reservation1 = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=1), end_time=datetime.now()+timedelta(hours=3), table=table)
        
        #create one in a different day
        reservation2 = Reservation.objects.create(start_time=datetime.now()+timedelta(days=2), end_time=datetime.now()+timedelta(days=2), table=table)

        current_date = (datetime.now()+timedelta(hours=1)).strftime('%Y-%m-%d')
        #print(current_date)

        resp = self.client.get('/api/reservations?start='+current_date+'&end='+current_date, content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation1.delete()
        reservation2.delete()
        table.delete()
        
        #print(resp.json())
        self.assertEqual(resp.json()['count'],1)

    def test_get_reservations_date_range_filtertable(self):
        """
            get all reservations by date range and filter by table
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table1 = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        table2= Table.objects.get_or_create(table_number=2, num_seats=2 )[0]
        
        reservation1 = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=1), end_time=datetime.now()+timedelta(hours=3), table=table1)
        reservation2 = Reservation.objects.create(start_time=datetime.now()+timedelta(days=2), end_time=datetime.now()+timedelta(days=2), table=table2)

        current_date = (datetime.now()+timedelta(hours=1)).strftime('%Y-%m-%d')
        
        # data = {"tables":[1]}
        resp = self.client.get('/api/reservations?start='+current_date+'&end='+current_date+"&tables[]=1", content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        
        reservation1.delete()
        reservation2.delete()
        table1.delete()
        table2.delete()
        
        
        self.assertEqual(resp.json()['count'],1)

    def test_delete_reservation(self):
        """
            delete reservation in the past
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        
        
        #create one in the past
        reservation = Reservation.objects.create(start_time=datetime.now()-timedelta(days=1), end_time=datetime.now()-timedelta(days=1), table=table)

        resp = self.client.delete('/api/reservations/1', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation.delete()
        
        table.delete()
        
        #print(resp.json())
        self.assertEquals(resp.status_code,400)
    
    def test_delete_table_with_reservation(self):
        """
            delete table with reservation
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        
        
        #create reservation
        reservation = Reservation.objects.create(start_time=datetime.now()+timedelta(days=1), end_time=datetime.now()+timedelta(days=1), table=table)

        resp = self.client.delete('/api/reservations/1', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation.delete()
        
        table.delete()
        
        #print(resp.json())
        self.assertEquals(resp.status_code,400)

    def test_delete_table_without_reservation(self):
        """
            delete table without reservation
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        
        

        resp = self.client.delete('/api/tables/1', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        
        table.delete()
        
        #print(resp.json())
        self.assertEquals(resp.status_code,200)
        

    def test_get_time_slots1(self):
        """
            Tesing if supplied more seats than currently available
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=1 )[0]
        
        reservation = Reservation.objects.create(start_time=datetime.now(), end_time=datetime.now()+timedelta(hours=1), table=table)
        
        resp = self.client.get('/api/today/reservations/timeslots/2', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        
        reservation.delete()
        table.delete()
        
        self.assertTrue('error' in resp.json().keys())

    def test_get_time_slots2(self):
        """
            Tesing if a table exactly matches 
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=2 )[0]
        
        reservation = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=5), end_time=datetime.now()+timedelta(hours=6), table=table)
        
        resp = self.client.get('/api/today/reservations/timeslots/2', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation.delete()
        table.delete()
        
        #print(resp.json())
        self.assertEquals(len(resp.json()['timeslots']),2)

    def test_get_time_slots3(self):
        """
            Tesing if a single table meets the min requirements
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table = Table.objects.get_or_create(table_number=1, num_seats=3 )[0]
        
        reservation = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=5), end_time=datetime.now()+timedelta(hours=6), table=table)
        
        resp = self.client.get('/api/today/reservations/timeslots/2', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation.delete()
        table.delete()
        
        #print(resp.json())
        self.assertEquals(len(resp.json()['timeslots']),2)

    def test_get_time_slots4(self):
        """
            two tables same size (not exact) with one free 
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table1 = Table.objects.get_or_create(table_number=1, num_seats=3 )[0]
        table2 = Table.objects.get_or_create(table_number=2, num_seats=3 )[0]
        
        reservation = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=5), end_time=datetime.now()+timedelta(hours=6), table=table1)
        
        resp = self.client.get('/api/today/reservations/timeslots/2', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation.delete()
        table1.delete()
        table2.delete()
        
        #print(resp.json())
        self.assertEquals(len(resp.json()['timeslots']),3)

    def test_get_time_slots4(self):
        """
            three tables two of same size one free while the third is more than needed
        """
        user = User.objects.create_user("test_admin","9999","Admin","testpassword")
        
        table1 = Table.objects.get_or_create(table_number=1, num_seats=3 )[0]
        table2 = Table.objects.get_or_create(table_number=2, num_seats=3 )[0]
        table3 = Table.objects.get_or_create(table_number=3, num_seats=4 )[0]
        
        reservation = Reservation.objects.create(start_time=datetime.now()+timedelta(hours=5), end_time=datetime.now()+timedelta(hours=6), table=table1)
        
        resp = self.client.get('/api/today/reservations/timeslots/2', content_type='application/json', HTTP_AUTHORIZATION='Token '+user.token)
        reservation.delete()
        table1.delete()
        table2.delete()
        table3.delete()
        
        #print(resp.json())
        self.assertEquals(len(resp.json()['timeslots']),3)
    

        
        
