from fastapi import Depends
from fastapi import status
from pydantic import BaseModel

from . import get_committee_dal
from . import router
from database.data_access.committeDAL import CommitteeDAL


# Schemas
class CommitteeMain(BaseModel):
    name: str
    role: str
    designation: str
    image_url: str


@router.get("/committee", status_code=status.HTTP_200_OK)
async def get_committee_members(
    committee_dal: CommitteeDAL = Depends(get_committee_dal),
):
    return await committee_dal.fetch_all_committe_members()
