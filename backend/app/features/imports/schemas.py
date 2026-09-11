from pydantic import BaseModel


class ImportResultOut(BaseModel):
    people_created: int
    people_updated: int
    hosts_created: int
    invitations_created: int
    invitations_updated: int
    skipped: int
