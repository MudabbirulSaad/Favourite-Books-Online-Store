from favourite_books.domain.checkout import CreditCard, PaymentResult


class FakePaymentGateway:
    """Prototype payment adapter: cards ending in 0000 are declined."""

    def authorise(self, card: CreditCard, amount) -> PaymentResult:
        if card.number.endswith("0000"):
            return PaymentResult(False, "Payment was declined by the test gateway.")
        return PaymentResult(True, "Payment authorised.", f"PAY-{card.number[-4:]}-{amount:.2f}")
