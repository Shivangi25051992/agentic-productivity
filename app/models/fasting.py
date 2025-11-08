"""
Fasting Domain Models - Enterprise Architecture
Follows Domain-Driven Design (DDD) principles with clear boundaries
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class FastingProtocol(str, Enum):
    """Supported intermittent fasting protocols"""
    SIXTEEN_EIGHT = "16:8"
    EIGHTEEN_SIX = "18:6"
    TWENTY_FOUR = "20:4"
    OMAD = "OMAD"
    FIVE_TWO = "5:2"
    CUSTOM = "custom"


class FastingStage(str, Enum):
    """Metabolic stages during fasting"""
    ANABOLIC = "anabolic"  # 0-4h: Digesting
    CATABOLIC = "catabolic"  # 4-16h: Fat burning
    AUTOPHAGY_LIGHT = "autophagy_light"  # 16-24h: Cellular cleanup begins
    AUTOPHAGY_DEEP = "autophagy_deep"  # 24-48h: Deep autophagy
    GROWTH_HORMONE = "growth_hormone"  # 48-72h: GH peak


class BreakReason(str, Enum):
    """Reasons for breaking a fast"""
    COMPLETED = "completed"
    HUNGER = "hunger"
    SOCIAL = "social"
    WEAKNESS = "weakness"
    STRESS = "stress"
    PLANNED = "planned"
    OTHER = "other"


class ExperienceLevel(str, Enum):
    """User's fasting experience"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# ============================================================================
# DOMAIN ENTITIES
# ============================================================================

