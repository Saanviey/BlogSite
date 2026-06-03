from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import models
from database import get_db
from schemas import CommentCreate, CommentResponse
from auth import CurrentUser
from websocket_manager import manager , notification_manager

#comments router lesgo 
#stacked on top of posts-routers 
router = APIRouter()


@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Comment)
        .options(selectinload(models.Comment.author))
        .where(models.Comment.post_id == post_id)
        .order_by(models.Comment.date_posted.asc()),
    )
    return result.scalars().all()
 
 
@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
 
    new_comment = models.Comment(
        content=comment.content,
        user_id=current_user.id,
        post_id=post_id,
    )
    post_user_id = post.user_id      # save before commit
    post_title = post.title          # save before commit
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment, attribute_names=["author"])
 
    # Broadcast the new comment to everyone viewing this post
    await manager.broadcast(
        post_id,
        {
            "event": "comment_added",
            "comment": {
                "id": new_comment.id,
                "content": new_comment.content,
                "date_posted": new_comment.date_posted.isoformat(),
                "user_id": new_comment.user_id,
                "post_id": new_comment.post_id,
                "author": {
                    "id": new_comment.author.id,
                    "username": new_comment.author.username,
                    "image_path": new_comment.author.image_path,
                },
            },
        },
    )
    # notify post author if they're not the commenter
    if post_user_id != current_user.id:
        await notification_manager.send_to_user(post_user_id, {
            "type": "notification",
            "message": f"{current_user.username} commented on your post",
            "post_id": post_user_id,
            "post_title": post_title,
        })
 
    return new_comment
 
 
@router.delete(
    "/{post_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    post_id: int,
    comment_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Comment).where(
            models.Comment.id == comment_id,
            models.Comment.post_id == post_id,
        ),
    )
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )
 
    await db.delete(comment)
    await db.commit()
 
    # Broadcast the deletion to everyone viewing this post
    await manager.broadcast(
        post_id,
        {"event": "comment_deleted", "comment_id": comment_id},
    )
 