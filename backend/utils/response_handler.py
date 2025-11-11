"""
Response Handler Utilities
Xử lý các response trả về từ API
"""
from datetime import datetime


def success_response(message="Thành công", data=None, status_code=200):
    """
    Tạo response thành công chuẩn
    
    Args:
        message: Thông báo
        data: Dữ liệu trả về
        status_code: HTTP status code
    
    Returns:
        Dictionary chứa response data
    """
    response = {
        "success": True,
        "message": message,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    return response


def error_response(message="Đã xảy ra lỗi", status_code=400, error=None):
    """
    Tạo response lỗi chuẩn
    
    Args:
        message: Thông báo lỗi
        status_code: HTTP status code
        error: Chi tiết lỗi
    
    Returns:
        Dictionary chứa error response
    """
    response = {
        "success": False,
        "message": message,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if error is not None:
        response["error"] = str(error)
    
    return response


def paginated_response(items, page, per_page, total_items, message="Thành công"):
    """
    Tạo response có phân trang
    
    Args:
        items: Danh sách items
        page: Trang hiện tại
        per_page: Số items mỗi trang
        total_items: Tổng số items
        message: Thông báo
    
    Returns:
        Dictionary chứa paginated response
    """
    total_pages = (total_items + per_page - 1) // per_page
    
    response = success_response(
        message=message,
        data={
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    )
    
    return response