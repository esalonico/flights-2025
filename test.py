from fast_flights import create_filter, get_flights_from_filter, FlightData, Passengers

if __name__ == "__main__":
    filter = create_filter(
        flight_data=[
            FlightData(date="2025-04-01", from_airport="FCO", to_airport="MUC"),
            FlightData(date="2025-04-20", from_airport="MUC", to_airport="FCO"),
        ],
        trip="round-trip",
        passengers=Passengers(adults=1),
        seat="economy",
    )

    flights = get_flights_from_filter(filter, currency="EUR", mode="common")
    print(flights)
