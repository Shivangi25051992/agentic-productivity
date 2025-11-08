"""
Integration Tests: Chat Classification Regression Tests

These tests ensure Phase 1 LLM Router integration does not break existing chat functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.models.llm_config import LLMRequest, LLMResponse


class TestChatClassificationRegression:
    """
    Regression tests for chat classification
    
    Tests ensure the new LLM Router integration maintains 100% backward compatibility
    with existing chat classification functionality.
    """
    
    @pytest.fixture
    def sample_llm_response(self):
        """Sample LLM response for chat classification"""
        return LLMResponse(
            content='{"items": [{"category": "meal", "summary": "2 eggs for breakfast", "data": {"item": "eggs", "quantity": "2", "meal_type": "breakfast", "calories": 140, "protein_g": 12, "carbs_g": 1, "fat_g": 10, "fiber_g": 0, "confidence_category": 1.0, "confidence_meal_type": 1.0, "confidence_macros": 0.95}}], "needs_clarification": false, "clarification_questions": []}',
            tokens_used=150,
            prompt_tokens=100,
            completion_tokens=50,
            response_time_ms=250,
            provider_used="openai",
            model_used="gpt-4o-mini",
            success=True
        )
    
    @pytest.mark.asyncio
    async def test_router_available_uses_router(self, sample_llm_response):
        """Test that when router is available, it's used for classification"""
        # This test verifies the integration uses the router when available
        
        # Mock the router
        mock_router = AsyncMock()
        mock_router.route_request = AsyncMock(return_value=sample_llm_response)
        
        # Mock the global router variable
        with patch('app.main._llm_router', mock_router):
            from app.main import _classify_with_llm
            
            # Call classification
            items, needs_clarification, clarification_question = await _classify_with_llm(
                text="2 eggs for breakfast",
                user_id="test_user_123"
            )
            
            # Verify router was called
            assert mock_router.route_request.called
            
            # Verify result
            assert len(items) == 1
            assert items[0].category == "meal"
            assert items[0].data["calories"] == 140
            assert needs_clarification == False
    
    @pytest.mark.asyncio
    async def test_router_failure_falls_back_to_openai(self):
        """Test that when router fails, it falls back to direct OpenAI"""
        
        # Mock router that raises an exception
        mock_router = AsyncMock()
        mock_router.route_request = AsyncMock(side_effect=Exception("Router unavailable"))
        
        # Mock OpenAI client
        mock_openai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"items": [{"category": "meal", "summary": "2 eggs", "data": {"item": "eggs", "quantity": "2", "calories": 140, "protein_g": 12, "carbs_g": 1, "fat_g": 10, "confidence_category": 1.0, "confidence_meal_type": 1.0, "confidence_macros": 0.95}}], "needs_clarification": false, "clarification_questions": []}'
        mock_openai_client.chat.completions.create = MagicMock(return_value=mock_response)
        
        with patch('app.main._llm_router', mock_router):
            with patch('app.main._get_openai_client', return_value=mock_openai_client):
                from app.main import _classify_with_llm
                
                # Call classification
                items, needs_clarification, clarification_question = await _classify_with_llm(
                    text="2 eggs for breakfast"
                )
                
                # Verify router was attempted
                assert mock_router.route_request.called
                
                # Verify OpenAI fallback was used
                assert mock_openai_client.chat.completions.create.called
                
                # Verify result is still correct
                assert len(items) == 1
                assert items[0].category == "meal"
    
    @pytest.mark.asyncio
    async def test_router_not_initialized_uses_direct_openai(self):
        """Test that when router is not initialized, direct OpenAI is used"""
        
        # Mock OpenAI client
        mock_openai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"items": [{"category": "workout", "summary": "5K run", "data": {"item": "running", "quantity": "5 km", "activity_type": "run", "duration_minutes": 30, "calories_burned": 400, "confidence_category": 1.0}}], "needs_clarification": false, "clarification_questions": []}'
        mock_openai_client.chat.completions.create = MagicMock(return_value=mock_response)
        
        # Set router to None (not initialized)
        with patch('app.main._llm_router', None):
            with patch('app.main._get_openai_client', return_value=mock_openai_client):
                from app.main import _classify_with_llm
                
                # Call classification
                items, needs_clarification, clarification_question = await _classify_with_llm(
                    text="ran 5km"
                )
                
                # Verify OpenAI was used directly
                assert mock_openai_client.chat.completions.create.called
                
                # Verify result
                assert len(items) == 1
                assert items[0].category == "workout"
    
    @pytest.mark.asyncio
    async def test_meal_classification_with_router(self, sample_llm_response):
        """Test meal classification through router"""
        
        mock_router = AsyncMock()
        mock_router.route_request = AsyncMock(return_value=sample_llm_response)
        
        with patch('app.main._llm_router', mock_router):
            from app.main import _classify_with_llm
            
            items, needs_clarification, _ = await _classify_with_llm(
                text="2 eggs for breakfast",
                user_id="test_user"
            )
            
            # Verify meal details
            assert len(items) == 1
            assert items[0].category == "meal"
            assert items[0].data["meal_type"] == "breakfast"
            assert items[0].data["calories"] == 140
            assert items[0].data["protein_g"] == 12
            assert not needs_clarification
    
    @pytest.mark.asyncio
    async def test_workout_classification_with_router(self):
        """Test workout classification through router"""
        
        workout_response = LLMResponse(
            content='{"items": [{"category": "workout", "summary": "5K run", "data": {"item": "running", "quantity": "5 km", "activity_type": "run", "duration_minutes": 30, "intensity": "moderate", "calories_burned": 400, "confidence_category": 1.0}}], "needs_clarification": false, "clarification_questions": []}',
            tokens_used=120,
            prompt_tokens=80,
            completion_tokens=40,
            response_time_ms=200,
            provider_used="openai",
            model_used="gpt-4o-mini",
            success=True
        )
        
        mock_router = AsyncMock()
        mock_router.route_request = AsyncMock(return_value=workout_response)
        
        with patch('app.main._llm_router', mock_router):
            from app.main import _classify_with_llm
            
            items, needs_clarification, _ = await _classify_with_llm(
                text="ran 5km",
                user_id="test_user"
            )
            
            # Verify workout details
            assert len(items) == 1
            assert items[0].category == "workout"
            assert items[0].data["activity_type"] == "run"
            assert items[0].data["calories_burned"] == 400
            assert not needs_clarification
    
    @pytest.mark.asyncio
    async def test_water_tracking_with_router(self):
        """Test water tracking through router"""
        
        water_response = LLMResponse(
            content='{"items": [{"category": "water", "summary": "2 glasses of water (500ml)", "data": {"item": "water", "quantity": "2 glasses", "quantity_ml": 500, "water_unit": "glasses", "calories": 0, "confidence_category": 1.0}}], "needs_clarification": false, "clarification_questions": []}',
            tokens_used=100,
            prompt_tokens=70,
            completion_tokens=30,
            response_time_ms=180,
            provider_used="gemini",
            model_used="gemini-1.5-flash",
            success=True
        )
        
        mock_router = AsyncMock()
        mock_router.route_request = AsyncMock(return_value=water_response)
        
        with patch('app.main._llm_router', mock_router):
            from app.main import _classify_with_llm
            
            items, needs_clarification, _ = await _classify_with_llm(
                text="drank 2 glasses of water",
                user_id="test_user"
            )
            
            # Verify water tracking
            assert len(items) == 1
            assert items[0].category == "water"
            assert items[0].data["quantity_ml"] == 500
            assert items[0].data["calories"] == 0
            assert not needs_clarification
    
    @pytest.mark.asyncio
    async def test_supplement_tracking_with_router(self):
        """Test supplement tracking through router"""
        
        supplement_response = LLMResponse(
            content='{"items": [{"category": "supplement", "summary": "Vitamin D 1000 IU", "data": {"item": "vitamin d", "quantity": "1 tablet", "supplement_type": "vitamin", "supplement_name": "Vitamin D", "dosage": "1000 IU", "calories": 5, "confidence_category": 1.0}}], "needs_clarification": false, "clarification_questions": []}',
            tokens_used=110,
            prompt_tokens=75,
            completion_tokens=35,
            response_time_ms=190,
            provider_used="groq",
            model_used="mixtral-8x7b-32768",
            success=True
        )
        
        mock_router = AsyncMock()
        mock_router.route_request = AsyncMock(return_value=supplement_response)
        
        with patch('app.main._llm_router', mock_router):
            from app.main import _classify_with_llm
            
            items, needs_clarification, _ = await _classify_with_llm(
                text="took vitamin d 1000 IU",
                user_id="test_user"
            )
            
            # Verify supplement tracking
            assert len(items) == 1
            assert items[0].category == "supplement"
            assert items[0].data["supplement_name"] == "Vitamin D"
            assert items[0].data["dosage"] == "1000 IU"
            assert not needs_clarification
    
    @pytest.mark.asyncio
    async def test_multi_item_classification_with_router(self):
        """Test multi-item classification (meal + workout + supplement)"""
        
        multi_response = LLMResponse(
            content='{"items": [{"category": "meal", "summary": "2 eggs for breakfast", "data": {"item": "eggs", "quantity": "2", "meal_type": "breakfast", "calories": 140, "protein_g": 12, "carbs_g": 1, "fat_g": 10, "confidence_category": 1.0, "confidence_meal_type": 1.0, "confidence_macros": 0.95}}, {"category": "workout", "summary": "5K run", "data": {"item": "running", "quantity": "5 km", "activity_type": "run", "duration_minutes": 30, "calories_burned": 400, "confidence_category": 1.0}}, {"category": "supplement", "summary": "1 multivitamin", "data": {"item": "multivitamin", "quantity": "1 tablet", "supplement_type": "multivitamin", "calories": 5, "confidence_category": 1.0}}], "needs_clarification": false, "clarification_questions": []}',
            tokens_used=250,
            prompt_tokens=150,
            completion_tokens=100,
            response_time_ms=400,
            provider_used="openai",
            model_used="gpt-4o-mini",
            success=True
        )
        
        mock_router = AsyncMock()
        mock_router.route_request = AsyncMock(return_value=multi_response)
        
        with patch('app.main._llm_router', mock_router):
            from app.main import _classify_with_llm
            
            items, needs_clarification, _ = await _classify_with_llm(
                text="2 eggs for breakfast\nran 5km\n1 multivitamin",
                user_id="test_user"
            )
            
            # Verify all 3 items were parsed
            assert len(items) == 3
            assert items[0].category == "meal"
            assert items[1].category == "workout"
            assert items[2].category == "supplement"
            assert not needs_clarification
    
    @pytest.mark.asyncio
    async def test_clarification_needed_with_router(self):
        """Test clarification flow through router"""
        
        clarification_response = LLMResponse(
            content='{"items": [{"category": "meal", "summary": "Rice logged", "data": {"item": "rice", "calories": 200, "confidence_category": 1.0, "confidence_meal_type": 0.5, "confidence_macros": 0.5}}], "needs_clarification": true, "clarification_questions": ["How much rice did you eat? (e.g., 1 cup, 100g)"]}',
            tokens_used=130,
            prompt_tokens=90,
            completion_tokens=40,
            response_time_ms=220,
            provider_used="openai",
            model_used="gpt-4o-mini",
            success=True
        )
        
        mock_router = AsyncMock()
        mock_router.route_request = AsyncMock(return_value=clarification_response)
        
        with patch('app.main._llm_router', mock_router):
            from app.main import _classify_with_llm
            
            items, needs_clarification, clarification_question = await _classify_with_llm(
                text="ate rice",
                user_id="test_user"
            )
            
            # Verify clarification is requested
            assert len(items) == 1
            assert needs_clarification == True
            assert clarification_question is not None
            assert "How much rice" in clarification_question


