"""
Unit tests for Prompt Template models

Tests validation, template rendering, and versioning
"""

import pytest
from datetime import datetime
from app.models.prompt_template import (
    PromptTemplate,
    PromptVersion,
    PromptUsageStats
)


class TestPromptTemplate:
    """Test PromptTemplate model"""
    
    def test_valid_template(self):
        """Test creating a valid prompt template"""
        template = PromptTemplate(
            name="meal_planning_v1",
            description="Generate meal plans",
            system_prompt="You are a nutrition expert.",
            user_prompt_template="Generate a {num_days}-day meal plan for {goal}.",
            required_context_keys=["num_days", "goal"]
        )
        
        assert template.name == "meal_planning_v1"
        assert template.version == "1.0"  # Default
        assert template.is_active == True  # Default
    
    def test_name_validation_empty(self):
        """Test that empty name is rejected"""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            PromptTemplate(
                name="",
                description="Test",
                system_prompt="System",
                user_prompt_template="User"
            )
    
    def test_name_validation_invalid_chars(self):
        """Test that invalid characters in name are rejected"""
        with pytest.raises(ValueError, match="alphanumeric"):
            PromptTemplate(
                name="meal planning v1",  # Spaces not allowed
                description="Test",
                system_prompt="System",
                user_prompt_template="User"
            )
        
        with pytest.raises(ValueError, match="alphanumeric"):
            PromptTemplate(
                name="meal@planning",  # Special chars not allowed
                description="Test",
                system_prompt="System",
                user_prompt_template="User"
            )
    
    def test_name_validation_valid_chars(self):
        """Test valid name formats"""
        # Underscores OK
        template1 = PromptTemplate(
            name="meal_planning_v1",
            description="Test",
            system_prompt="System",
            user_prompt_template="User"
        )
        assert template1.name == "meal_planning_v1"
        
        # Hyphens OK
        template2 = PromptTemplate(
            name="meal-planning-v1",
            description="Test",
            system_prompt="System",
            user_prompt_template="User"
        )
        assert template2.name == "meal-planning-v1"
        
        # Numbers OK
        template3 = PromptTemplate(
            name="template123",
            description="Test",
            system_prompt="System",
            user_prompt_template="User"
        )
        assert template3.name == "template123"
    
    def test_version_validation_valid(self):
        """Test valid version formats"""
        # Major.Minor
        template1 = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="System",
            user_prompt_template="User",
            version="1.0"
        )
        assert template1.version == "1.0"
        
        # Major.Minor.Patch
        template2 = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="System",
            user_prompt_template="User",
            version="2.1.3"
        )
        assert template2.version == "2.1.3"
    
    def test_version_validation_invalid(self):
        """Test invalid version formats"""
        with pytest.raises(ValueError, match="semantic versioning"):
            PromptTemplate(
                name="test",
                description="Test",
                system_prompt="System",
                user_prompt_template="User",
                version="v1.0"  # 'v' prefix not allowed
            )
        
        with pytest.raises(ValueError, match="semantic versioning"):
            PromptTemplate(
                name="test",
                description="Test",
                system_prompt="System",
                user_prompt_template="User",
                version="1"  # Must have major.minor at minimum
            )
    
    def test_response_format_validation(self):
        """Test response format validation"""
        # Valid formats
        template1 = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="System",
            user_prompt_template="User",
            response_format="text"
        )
        assert template1.response_format == "text"
        
        template2 = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="System",
            user_prompt_template="User",
            response_format="json"
        )
        assert template2.response_format == "json"
        
        # Invalid format
        with pytest.raises(ValueError, match="Response format must be one of"):
            PromptTemplate(
                name="test",
                description="Test",
                system_prompt="System",
                user_prompt_template="User",
                response_format="xml"  # Not supported
            )
    
    def test_extract_placeholders(self):
        """Test extracting placeholders from template"""
        template = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="System",
            user_prompt_template="Create a {num_days}-day plan for {goal} with {calories} calories."
        )
        
        placeholders = template.extract_placeholders()
        
        assert "num_days" in placeholders
        assert "goal" in placeholders
        assert "calories" in placeholders
        assert len(placeholders) == 3
    
    def test_extract_placeholders_none(self):
        """Test template with no placeholders"""
        template = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="System",
            user_prompt_template="Generate a meal plan."
        )
        
        placeholders = template.extract_placeholders()
        
        assert len(placeholders) == 0
    
    def test_validate_context_success(self):
        """Test context validation with valid context"""
        template = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="System",
            user_prompt_template="Plan for {num_days} days with {goal}.",
            required_context_keys=["num_days", "goal"]
        )
        
        is_valid, error = template.validate_context({"num_days": 7, "goal": "weight_loss"})
        
        assert is_valid == True
        assert error is None
    
    def test_validate_context_missing_required_key(self):
        """Test context validation with missing required key"""
        template = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="System",
            user_prompt_template="Plan for {num_days} days.",
            required_context_keys=["num_days", "goal"]
        )
        
        is_valid, error = template.validate_context({"num_days": 7})
        
        assert is_valid == False
        assert "goal" in error
    
    def test_validate_context_missing_placeholder(self):
        """Test context validation with missing placeholder value"""
        template = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="System",
            user_prompt_template="Plan for {num_days} days with {calories} calories.",
            required_context_keys=[]
        )
        
        is_valid, error = template.validate_context({"num_days": 7})
        
        assert is_valid == False
        assert "calories" in error
    
    def test_render_success(self):
        """Test successful template rendering"""
        template = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="You are a nutrition expert.",
            user_prompt_template="Create a {num_days}-day plan for {goal} with {calories} calories.",
            required_context_keys=["num_days", "goal", "calories"]
        )
        
        system, user = template.render({
            "num_days": 7,
            "goal": "weight loss",
            "calories": 2000
        })
        
        assert system == "You are a nutrition expert."
        assert user == "Create a 7-day plan for weight loss with 2000 calories."
    
    def test_render_failure_missing_key(self):
        """Test template rendering fails with missing key"""
        template = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="System",
            user_prompt_template="Plan for {num_days} days.",
            required_context_keys=["num_days"]
        )
        
        with pytest.raises(ValueError, match="Missing"):
            template.render({})
    
    def test_render_extra_keys(self):
        """Test rendering with extra context keys (should be ignored)"""
        template = PromptTemplate(
            name="test",
            description="Test",
            system_prompt="System",
            user_prompt_template="Plan for {num_days} days.",
            required_context_keys=["num_days"]
        )
        
        system, user = template.render({
            "num_days": 7,
            "extra_key": "ignored"
        })
        
        assert user == "Plan for 7 days."
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization"""
        original = PromptTemplate(
            name="meal_plan_v1",
            description="Meal planning",
            system_prompt="Expert nutrition AI",
            user_prompt_template="Generate {num_days} days",
            version="1.5",
            tags=["nutrition", "meal_planning"]
        )
        
        data = original.to_dict()
        assert isinstance(data, dict)
        assert data['name'] == 'meal_plan_v1'
        assert data['version'] == '1.5'
        
        restored = PromptTemplate.from_dict(data)
        assert restored.name == original.name
        assert restored.version == original.version
        assert restored.tags == original.tags


class TestPromptVersion:
    """Test PromptVersion model"""
    
    def test_valid_prompt_version(self):
        """Test creating a valid prompt version"""
        version = PromptVersion(
            template_id="meal_planning_v1",
            version="1.1",
            system_prompt="Updated system prompt",
            user_prompt_template="Updated template",
            change_description="Improved wording for clarity",
            changed_by="admin123"
        )
        
        assert version.template_id == "meal_planning_v1"
        assert version.version == "1.1"
        assert version.change_description == "Improved wording for clarity"
    
    def test_to_dict_and_from_dict(self):
        """Test serialization"""
        original = PromptVersion(
            template_id="test_template",
            version="2.0",
            system_prompt="System",
            user_prompt_template="User",
            change_description="Major update"
        )
        
        data = original.to_dict()
        restored = PromptVersion.from_dict(data)
        
        assert restored.template_id == original.template_id
        assert restored.version == original.version


class TestPromptUsageStats:
    """Test PromptUsageStats model"""
    
    def test_valid_usage_stats(self):
        """Test creating valid usage stats"""
        stats = PromptUsageStats(
            template_id="meal_planning_v1",
            template_name="meal_planning_v1",
            total_uses=1000,
            successful_uses=950,
            failed_uses=50,
            avg_response_time_ms=2500.0,
            avg_tokens_used=3000.0,
            total_cost_usd=15.50,
            period_start=datetime(2025, 11, 1),
            period_end=datetime(2025, 11, 30)
        )
        
        assert stats.total_uses == 1000
        assert stats.successful_uses == 950
    
    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        stats = PromptUsageStats(
            template_id="test",
            template_name="test",
            total_uses=100,
            successful_uses=95,
            failed_uses=5,
            period_start=datetime.now(),
            period_end=datetime.now()
        )
        
        assert stats.success_rate() == 95.0
    
    def test_success_rate_zero_uses(self):
        """Test success rate with zero uses"""
        stats = PromptUsageStats(
            template_id="test",
            template_name="test",
            total_uses=0,
            successful_uses=0,
            failed_uses=0,
            period_start=datetime.now(),
            period_end=datetime.now()
        )
        
        assert stats.success_rate() == 0.0
    
    def test_success_rate_all_failed(self):
        """Test success rate with all failures"""
        stats = PromptUsageStats(
            template_id="test",
            template_name="test",
            total_uses=100,
            successful_uses=0,
            failed_uses=100,
            period_start=datetime.now(),
            period_end=datetime.now()
        )
        
        assert stats.success_rate() == 0.0
    
    def test_success_rate_perfect(self):
        """Test success rate with perfect score"""
        stats = PromptUsageStats(
            template_id="test",
            template_name="test",
            total_uses=100,
            successful_uses=100,
            failed_uses=0,
            period_start=datetime.now(),
            period_end=datetime.now()
        )
        
        assert stats.success_rate() == 100.0

