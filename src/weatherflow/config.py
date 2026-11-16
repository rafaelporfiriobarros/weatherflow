"""Configuracoes iniciais do projeto WeatherFlow."""

from dataclasses import dataclass


@dataclass(frozen=True)
class City:
    """Representa uma cidade monitorada pelo pipeline."""

    name: str
    latitude: float
    longitude: float


CITIES = (
    City(
        name="Sao Paulo",
        latitude=-23.5505,
        longitude=-46.6333,
    ),
    City(
        name="Rio de Janeiro",
        latitude=-22.9068,
        longitude=-43.1729,
    ),
    City(
        name="Curitiba",
        latitude=-25.4284,
        longitude=-49.2733,
    ),
)


def get_cities() -> tuple[City, ...]:
    """Retorna as cidades configuradas para monitoramento."""
    return CITIES


def validate_cities(cities: tuple[City, ...]) -> bool:
    """Valida coordenadas e nomes das cidades."""

    if not cities:
        return False

    names = set()

    for city in cities:
        if not city.name.strip():
            return False

        if not -90 <= city.latitude <= 90:
            return False

        if not -180 <= city.longitude <= 180:
            return False

        if city.name in names:
            return False

        names.add(city.name)

    return True
