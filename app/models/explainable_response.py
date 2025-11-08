"""
Explainable AI Response Models

Data models for confidence scoring, explanations, and alternative suggestions
Part of Phase 2: Explainable AI & Context Management
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence level categories"""
    very_high = "very_high"  # 0.9 - 1.0
    high = "high"            # 0.8 - 0.9
    medium = "medium"        # 0.7 - 0.8
    low = "low"              # 0.5 - 0.7
    very_low = "very_low"    # 0.0 - 0.5


class ConfidenceFactors(BaseModel):
    """Factors contributing to confidence score"""
    input_clarity: float = Field(ge=0.0, le=1.0, description="How clear/ambiguous was the input")
    data_completeness: float = Field(ge=0.0, le=1.0, description="How much data is available")
    model_certainty: float = Field(ge=0.0, le=1.0, description="Model's internal confidence")
    historical_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Past accuracy for similar requests")
    
    model_config = ConfigDict(extra='allow')


class AlternativeInterpretation(BaseModel):
    """Alternative interpretation of user input"""
    interpretation: str = Field(description="Human-readable interpretation")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in this interpretation")
    explanation: str = Field(description="Why this is plausible")
    data: Dict[str, Any] = Field(default_factory=dict, description="Structured data for this interpretation")
    
    model_config = ConfigDict(extra='allow')


class ResponseExplanation(BaseModel):
    """Explanation of AI reasoning"""
    reasoning: str = Field(description="Step-by-step reasoning")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made")
    why_this_classification: Optional[str] = Field(None, description="Why this category/classification")
    confidence_breakdown: Optional[Dict[str, float]] = Field(None, description="Detailed confidence factors")
    
    model_config = ConfigDict(extra='allow')


class ExplainableResponse(BaseModel):
    """
    AI Response with confidence, explanations, and alternatives
    
    This is the main response model for Phase 2 Explainable AI
    """
    
    # Primary response (existing)
    response: str = Field(description="The main AI response text")
    items: List[Dict[str, Any]] = Field(default_factory=list, description="Parsed items")
    
    # Phase 2: Explainability fields
    confidence_score: float = Field(ge=0.0, le=1.0, description="Overall confidence (0.0 - 1.0)")
    confidence_level: ConfidenceLevel = Field(description="Human-readable confidence level")
    confidence_factors: ConfidenceFactors = Field(description="Factors contributing to confidence")
    
    explanation: ResponseExplanation = Field(description="Why AI made this decision")
    
    alternatives: List[AlternativeInterpretation] = Field(
        default_factory=list,
        description="Alternative interpretations (if confidence < 0.8)"
    )
    
    needs_clarification: bool = Field(
        default=False,
        description="Whether AI needs user clarification (confidence < 0.7)"
    )
    
    clarification_question: Optional[str] = Field(
        None,
        description="Question to ask user for clarification"
    )
    
    # Metadata
    model_used: Optional[str] = Field(None, description="Which LLM was used")
    processing_time_ms: Optional[int] = Field(None, description="How long it took")
    
    model_config = ConfigDict(extra='allow')
    
    @classmethod
    def determine_confidence_level(cls, score: float) -> ConfidenceLevel:
        """Convert numeric score to confidence level"""
        if score >= 0.9:
            return ConfidenceLevel.very_high
        elif score >= 0.8:
            return ConfidenceLevel.high
        elif score >= 0.7:
            return ConfidenceLevel.medium
        elif score >= 0.5:
            return ConfidenceLevel.low
        else:
            return ConfidenceLevel.very_low


class UserFeedback(BaseModel):
    """User feedback on AI response"""
    feedback_id: str = Field(description="Unique feedback ID")
    user_id: str = Field(description="User who gave feedback")
    message_id: str = Field(description="Message being rated")
    
    rating: str = Field(description="helpful|not_helpful|incorrect")
    correction: Optional[str] = Field(None, description="User's correction if AI was wrong")
    feedback_type: str = Field(description="classification|calories|timing|other")
    
    # Context
    ai_confidence: float = Field(ge=0.0, le=1.0, description="AI's original confidence")
    was_correct: bool = Field(description="Whether AI was actually correct")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(extra='allow')


class ConfidenceScoreRequest(BaseModel):
    """Request to calculate confidence score"""
    user_input: str = Field(description="User's original input")
    parsed_items: List[Dict[str, Any]] = Field(description="What AI parsed")
    llm_response: Dict[str, Any] = Field(description="Raw LLM response")
    user_history: Optional[Dict[str, Any]] = Field(None, description="User's historical data")
    
    model_config = ConfigDict(extra='allow')

