from fast_flights import create_filter, get_flights_from_filter, FlightData, Passengers

if __name__ == "__main__":
    filter = create_filter(
        flight_data=[
            FlightData(date="2025-04-01", from_airport="FCO", to_airport="MUC"),
            FlightData(date="2025-04-12", from_airport="MUC", to_airport="FCO"),
        ],
        trip="return",
        passengers=Passengers(adults=1),
        seat="economy",
    )

    print(filter.as_b64().decode("utf-8"))

    flights = get_flights_from_filter(filter, currency="EUR", mode="common")
    print(flights)