class FastingSession(BaseModel):
    """
    Represents a single fasting session
    
    Aggregate Root in DDD terminology
    Encapsulates all business logic for a fasting session
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    target_duration_hours: int
    actual_duration_hours: Optional[float] = None
    protocol: FastingProtocol
    break_reason: Optional[BreakReason] = None
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    hunger_level: Optional[int] = Field(None, ge=1, le=5)
    mood: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('energy_level', 'hunger_level')
    def validate_levels(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Level must be between 1 and 5')
        return v
    
    @property
    def current_duration_hours(self) -> float:
        """Calculate current duration in hours"""
        if self.end_time:
            delta = self.end_time - self.start_time
        else:
            delta = datetime.utcnow() - self.start_time
        return delta.total_seconds() / 3600
    
    @property
    def current_stage(self) -> FastingStage:
        """Determine current metabolic stage"""
        hours = self.current_duration_hours
        if hours < 4:
            return FastingStage.ANABOLIC
        elif hours < 16:
            return FastingStage.CATABOLIC
        elif hours < 24:
            return FastingStage.AUTOPHAGY_LIGHT
        elif hours < 48:
            return FastingStage.AUTOPHAGY_DEEP
        else:
            return FastingStage.GROWTH_HORMONE
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress towards target"""
        if self.target_duration_hours == 0:
            return 0.0
        return min((self.current_duration_hours / self.target_duration_hours) * 100, 100.0)
    
    @property
    def is_completed(self) -> bool:
        """Check if fast was completed successfully"""
        return (
            self.end_time is not None and 
            self.break_reason == BreakReason.COMPLETED and
            self.actual_duration_hours >= self.target_duration_hours
        )
    
    def complete(self, reason: BreakReason, energy: int, hunger: int, notes: str = None):
        """Complete the fasting session"""
        self.end_time = datetime.utcnow()
        self.actual_duration_hours = self.current_duration_hours
        self.break_reason = reason
        self.energy_level = energy
        self.hunger_level = hunger
        self.notes = notes
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "target_duration_hours": self.target_duration_hours,
            "actual_duration_hours": self.actual_duration_hours,
            "protocol": self.protocol.value,
            "break_reason": self.break_reason.value if self.break_reason else None,
            "energy_level": self.energy_level,
            "hunger_level": self.hunger_level,
            "mood": self.mood,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FastingSession":
        """Create from Firestore dictionary"""
        return cls(
            id=data.get("id"),
            user_id=data["user_id"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            target_duration_hours=data["target_duration_hours"],
            actual_duration_hours=data.get("actual_duration_hours"),
            protocol=FastingProtocol(data["protocol"]),
            break_reason=BreakReason(data["break_reason"]) if data.get("break_reason") else None,
            energy_level=data.get("energy_level"),
            hunger_level=data.get("hunger_level"),
            mood=data.get("mood"),
            notes=data.get("notes"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
        )


class FastingProfile(BaseModel):
    """
    User's fasting preferences and settings
    
    Value Object in DDD terminology
    """
    user_id: str
    default_protocol: FastingProtocol = FastingProtocol.SIXTEEN_EIGHT
    eating_window_start: str = "12:00"  # HH:MM format
    eating_window_end: str = "20:00"
    goals: str = "weight_loss"
    experience_level: ExperienceLevel = ExperienceLevel.BEGINNER
    reminder_enabled: bool = True
    reminder_before_window_minutes: int = 30
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('eating_window_start', 'eating_window_end')
    def validate_time_format(cls, v):
        """Validate HH:MM format"""
        try:
            hours, minutes = v.split(':')
            if not (0 <= int(hours) < 24 and 0 <= int(minutes) < 60):
                raise ValueError
        except:
            raise ValueError('Time must be in HH:MM format (00:00 to 23:59)')
        return v
    
    @property
    def eating_window_duration_hours(self) -> int:
        """Calculate eating window duration"""
        start_h, start_m = map(int, self.eating_window_start.split(':'))
        end_h, end_m = map(int, self.eating_window_end.split(':'))
        
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        
        if end_minutes < start_minutes:
            # Window crosses midnight
            duration = (24 * 60 - start_minutes) + end_minutes
        else:
            duration = end_minutes - start_minutes
        
        return duration // 60
    
    @property
    def fasting_window_duration_hours(self) -> int:
        """Calculate fasting window duration"""
        return 24 - self.eating_window_duration_hours
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore"""
        return {
            "user_id": self.user_id,
            "default_protocol": self.default_protocol.value,
            "eating_window_start": self.eating_window_start,
            "eating_window_end": self.eating_window_end,
            "goals": self.goals,
            "experience_level": self.experience_level.value,
            "reminder_enabled": self.reminder_enabled,
            "reminder_before_window_minutes": self.reminder_before_window_minutes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FastingProfile":
        """Create from Firestore dictionary"""
        return cls(
            user_id=data["user_id"],
            default_protocol=FastingProtocol(data.get("default_protocol", "16:8")),
            eating_window_start=data.get("eating_window_start", "12:00"),
            eating_window_end=data.get("eating_window_end", "20:00"),
            goals=data.get("goals", "weight_loss"),
            experience_level=ExperienceLevel(data.get("experience_level", "beginner")),
            reminder_enabled=data.get("reminder_enabled", True),
            reminder_before_window_minutes=data.get("reminder_before_window_minutes", 30),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
        )


# ============================================================================
# DTOs (Data Transfer Objects)
# ============================================================================

class StartFastingRequest(BaseModel):
    """Request to start a new fasting session"""
    protocol: FastingProtocol
    target_duration_hours: int = Field(ge=1, le=72)
    notes: Optional[str] = None


class EndFastingRequest(BaseModel):
    """Request to end a fasting session"""
    break_reason: BreakReason
    energy_level: int = Field(ge=1, le=5)
    hunger_level: int = Field(ge=1, le=5)
    mood: Optional[str] = None
    notes: Optional[str] = None


class FastingAnalytics(BaseModel):
    """Analytics data for fasting performance"""
    user_id: str
    period_days: int
    total_fasts: int
    completed_fasts: int
    completion_rate: float
    average_duration_hours: float
    longest_fast_hours: float
    current_streak_days: int
    total_fasting_hours: float
    break_reasons: Dict[str, int]
    average_energy_level: Optional[float] = None
    average_hunger_level: Optional[float] = None
    best_time_of_day: Optional[str] = None  # When user completes most fasts


class FastingSessionResponse(BaseModel):
    """Response for fasting session queries"""
    session: FastingSession
    current_stage: FastingStage
    progress_percentage: float
    time_remaining_hours: Optional[float] = None
    next_stage: Optional[FastingStage] = None
    next_stage_in_hours: Optional[float] = None

