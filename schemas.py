from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

#shapes of data flow

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password:str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str = Field(min_length=1, max_length=50)
    image_file: str | None
    image_path: str


class UserPrivate(UserPublic):
    email:EmailStr = Field(max_length=120)


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class PostCreate(PostBase):
   pass


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic
    liked :bool


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)
   

class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)

class Token(BaseModel):
    access_token: str
    token_type:str

class PaginatedPostsResponse(BaseModel):
    posts: list[PostResponse]
    total:int 
    skip:int
    limit:int
    has_more: int


# Password Reset Schemas
#initial request hit(user->server)
class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)

#after reset hit -> token+ new_pass(user->server)
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

#change pass req(server->user)
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


#comments schemas
class CommentCreate(BaseModel):
    content: str = Field(min_length=1)

class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    content: str
    date_posted: datetime
    user_id: int
    post_id: int
    author: UserPublic


#likes
class LikeResponse(BaseModel):
    liked: bool  # True if just liked, False if unliked
    likes: int   # updated count