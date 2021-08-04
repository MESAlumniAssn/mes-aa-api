from fastapi import Depends
from fastapi import status
from sentry_sdk import capture_exception

from . import get_famous_alumni_dal
from . import router
from database.data_access.famous_alumniDAL import FamousAlumniDAL


@router.get("/famous_alumni/all", status_code=status.HTTP_200_OK)
async def get_famous_alumni_list(
    famous_alumni_dal: FamousAlumniDAL = Depends(get_famous_alumni_dal),
):
    try:
        return await famous_alumni_dal.fetch_all_famous_alumni()
    except Exception as e:
        capture_exception(e)
