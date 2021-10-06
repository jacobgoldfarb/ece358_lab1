class Utility:

    @staticmethod
    def get_arrival_rate_from_rho(rho, transmission_rate=1_000_000, avg_packet_length=2000):
        return rho * transmission_rate / avg_packet_length
