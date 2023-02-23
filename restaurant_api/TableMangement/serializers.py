from rest_framework import serializers
from .models import Table, Reservation

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['table_number', 'num_seats']

    def validate_num_seats(self,value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("Number of seats must be between 1 and 12")
        return value

class SetReservationSerializer(serializers.Serializer):
    table_number = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    
    # class Meta:
    #     model = Reservation
    #     fields = ['table', 'start_time', 'end_time']
    
    def save(self):
        
        table = Table.objects.get(table_number = self.validated_data['table_number'])
        return Reservation.objects.create(table=table, start_time=self.validated_data['start_time'], end_time=self.validated_data['end_time'])

class ReservationSerializer(serializers.ModelSerializer):
    table = TableSerializer()
    class Meta:
        model = Reservation
        fields = ['table', 'start_time', 'end_time']