"""
Response Formatter Service - ChatGPT-Style Summary Format
Generates beautiful, intelligent summaries like ChatGPT
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class FormattedResponse(BaseModel):
    """Formatted response with summary and suggestions"""
    summary_text: str
    items: List[Dict[str, Any]]
    net_calories: int
    suggestions: Optional[str] = None


class ResponseFormatter:
    """Formats AI responses in ChatGPT-style summary format"""
    
    def __init__(self):
        pass
    
    def format_response(
        self,
        items: List[Dict[str, Any]],
        user_goal: Optional[str] = None,
        daily_calorie_goal: Optional[int] = None
    ) -> FormattedResponse:
        """
        Format items into ChatGPT-style summary
        
        Args:
            items: List of parsed items (meals, workouts, supplements)
            user_goal: User's fitness goal (lose_weight, gain_muscle, maintain)
            daily_calorie_goal: User's daily calorie target
        
        Returns:
            FormattedResponse with summary text and suggestions
        """
        # Separate items by category
        meals = [item for item in items if item.get('category') in ['meal', 'snack']]
        workouts = [item for item in items if item.get('category') == 'workout']
        supplements = [item for item in items if item.get('category') == 'supplement']
        
        # Calculate totals
        total_calories_consumed = sum(
            item.get('data', {}).get('calories', 0) for item in meals + supplements
        )
        total_calories_burned = sum(
            item.get('data', {}).get('calories_burned', 0) for item in workouts
        )
        total_protein = sum(
            item.get('data', {}).get('protein_g', 0) for item in meals
        )
        total_carbs = sum(
            item.get('data', {}).get('carbs_g', 0) for item in meals
        )
        total_fat = sum(
            item.get('data', {}).get('fat_g', 0) for item in meals
        )
        
        net_calories = total_calories_consumed - total_calories_burned
        
        # Build summary text
        summary_parts = []
        
        # Header
        summary_parts.append("Here's a quick nutrition + activity summary for what you listed today 👇\n")
        
        # Food Intake Section
        if meals or supplements:
            summary_parts.append("🥘 Food Intake\n")
            
            for item in meals + supplements:
                data = item.get('data', {})
                item_name = data.get('item', 'Unknown').title()  # Capitalize properly
                quantity = data.get('quantity', '')
                preparation = data.get('preparation', '')
                meal_type = data.get('meal_type', '').capitalize()
                calories = data.get('calories', 0)
                protein = data.get('protein_g', 0)
                carbs = data.get('carbs_g', 0)
                fat = data.get('fat_g', 0)
                
                # Format item line
                prep_text = f" ({preparation})" if preparation else ""
                quantity_text = f" {quantity}" if quantity else ""
                meal_tag = f" [{meal_type}]" if meal_type and meal_type != 'Unknown' else ""
                
                summary_parts.append(
                    f"• {item_name}{quantity_text}{prep_text}{meal_tag} → "
                    f"~{calories} kcal | {protein}g protein | {fat}g fat | {carbs}g carbs"
                )
            
            summary_parts.append(
                f"\nEstimated Total (Food): "
                f"~{total_calories_consumed} kcal | "
                f"~{total_protein}g protein | "
                f"~{total_fat}g fat | "
                f"~{total_carbs}g carbs\n"
            )
        
        # Exercise Section
        if workouts:
            summary_parts.append("🏃 Exercise\n")
            
            for workout in workouts:
                data = workout.get('data', {})
                activity = data.get('item', 'Unknown').title()
                quantity = data.get('quantity', '')
                calories_burned = data.get('calories_burned', 0)
                calories_range = data.get('calories_burned_range', '')
                intensity = data.get('intensity', '')
                
                range_text = f" ({calories_range})" if calories_range else ""
                intensity_text = f" - {intensity} intensity" if intensity else ""
                
                summary_parts.append(
                    f"• {quantity} {activity} → burns approximately "
                    f"{calories_burned} kcal{range_text}{intensity_text}"
                )
            
            summary_parts.append("")
        
        # Net Estimate Section
        summary_parts.append("⚖️ Net Estimate\n")
        summary_parts.append(f"• Calories consumed: ~{total_calories_consumed} kcal")
        if total_calories_burned > 0:
            summary_parts.append(f"• Calories burned: ~{total_calories_burned} kcal")
        summary_parts.append(
            f"• Net: ≈ {'+' if net_calories >= 0 else ''}{net_calories} kcal "
            f"({'surplus' if net_calories > 0 else 'deficit' if net_calories < 0 else 'maintenance'})"
        )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            net_calories=net_calories,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat,
            user_goal=user_goal,
            daily_calorie_goal=daily_calorie_goal
        )
        
        if suggestions:
            summary_parts.append(f"\n💡 Suggestions:\n{suggestions}")
        
        summary_text = "\n".join(summary_parts)
        
        return FormattedResponse(
            summary_text=summary_text,
            items=items,
            net_calories=net_calories,
            suggestions=suggestions
        )
    
    def _generate_suggestions(
        self,
        net_calories: int,
        total_protein: float,
        total_carbs: float,
        total_fat: float,
        user_goal: Optional[str],
        daily_calorie_goal: Optional[int]
    ) -> Optional[str]:
        """Generate personalized suggestions based on user's data and goals"""
        suggestions = []
        
        # Calorie-based suggestions
        if daily_calorie_goal:
            remaining = daily_calorie_goal - net_calories
            
            if user_goal == "lose_weight":
                if net_calories > daily_calorie_goal:
                    suggestions.append(
                        f"You're {net_calories - daily_calorie_goal} kcal over your goal. "
                        f"Consider a lighter dinner or skip snacks to stay on track for weight loss."
                    )
                elif remaining > 500:
                    suggestions.append(
                        f"Great! You have {remaining} kcal remaining. "
                        f"Focus on protein-rich foods to preserve muscle while losing fat."
                    )
            elif user_goal == "gain_muscle":
                if remaining > 300:
                    suggestions.append(
                        f"You have {remaining} kcal remaining. "
                        f"Add a protein shake or lean meat to support muscle growth."
                    )
        
        # Protein suggestions
        if total_protein < 50:
            suggestions.append(
                "Your protein intake is low. Add eggs, chicken, fish, or legumes to your next meal."
            )
        
        # Macro balance suggestions
        if total_carbs > total_protein * 3:
            suggestions.append(
                "Your carbs are high relative to protein. Balance with more protein sources."
            )
        
        return "\n".join(suggestions) if suggestions else None


# Singleton instance
_formatter = None


def get_response_formatter() -> ResponseFormatter:
    """Get singleton instance of ResponseFormatter"""
    global _formatter
    if _formatter is None:
        _formatter = ResponseFormatter()
    return _formatter

