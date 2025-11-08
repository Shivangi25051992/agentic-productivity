"""
Prompt Management Service

Manages LLM prompt templates with:
- Loading templates from Firestore
- Template rendering with context variables
- Version control and tracking
- Template caching for performance
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from google.cloud import firestore

from app.models.prompt_template import (
    PromptTemplate,
    PromptVersion,
    PromptUsageStats
)


class PromptService:
    """
    Prompt Management Service
    
    Features:
    - Load prompt templates from Firestore
    - Render templates with context variables
    - Track template usage
    - Version management
    - Template caching
    """
    
    def __init__(self, db: firestore.Client):
        """
        Initialize Prompt Service
        
        Args:
            db: Firestore client
        """
        self.db = db
        self.template_cache: Dict[str, PromptTemplate] = {}
        self.cache_ttl_seconds = 300  # Cache templates for 5 minutes
        self.last_cache_refresh: Dict[str, datetime] = {}
    
    async def get_template(self, template_id: str) -> PromptTemplate:
        """
        Get prompt template by ID
        
        Args:
            template_id: Template identifier
        
        Returns:
            PromptTemplate object
        
        Raises:
            Exception: If template not found or inactive
        """
        # Check cache
        if template_id in self.template_cache:
            # Check cache age
            last_refresh = self.last_cache_refresh.get(template_id)
            if last_refresh:
                age_seconds = (datetime.now(timezone.utc) - last_refresh).total_seconds()
                if age_seconds < self.cache_ttl_seconds:
                    return self.template_cache[template_id]
        
        # Load from Firestore
        try:
            template_ref = self.db.collection('admin').document('prompts')\
                                  .collection('templates').document(template_id)
            doc = template_ref.get()
            
            if not doc.exists:
                raise Exception(f"Template not found: {template_id}")
            
            template = PromptTemplate.from_dict(doc.to_dict())
            
            if not template.is_active:
                raise Exception(f"Template is inactive: {template_id}")
            
            # Update cache
            self.template_cache[template_id] = template
            self.last_cache_refresh[template_id] = datetime.now(timezone.utc)
            
            return template
            
        except Exception as e:
            print(f"❌ [PROMPT SERVICE] Error loading template {template_id}: {e}")
            raise
    
    async def render_template(
        self,
        template_id: str,
        context: Dict[str, Any]
    ) -> tuple[str, str]:
        """
        Render prompt template with context
        
        Args:
            template_id: Template identifier
            context: Context variables for template
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        
        Raises:
            Exception: If template not found or context invalid
        """
        # Get template
        template = await self.get_template(template_id)
        
        # Render with context
        try:
            system_prompt, user_prompt = template.render(context)
            
            # Increment usage count
            await self._increment_usage_count(template_id)
            
            return system_prompt, user_prompt
            
        except Exception as e:
            print(f"❌ [PROMPT SERVICE] Error rendering template {template_id}: {e}")
            raise
    
    async def create_template(self, template: PromptTemplate) -> PromptTemplate:
        """
        Create new prompt template
        
        Args:
            template: Template to create
        
        Returns:
            Created template with ID
        
        Raises:
            Exception: If template with same name already exists
        """
        try:
            # Check if template with same name exists
            existing = await self._find_template_by_name(template.name)
            if existing:
                raise Exception(f"Template with name '{template.name}' already exists")
            
            # Save to Firestore
            template_ref = self.db.collection('admin').document('prompts')\
                                  .collection('templates').document(template.id)
            template_ref.set(template.to_dict())
            
            # Create initial version
            await self._create_version(
                template=template,
                change_description="Initial version",
                changed_by=template.created_by
            )
            
            print(f"✅ [PROMPT SERVICE] Created template: {template.name} (v{template.version})")
            
            return template
            
        except Exception as e:
            print(f"❌ [PROMPT SERVICE] Error creating template: {e}")
            raise
    
    async def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any],
        changed_by: Optional[str] = None,
        change_description: str = "Updated template"
    ) -> PromptTemplate:
        """
        Update existing template
        
        Args:
            template_id: Template identifier
            updates: Fields to update
            changed_by: User making the change
            change_description: Description of changes
        
        Returns:
            Updated template
        
        Raises:
            Exception: If template not found
        """
        try:
            # Get current template
            current_template = await self.get_template(template_id)
            
            # Apply updates
            template_ref = self.db.collection('admin').document('prompts')\
                                  .collection('templates').document(template_id)
            
            # Add updated_at timestamp
            updates['updated_at'] = datetime.now(timezone.utc)
            
            template_ref.update(updates)
            
            # Create version snapshot
            updated_template = await self.get_template(template_id)
            await self._create_version(
                template=updated_template,
                change_description=change_description,
                changed_by=changed_by
            )
            
            # Clear cache for this template
            if template_id in self.template_cache:
                del self.template_cache[template_id]
                del self.last_cache_refresh[template_id]
            
            print(f"✅ [PROMPT SERVICE] Updated template: {template_id}")
            
            return updated_template
            
        except Exception as e:
            print(f"❌ [PROMPT SERVICE] Error updating template: {e}")
            raise
    
    async def list_templates(
        self,
        active_only: bool = True,
        tags: Optional[List[str]] = None
    ) -> List[PromptTemplate]:
        """
        List all prompt templates
        
        Args:
            active_only: Only return active templates
            tags: Filter by tags (if provided)
        
        Returns:
            List of templates
        """
        try:
            query = self.db.collection('admin').document('prompts')\
                           .collection('templates')
            
            # Filter by active status
            if active_only:
                query = query.where('is_active', '==', True)
            
            # Get all templates
            docs = query.stream()
            templates = []
            
            for doc in docs:
                try:
                    template = PromptTemplate.from_dict(doc.to_dict())
                    
                    # Filter by tags if specified
                    if tags:
                        if any(tag in template.tags for tag in tags):
                            templates.append(template)
                    else:
                        templates.append(template)
                        
                except Exception as e:
                    print(f"⚠️ [PROMPT SERVICE] Error parsing template {doc.id}: {e}")
            
            return templates
            
        except Exception as e:
            print(f"❌ [PROMPT SERVICE] Error listing templates: {e}")
            raise
    
    async def get_template_versions(self, template_id: str) -> List[PromptVersion]:
        """
        Get version history for a template
        
        Args:
            template_id: Template identifier
        
        Returns:
            List of template versions (newest first)
        """
        try:
            versions_ref = self.db.collection('admin').document('prompts')\
                                  .collection('templates').document(template_id)\
                                  .collection('versions')\
                                  .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                                  .limit(50)  # Limit to 50 most recent versions
            
            versions = []
            for doc in versions_ref.stream():
                try:
                    version = PromptVersion.from_dict(doc.to_dict())
                    versions.append(version)
                except Exception as e:
                    print(f"⚠️ [PROMPT SERVICE] Error parsing version {doc.id}: {e}")
            
            return versions
            
        except Exception as e:
            print(f"❌ [PROMPT SERVICE] Error getting versions: {e}")
            raise
    
    async def _increment_usage_count(self, template_id: str):
        """
        Increment usage count for a template
        
        Args:
            template_id: Template identifier
        """
        try:
            template_ref = self.db.collection('admin').document('prompts')\
                                  .collection('templates').document(template_id)
            
            template_ref.update({
                'usage_count': firestore.Increment(1)
            })
            
            # Update cache if present
            if template_id in self.template_cache:
                self.template_cache[template_id].usage_count += 1
                
        except Exception as e:
            print(f"⚠️ [PROMPT SERVICE] Error incrementing usage count: {e}")
            # Don't raise - usage counting failures shouldn't break rendering
    
    async def _create_version(
        self,
        template: PromptTemplate,
        change_description: str,
        changed_by: Optional[str] = None
    ):
        """
        Create version snapshot of template
        
        Args:
            template: Template to snapshot
            change_description: Description of changes
            changed_by: User making the change
        """
        try:
            version = PromptVersion(
                template_id=template.id,
                version=template.version,
                system_prompt=template.system_prompt,
                user_prompt_template=template.user_prompt_template,
                json_schema=template.json_schema,
                change_description=change_description,
                changed_by=changed_by
            )
            
            version_ref = self.db.collection('admin').document('prompts')\
                                 .collection('templates').document(template.id)\
                                 .collection('versions').document(version.id)
            
            version_ref.set(version.to_dict())
            
        except Exception as e:
            print(f"⚠️ [PROMPT SERVICE] Error creating version: {e}")
            # Don't raise - version creation failures shouldn't break template operations
    
    async def _find_template_by_name(self, name: str) -> Optional[PromptTemplate]:
        """
        Find template by name
        
        Args:
            name: Template name
        
        Returns:
            Template if found, None otherwise
        """
        try:
            query = self.db.collection('admin').document('prompts')\
                           .collection('templates')\
                           .where('name', '==', name)\
                           .limit(1)
            
            docs = list(query.stream())
            if docs:
                return PromptTemplate.from_dict(docs[0].to_dict())
            
            return None
            
        except Exception as e:
            print(f"⚠️ [PROMPT SERVICE] Error finding template by name: {e}")
            return None
    
    async def clear_cache(self):
        """Clear template cache"""
        self.template_cache.clear()
        self.last_cache_refresh.clear()
        print(f"✅ [PROMPT SERVICE] Cache cleared")

