class InvoiceNotFoundError(Exception):
    """Raised when an invoice cannot be found."""

    def __init__(self, invoice_number: str):
        self.invoice_number = invoice_number
        super().__init__(f"Invoice '{invoice_number}' not found")

class AccountingValidationError(Exception):

    """Raised when an accounting rule is violated."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


    
class OllamaServiceError(Exception):
    """Raised when communication with Ollama fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)