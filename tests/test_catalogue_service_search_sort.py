import pytest

from favourite_books.application.services import CatalogueService, ValidationError


def test_catalogue_service_rejects_unknown_sort_key(seeded_catalogue):
    service = CatalogueService(seeded_catalogue["books"])

    with pytest.raises(ValidationError):
        service.list_books("bad")


def test_catalogue_service_combines_search_and_sort(seeded_catalogue):
    service = CatalogueService(seeded_catalogue["books"])

    books = service.list_books(sort="pages", query="ray")

    assert [book.name for book in books] == ["Fahrenheit 451"]