class TestRouterIntegrationLogging:
    """Test that router integration logs correctly"""
    
    @pytest.mark.asyncio
    async def test_router_success_logs_provider(self, capsys):
        """Test that successful router calls log the provider used"""
        
        mock_response = LLMResponse(
            content='{"items": [{"category": "meal", "summary": "test", "data": {"item": "test", "calories": 100, "confidence_category": 1.0}}], "needs_clarification": false, "clarification_questions": []}',
            tokens_used=100,
            prompt_tokens=70,
            completion_tokens=30,
            response_time_ms=200,
            provider_used="gemini",
            model_used="gemini-1.5-flash",
            success=True
        )
        
        mock_router = AsyncMock()
        mock_router.route_request = AsyncMock(return_value=mock_response)
        
        with patch('app.main._llm_router', mock_router):
            from app.main import _classify_with_llm
            
            await _classify_with_llm(text="test", user_id="test_user")
            
            # Capture print output
            captured = capsys.readouterr()
            
            # Verify router success was logged
            assert "AGENTIC AI" in captured.out
            assert "Router success" in captured.out
            assert "gemini" in captured.out
    
    @pytest.mark.asyncio
    async def test_router_failure_logs_fallback(self, capsys):
        """Test that router failures log the fallback"""
        
        mock_router = AsyncMock()
        mock_router.route_request = AsyncMock(side_effect=Exception("Test error"))
        
        mock_openai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"items": [{"category": "meal", "summary": "test", "data": {"item": "test", "calories": 100, "confidence_category": 1.0}}], "needs_clarification": false, "clarification_questions": []}'
        mock_openai_client.chat.completions.create = MagicMock(return_value=mock_response)
        
        with patch('app.main._llm_router', mock_router):
            with patch('app.main._get_openai_client', return_value=mock_openai_client):
                from app.main import _classify_with_llm
                
                await _classify_with_llm(text="test")
                
                # Capture print output
                captured = capsys.readouterr()
                
                # Verify fallback was logged
                assert "Router failed" in captured.out
                assert "falling back to direct OpenAI" in captured.out


