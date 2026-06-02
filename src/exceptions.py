class APIException(Exception):
    """Base exception for team-portal-backend application exceptions."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        headers: dict = None,
    ):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.headers = headers
