from dataclasses import asdict
from datetime import date
from io import BytesIO
from zipfile import BadZipFile

from openpyxl.utils.exceptions import InvalidFileException
from sqlalchemy.orm import Session

from app.core.errors import BadRequestError
from app.features.imports.importer import import_workbook
from app.features.imports.schemas import ImportResultOut


class ImportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def import_bytes(
        self,
        data: bytes,
        *,
        event_name: str | None = None,
        event_starts_on: date | None = None,
        event_ends_on: date | None = None,
    ) -> ImportResultOut:
        try:
            result = import_workbook(
                self.db,
                BytesIO(data),
                event_name=event_name,
                event_starts_on=event_starts_on,
                event_ends_on=event_ends_on,
            )
        except (InvalidFileException, BadZipFile, KeyError) as exc:
            raise BadRequestError(
                "could not read the upload as an .xlsx guest list"
            ) from exc
        return ImportResultOut(**asdict(result))
