from data.models import StudentRegisterData, TeacherRegisterData
from typing import Union

#
# async def create_account(data: Union[StudentRegisterData, TeacherRegisterData], hashed_password: str):
#     #   # Check if data has teacher fields
#     if hasattr(data, "mobile") and hasattr(data, "linked_in_url"):
#         # Converting if data is not yet a TeacherRegisterData
#         if not isinstance(data, TeacherRegisterData):
#             data = TeacherRegisterData(**data.model_dump())
#     else:
#         # Same for StudentRegisterData instance
#         if not isinstance(data, StudentRegisterData):
#             data = StudentRegisterData(**data.model_dump())
#
#     role, user_id = await create_account(data, hashed_password)
#     return role, user_id

