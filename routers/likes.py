from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from auth import CurrentUser
from database import get_db
from schemas import LikeResponse

router = APIRouter()

#toggle logic
@router.post("/posts/{post_id}/like", response_model=LikeResponse)
async def toggle_post_like(
    post_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    post = await db.get(models.Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    result = await db.execute(
        select(models.PostLike).where(
            models.PostLike.user_id == current_user.id,
            models.PostLike.post_id == post_id,
        )
    )
    existing = result.scalars().first()

    if existing:
        await db.delete(existing)
        post.likes -= 1
        liked = False
    else:
        db.add(models.PostLike(user_id=current_user.id, post_id=post_id))
        post.likes += 1
        liked = True

    await db.commit()
    await db.refresh(post)

    return LikeResponse(liked=liked, likes=post.likes)


# like button logic (to know exactly when a user has liked or not)
@router.get("/posts/{post_id}/like/status")
async def get_like_status(
    post_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.PostLike).where(
            models.PostLike.user_id == current_user.id,
            models.PostLike.post_id == post_id,
        )
    )
    liked = result.scalars().first() is not None
    return {"liked": liked}