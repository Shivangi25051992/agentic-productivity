"""
Unit tests for Prompt Service

Tests template management, rendering, versioning, and caching.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.models.prompt_template import PromptTemplate, PromptVersion
from app.services.prompt_service import PromptService


class TestPromptService:
    """Test Prompt Service functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock Firestore client"""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_db):
        """Create Prompt Service instance"""
        return PromptService(db=mock_db)
    
    @pytest.fixture
    def sample_template(self):
        """Sample prompt template"""
        return PromptTemplate(
            id="test_template_1",
            name="meal_planning_v1",
            description="Generate meal plans",
            system_prompt="You are a nutrition expert.",
            user_prompt_template="Create a {num_days}-day meal plan for {goal}.",
            required_context_keys=["num_days", "goal"],
            version="1.0",
            is_active=True
        )


class TestGetTemplate(TestPromptService):
    """Test template retrieval"""
    
    @pytest.mark.asyncio
    async def test_get_template_from_firestore(self, service, sample_template):
        """Test loading template from Firestore"""
        # Mock Firestore document
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = sample_template.to_dict()
        
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        
        # Setup mock chain
        mock_templates = MagicMock()
        mock_templates.document.return_value = mock_doc_ref
        mock_prompts = MagicMock()
        mock_prompts.collection.return_value = mock_templates
        mock_admin = MagicMock()
        mock_admin.document.return_value = mock_prompts
        service.db.collection.return_value = mock_admin
        
        template = await service.get_template("test_template_1")
        
        assert template.name == "meal_planning_v1"
        assert template.id == "test_template_1"
        assert template.is_active == True
    
    @pytest.mark.asyncio
    async def test_get_template_cached(self, service, sample_template):
        """Test that templates are cached"""
        # Populate cache
        service.template_cache["test_template_1"] = sample_template
        service.last_cache_refresh["test_template_1"] = datetime.now(timezone.utc)
        
        template = await service.get_template("test_template_1")
        
        # Should get from cache without hitting Firestore
        assert template.name == "meal_planning_v1"
        service.db.collection.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_template_not_found(self, service):
        """Test error when template doesn't exist"""
        # Mock Firestore to return non-existent document
        mock_doc = MagicMock()
        mock_doc.exists = False
        
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        
        mock_templates = MagicMock()
        mock_templates.document.return_value = mock_doc_ref
        mock_prompts = MagicMock()
        mock_prompts.collection.return_value = mock_templates
        mock_admin = MagicMock()
        mock_admin.document.return_value = mock_prompts
        service.db.collection.return_value = mock_admin
        
        with pytest.raises(Exception, match="Template not found"):
            await service.get_template("nonexistent")
    
    @pytest.mark.asyncio
    async def test_get_template_inactive(self, service, sample_template):
        """Test error when template is inactive"""
        sample_template.is_active = False
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = sample_template.to_dict()
        
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        
        mock_templates = MagicMock()
        mock_templates.document.return_value = mock_doc_ref
        mock_prompts = MagicMock()
        mock_prompts.collection.return_value = mock_templates
        mock_admin = MagicMock()
        mock_admin.document.return_value = mock_prompts
        service.db.collection.return_value = mock_admin
        
        with pytest.raises(Exception, match="Template is inactive"):
            await service.get_template("test_template_1")


