from enum import Enum

from src.schemas import Error


class Role(Enum):
    ADMIN = 1
    USER = 2
    GUEST = 3


class SeatStatus(str, Enum):
    VACANT = "V"
    TEMP_HOLD = "T"
    RESERVED = "R"
    SOLD = "S"


class OrderStatus(str, Enum):
    PENDING = "PENDING"  # 尚未付款
    PAID = "PAID"  # 已付款
    CANCELED = "CANCELED"  # 使用者取消
    EXPIRED = "EXPIRED"  # 鎖位逾時未付款


class PaymentMethod(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    IBON = "IBON"
    LINE_PAY = "LINE_PAY"


DEFAULT_ERROR_RESPONSE = {
    400: {
        "description": "Bad request",
        "model": Error,
        "content": {
            "application/json": {
                "examples": {
                    "error": {"summary": "Error", "value": {"detail": "Bad request"}},
                }
            }
        },
    },
    401: {
        "description": "Unauthorized",
        "model": Error,
        "content": {
            "application/json": {
                "examples": {
                    "invalid_token": {
                        "summary": "Invalid Token",
                        "value": {"detail": "Could not validate credentials"},
                    },
                    "missing_token": {
                        "summary": "Missing Token",
                        "value": {"detail": "Not authenticated"},
                    },
                    "expired_token": {
                        "summary": "Expired Token",
                        "value": {"detail": "Token expired"},
                    },
                }
            }
        },
    },
    403: {
        "description": "Forbidden",
        "model": Error,
        "content": {
            "application/json": {
                "examples": {
                    "insufficient_permissions": {
                        "summary": "Insufficient Permissions",
                        "value": {"detail": "Not enough permissions"},
                    },
                    "forbidden": {
                        "summary": "Forbidden",
                        "value": {
                            "detail": "You do not have the permission to access this resource"
                        },
                    },
                }
            }
        },
    },
    404: {
        "description": "Item not found",
        "model": Error,
        "content": {
            "application/json": {
                "examples": {
                    "not_found": {
                        "summary": "Resource Not Found",
                        "value": {"detail": "Item not found"},
                    }
                }
            }
        },
    },
    422: {
        "description": "Validation error",
        "model": Error,
        "content": {
            "application/json": {
                "examples": {
                    "validation_error": {
                        "summary": "Validation Error",
                        "value": {"detail": "Invalid input parameters"},
                    },
                    "missing_field": {
                        "summary": "Missing Required Field",
                        "value": {"detail": "Required field 'email' is missing"},
                    },
                }
            }
        },
    },
    500: {
        "description": "Internal server error",
        "model": Error,
        "content": {
            "application/json": {
                "examples": {
                    "internal_error": {
                        "summary": "Internal Server Error",
                        "value": {"detail": "Internal server error"},
                    }
                }
            }
        },
    },
}
