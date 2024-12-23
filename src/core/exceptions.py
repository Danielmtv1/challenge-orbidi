from fastapi import HTTPException, status



class MapMyWordException(HTTPException):
    def __init__(
            self,
            status_code: int = 400,
            detail: str = None
        ):
            super().__init__(status_code=status_code, detail=detail)

class LocationNotFound(MapMyWordException):
    def __init__(self, location_id: int):
        super().__init__(
             status_code=status.HTTP_404_NOT_FOUND,
             detail=f"Location with id: {location_id} not found")
        
class LocationAlreadyExists(MapMyWordException):
    def __init__(self, location_id: int):
        super().__init__(
             status_code=status.HTTP_409_CONFLICT,
             detail=f"Location with id: {location_id} already exists")

class CategoryNotFound(MapMyWordException):
    def __init__(self, category_id: int):
        super().__init__(
             status_code=status.HTTP_404_NOT_FOUND,
             detail=f"Category with id: {category_id} not found")
        
class NotFoundException(Exception):
    """Excepción para recursos no encontrados."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
