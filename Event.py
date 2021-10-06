class Event:
    eligible_event_types = set(['Packet', 'Observer'])

    def __init__(self,
                 arrival_time,
                 length=0,
                 transmission_rate=1,
                 type='Packet'):
        if type not in self.eligible_event_types:
            raise
        self.type = type
        self.arrival_time = arrival_time
        self.departure_time = 0
        self.packet_length = length
        self.service_time = length / transmission_rate
        self.dropped = False
