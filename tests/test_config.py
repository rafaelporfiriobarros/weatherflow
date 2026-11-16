"""Testes das configuracoes do WeatherFlow."""

import pytest

from weatherflow.config import City, get_cities, validate_cities


def test_get_cities_returns_three_cities():
    cities = get_cities()

    assert len(cities) == 3


def test_default_cities_are_valid():
    cities = get_cities()

    assert validate_cities(cities) is True


def test_empty_city_list_is_invalid():
    assert validate_cities(()) is False


def test_duplicate_city_is_invalid():
    cities = (
        City("Sao Paulo", -23.5505, -46.6333),
        City("Sao Paulo", -23.5505, -46.6333),
    )

    assert validate_cities(cities) is False


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [
        (91.0, -46.6333),
        (-91.0, -46.6333),
        (-23.5505, 181.0),
        (-23.5505, -181.0),
    ],
)
def test_invalid_coordinates(latitude, longitude):
    cities = (City("Cidade Teste", latitude, longitude),)

    assert validate_cities(cities) is False


def test_empty_city_name_is_invalid():
    cities = (City("   ", -23.5505, -46.6333),)

    assert validate_cities(cities) is False
