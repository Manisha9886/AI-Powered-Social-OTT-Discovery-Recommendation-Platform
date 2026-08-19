from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.user_preference import UserPreference
from app.schemas.preferences import UserPreferenceCreate, UserPreferenceResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserPreferenceResponse)
def get_user_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        # Return empty default preference
        return UserPreferenceResponse(
            id=0,
            user_id=current_user.id,
            genres=[],
            duration=[],
            release_year=[],
            onboarding_completed=False,
            created_at=current_user.created_at
        )
    return pref

@router.post("/me", response_model=UserPreferenceResponse)
def save_user_preferences(
    pref_in: UserPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if pref:
        pref.genres = pref_in.genres
        pref.duration = pref_in.duration
        pref.release_year = pref_in.release_year
        pref.onboarding_completed = True
        db.commit()
        db.refresh(pref)
    else:
        pref = UserPreference(
            user_id=current_user.id,
            genres=pref_in.genres,
            duration=pref_in.duration,
            release_year=pref_in.release_year,
            onboarding_completed=True
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)
        
    return pref
