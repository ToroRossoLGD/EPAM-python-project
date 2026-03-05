from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    project_id: int
    uploaded_by: int | None
    filename: str
    content_type: str
    size_bytes: int