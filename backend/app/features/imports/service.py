from dataclasses import asdict
from io import BytesIO
from zipfile import BadZipFile

from openpyxl.utils.exceptions import InvalidFileException
from sqlalchemy.orm import Session

from app.core.errors import BadRequestError
from app.features.imports.importer import SessionParseError, import_workbook
from app.features.imports.schemas import ImportResultOut


class ImportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def import_bytes(self, data: bytes) -> ImportResultOut:
        try:
            result = import_workbook(self.db, BytesIO(data))
        except (InvalidFileException, BadZipFile, KeyError) as exc:
            self.db.rollback()
            raise BadRequestError(
                "could not read the upload as an .xlsx guest list"
            ) from exc
        except SessionParseError as exc:
            self.db.rollback()
            raise BadRequestError(
                f"import aborted, nothing was saved: {exc}"
            ) from exc
        return ImportResultOut(**asdict(result))
