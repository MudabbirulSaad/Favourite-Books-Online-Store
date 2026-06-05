from favourite_books.domain.checkout import CreditCard
from favourite_books.domain.customer import Address, Customer


def test_customer_address_and_payment_card_value_objects():
    address = Address("1 Main St", "Melbourne", "VIC", "3000")
    customer = Customer.guest("Saad", "saad@example.com", address)
    card = CreditCard("Saad", "4111 1111 1111 1111", "12/28", "123")

    assert customer.shipping_address.postcode == "3000"
    assert customer.billing_address is address
    assert card.masked_number() == "**** **** **** 1111"