class TestBackwardCompatibility:
    """Test backward compatibility with existing chat behavior"""
    
    @pytest.mark.asyncio
    async def test_openai_fallback_preserves_behavior(self):
        """Test that OpenAI fallback produces identical results to before"""
        
        # Mock OpenAI client with expected response
        mock_openai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"items": [{"category": "meal", "summary": "2 eggs for breakfast (140 kcal)", "data": {"item": "eggs", "quantity": "2", "meal_type": "breakfast", "calories": 140, "protein_g": 12, "carbs_g": 1, "fat_g": 10, "fiber_g": 0, "confidence_category": 1.0, "confidence_meal_type": 1.0, "confidence_macros": 0.95}}], "needs_clarification": false, "clarification_questions": []}'
        mock_openai_client.chat.completions.create = MagicMock(return_value=mock_response)
        
        # Test with router disabled (None)
        with patch('app.main._llm_router', None):
            with patch('app.main._get_openai_client', return_value=mock_openai_client):
                from app.main import _classify_with_llm
                
                items, needs_clarification, _ = await _classify_with_llm(
                    text="2 eggs for breakfast"
                )
                
                # Verify behavior matches pre-router expectations
                assert len(items) == 1
                assert items[0].category == "meal"
                assert items[0].data["meal_type"] == "breakfast"
                assert items[0].data["calories"] == 140
                assert items[0].data["protein_g"] == 12
                assert not needs_clarification
                
                # Verify OpenAI was called with correct parameters
                call_args = mock_openai_client.chat.completions.create.call_args
                assert call_args.kwargs["temperature"] == 0.2
                assert call_args.kwargs["response_format"] == {"type": "json_object"}