class TestRenderTemplate(TestPromptService):
    """Test template rendering"""
    
    @pytest.mark.asyncio
    async def test_render_template_success(self, service, sample_template):
        """Test successful template rendering"""
        # Mock get_template
        with patch.object(service, 'get_template', new=AsyncMock(return_value=sample_template)):
            # Mock increment usage
            with patch.object(service, '_increment_usage_count', new=AsyncMock()):
                system, user = await service.render_template(
                    template_id="test_template_1",
                    context={"num_days": 7, "goal": "weight loss"}
                )
                
                assert system == "You are a nutrition expert."
                assert user == "Create a 7-day meal plan for weight loss."
    
    @pytest.mark.asyncio
    async def test_render_template_missing_context(self, service, sample_template):
        """Test error when context is missing required keys"""
        with patch.object(service, 'get_template', new=AsyncMock(return_value=sample_template)):
            with pytest.raises(ValueError, match="Missing"):
                await service.render_template(
                    template_id="test_template_1",
                    context={"num_days": 7}  # Missing 'goal'
                )
    
    @pytest.mark.asyncio
    async def test_render_template_increments_usage(self, service, sample_template):
        """Test that rendering increments usage count"""
        mock_increment = AsyncMock()
        
        with patch.object(service, 'get_template', new=AsyncMock(return_value=sample_template)):
            with patch.object(service, '_increment_usage_count', new=mock_increment):
                await service.render_template(
                    template_id="test_template_1",
                    context={"num_days": 7, "goal": "weight loss"}
                )
                
                mock_increment.assert_called_once_with("test_template_1")


class TestCreateTemplate(TestPromptService):
    """Test template creation"""
    
    @pytest.mark.asyncio
    async def test_create_template_success(self, service, sample_template):
        """Test successful template creation"""
        # Mock finding existing template (should return None)
        with patch.object(service, '_find_template_by_name', new=AsyncMock(return_value=None)):
            # Mock create version
            with patch.object(service, '_create_version', new=AsyncMock()):
                # Mock Firestore
                mock_doc_ref = MagicMock()
                mock_templates = MagicMock()
                mock_templates.document.return_value = mock_doc_ref
                mock_prompts = MagicMock()
                mock_prompts.collection.return_value = mock_templates
                mock_admin = MagicMock()
                mock_admin.document.return_value = mock_prompts
                service.db.collection.return_value = mock_admin
                
                created = await service.create_template(sample_template)
                
                assert created.name == "meal_planning_v1"
                mock_doc_ref.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_template_duplicate_name(self, service, sample_template):
        """Test error when template name already exists"""
        # Mock finding existing template
        with patch.object(service, '_find_template_by_name', new=AsyncMock(return_value=sample_template)):
            with pytest.raises(Exception, match="already exists"):
                await service.create_template(sample_template)


class TestUpdateTemplate(TestPromptService):
    """Test template updates"""
    
    @pytest.mark.asyncio
    async def test_update_template_success(self, service, sample_template):
        """Test successful template update"""
        # Mock get_template (called twice - before and after update)
        mock_get = AsyncMock(side_effect=[sample_template, sample_template])
        
        with patch.object(service, 'get_template', new=mock_get):
            with patch.object(service, '_create_version', new=AsyncMock()):
                # Mock Firestore
                mock_doc_ref = MagicMock()
                mock_templates = MagicMock()
                mock_templates.document.return_value = mock_doc_ref
                mock_prompts = MagicMock()
                mock_prompts.collection.return_value = mock_templates
                mock_admin = MagicMock()
                mock_admin.document.return_value = mock_prompts
                service.db.collection.return_value = mock_admin
                
                updated = await service.update_template(
                    template_id="test_template_1",
                    updates={"description": "Updated description"},
                    change_description="Updated description field"
                )
                
                mock_doc_ref.update.assert_called_once()
                assert updated.name == "meal_planning_v1"
    
    @pytest.mark.asyncio
    async def test_update_template_clears_cache(self, service, sample_template):
        """Test that updating a template clears its cache"""
        # Populate cache
        service.template_cache["test_template_1"] = sample_template
        service.last_cache_refresh["test_template_1"] = datetime.now(timezone.utc)
        
        mock_get = AsyncMock(side_effect=[sample_template, sample_template])
        
        with patch.object(service, 'get_template', new=mock_get):
            with patch.object(service, '_create_version', new=AsyncMock()):
                mock_doc_ref = MagicMock()
                mock_templates = MagicMock()
                mock_templates.document.return_value = mock_doc_ref
                mock_prompts = MagicMock()
                mock_prompts.collection.return_value = mock_templates
                mock_admin = MagicMock()
                mock_admin.document.return_value = mock_prompts
                service.db.collection.return_value = mock_admin
                
                await service.update_template(
                    template_id="test_template_1",
                    updates={"description": "Updated"}
                )
                
                # Cache should be cleared
                assert "test_template_1" not in service.template_cache
                assert "test_template_1" not in service.last_cache_refresh


class TestListTemplates(TestPromptService):
    """Test listing templates"""
    
    @pytest.mark.asyncio
    async def test_list_templates_active_only(self, service, sample_template):
        """Test listing only active templates"""
        # Mock Firestore query
        mock_doc = MagicMock()
        mock_doc.id = sample_template.id
        mock_doc.to_dict.return_value = sample_template.to_dict()
        
        mock_stream = [mock_doc]
        
        mock_where = MagicMock()
        mock_where.stream.return_value = mock_stream
        
        mock_templates = MagicMock()
        mock_templates.where.return_value = mock_where
        
        mock_prompts = MagicMock()
        mock_prompts.collection.return_value = mock_templates
        
        mock_admin = MagicMock()
        mock_admin.document.return_value = mock_prompts
        
        service.db.collection.return_value = mock_admin
        
        templates = await service.list_templates(active_only=True)
        
        assert len(templates) == 1
        assert templates[0].name == "meal_planning_v1"
        mock_templates.where.assert_called_once_with('is_active', '==', True)
    
    @pytest.mark.asyncio
    async def test_list_templates_filter_by_tags(self, service, sample_template):
        """Test filtering templates by tags"""
        sample_template.tags = ["nutrition", "meal_planning"]
        
        mock_doc = MagicMock()
        mock_doc.id = sample_template.id
        mock_doc.to_dict.return_value = sample_template.to_dict()
        
        mock_where = MagicMock()
        mock_where.stream.return_value = [mock_doc]
        
        mock_templates = MagicMock()
        mock_templates.where.return_value = mock_where
        
        mock_prompts = MagicMock()
        mock_prompts.collection.return_value = mock_templates
        
        mock_admin = MagicMock()
        mock_admin.document.return_value = mock_prompts
        
        service.db.collection.return_value = mock_admin
        
        templates = await service.list_templates(tags=["nutrition"])
        
        assert len(templates) == 1
        assert "nutrition" in templates[0].tags


class TestVersionManagement(TestPromptService):
    """Test version management"""
    
    @pytest.mark.asyncio
    async def test_get_template_versions(self, service):
        """Test getting version history"""
        version = PromptVersion(
            template_id="test_template_1",
            version="1.0",
            system_prompt="System",
            user_prompt_template="User",
            change_description="Initial version"
        )
        
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = version.to_dict()
        
        # Create mock chain for: .order_by().limit().stream()
        mock_versions_ref = MagicMock()
        mock_versions_ref.order_by = MagicMock(return_value=mock_versions_ref)
        mock_versions_ref.limit = MagicMock(return_value=mock_versions_ref)
        mock_versions_ref.stream.return_value = [mock_doc]
        
        mock_template_doc = MagicMock()
        mock_template_doc.collection.return_value = mock_versions_ref
        
        mock_templates = MagicMock()
        mock_templates.document.return_value = mock_template_doc
        
        mock_prompts = MagicMock()
        mock_prompts.collection.return_value = mock_templates
        
        mock_admin = MagicMock()
        mock_admin.document.return_value = mock_prompts
        
        service.db.collection.return_value = mock_admin
        
        versions = await service.get_template_versions("test_template_1")
        
        assert len(versions) == 1
        assert versions[0].version == "1.0"


class TestCaching(TestPromptService):
    """Test caching behavior"""
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, service, sample_template):
        """Test cache clearing"""
        # Populate cache
        service.template_cache["test_template_1"] = sample_template
        service.last_cache_refresh["test_template_1"] = datetime.now(timezone.utc)
        
        await service.clear_cache()
        
        assert len(service.template_cache) == 0
        assert len(service.last_cache_refresh) == 0

