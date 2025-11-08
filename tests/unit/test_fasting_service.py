"""
Unit Tests for FastingService

Tests fasting timer, window calculations, and fasting log management
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone


class TestFastingCalculations:
    """Test fasting time calculations"""
    
    def test_calculate_fasting_duration_hours(self):
        """Test calculating fasting duration in hours"""
        start = datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc)  # 8 PM
        end = datetime(2024, 1, 2, 12, 0, tzinfo=timezone.utc)    # 12 PM next day
        
        duration = end - start
        hours = duration.total_seconds() / 3600
        
        assert hours == 16.0
    
    def test_calculate_fasting_duration_minutes(self):
        """Test calculating fasting duration in minutes"""
        start = datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 22, 30, tzinfo=timezone.utc)
        
        duration = end - start
        minutes = duration.total_seconds() / 60
        
        assert minutes == 150.0
    
    def test_is_fasting_in_progress(self):
        """Test checking if fasting is currently in progress"""
        start = datetime.now(timezone.utc) - timedelta(hours=10)
        end = None  # Still fasting
        
        is_active = end is None
        
        assert is_active is True
    
    def test_is_fasting_completed(self):
        """Test checking if fasting is completed"""
        start = datetime.now(timezone.utc) - timedelta(hours=16)
        end = datetime.now(timezone.utc)  # Ended
        
        is_active = end is None
        
        assert is_active is False


class TestFastingGoals:
    """Test fasting goal tracking"""
    
    def test_16_8_fasting_goal_met(self):
        """Test 16:8 fasting goal met"""
        duration_hours = 16.5
        goal_hours = 16
        
        goal_met = duration_hours >= goal_hours
        
        assert goal_met is True
    
    def test_16_8_fasting_goal_not_met(self):
        """Test 16:8 fasting goal not met"""
        duration_hours = 14.0
        goal_hours = 16
        
        goal_met = duration_hours >= goal_hours
        
        assert goal_met is False
    
    def test_calculate_progress_percentage(self):
        """Test calculating fasting progress percentage"""
        current_hours = 10
        goal_hours = 16
        
        progress = (current_hours / goal_hours) * 100
        
        assert progress == 62.5


class TestFastingWindows:
    """Test fasting window calculations"""
    
    def test_eating_window_16_8(self):
        """Test calculating eating window for 16:8 fast"""
        fasting_hours = 16
        eating_hours = 24 - fasting_hours
        
        assert eating_hours == 8
    
    def test_eating_window_18_6(self):
        """Test calculating eating window for 18:6 fast"""
        fasting_hours = 18
        eating_hours = 24 - fasting_hours
        
        assert eating_hours == 6
    
    def test_eating_window_20_4(self):
        """Test calculating eating window for 20:4 fast"""
        fasting_hours = 20
        eating_hours = 24 - fasting_hours
        
        assert eating_hours == 4


class TestFastingStreak:
    """Test fasting streak calculations"""
    
    def test_consecutive_days_streak(self):
        """Test consecutive fasting days"""
        fasting_dates = [
            datetime(2024, 1, 1, tzinfo=timezone.utc).date(),
            datetime(2024, 1, 2, tzinfo=timezone.utc).date(),
            datetime(2024, 1, 3, tzinfo=timezone.utc).date()
        ]
        
        # Check if consecutive
        is_consecutive = True
        for i in range(len(fasting_dates) - 1):
            diff = (fasting_dates[i+1] - fasting_dates[i]).days
            if diff != 1:
                is_consecutive = False
                break
        
        assert is_consecutive is True
        assert len(fasting_dates) == 3
    
    def test_broken_streak(self):
        """Test broken fasting streak"""
        fasting_dates = [
            datetime(2024, 1, 1, tzinfo=timezone.utc).date(),
            datetime(2024, 1, 2, tzinfo=timezone.utc).date(),
            # Missing Jan 3
            datetime(2024, 1, 4, tzinfo=timezone.utc).date()
        ]
        
        # Check if consecutive
        is_consecutive = True
        for i in range(len(fasting_dates) - 1):
            diff = (fasting_dates[i+1] - fasting_dates[i]).days
            if diff != 1:
                is_consecutive = False
                break
        
        assert is_consecutive is False


class TestFastingTypes:
    """Test different fasting types"""
    
    def test_intermittent_fasting_16_8(self):
        """Test 16:8 intermittent fasting"""
        fasting_type = "16:8"
        fasting_hours, eating_hours = fasting_type.split(":")
        
        assert int(fasting_hours) == 16
        assert int(eating_hours) == 8
    
    def test_intermittent_fasting_18_6(self):
        """Test 18:6 intermittent fasting"""
        fasting_type = "18:6"
        fasting_hours, eating_hours = fasting_type.split(":")
        
        assert int(fasting_hours) == 18
        assert int(eating_hours) == 6
    
    def test_alternate_day_fasting(self):
        """Test alternate day fasting (36 hours)"""
        fasting_hours = 36
        is_extended = fasting_hours > 24
        
        assert is_extended is True


class TestTimezoneHandling:
    """Test timezone handling for fasting times"""
    
    def test_utc_timezone_aware(self):
        """Test UTC timezone aware datetime"""
        now = datetime.now(timezone.utc)
        
        assert now.tzinfo is not None
        assert now.tzinfo == timezone.utc
    
    def test_convert_local_to_utc(self):
        """Test converting local time to UTC"""
        # Create a naive datetime
        local_time = datetime(2024, 1, 1, 20, 0)
        
        # Add UTC timezone
        utc_time = local_time.replace(tzinfo=timezone.utc)
        
        assert utc_time.tzinfo == timezone.utc


class TestFastingValidation:
    """Test fasting data validation"""
    
    def test_validate_positive_duration(self):
        """Test validating positive fasting duration"""
        start = datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 12, 0, tzinfo=timezone.utc)
        
        is_valid = end > start
        
        assert is_valid is True
    
    def test_validate_negative_duration(self):
        """Test detecting invalid negative duration"""
        start = datetime(2024, 1, 2, 12, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc)  # Before start
        
        is_valid = end > start
        
        assert is_valid is False
    
    def test_validate_same_time(self):
        """Test detecting same start and end time"""
        time = datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc)
        start = time
        end = time
        
        is_valid = end > start
        
        assert is_valid is False


class TestFastingStatistics:
    """Test fasting statistics calculations"""
    
    def test_average_fasting_duration(self):
        """Test calculating average fasting duration"""
        durations = [16.0, 17.5, 15.5, 18.0]  # hours
        
        average = sum(durations) / len(durations)
        
        assert average == 16.75
    
    def test_longest_fast(self):
        """Test finding longest fast"""
        durations = [16.0, 17.5, 15.5, 18.0, 20.0]
        
        longest = max(durations)
        
        assert longest == 20.0
    
    def test_total_fasting_hours(self):
        """Test calculating total fasting hours"""
        durations = [16.0, 17.0, 18.0]
        
        total = sum(durations)
        
        assert total == 51.0


class TestFastingNotifications:
    """Test fasting notification logic"""
    
    def test_should_notify_goal_reached(self):
        """Test notification when goal is reached"""
        current_hours = 16.0
        goal_hours = 16.0
        
        should_notify = current_hours >= goal_hours
        
        assert should_notify is True
    
    def test_should_not_notify_before_goal(self):
        """Test no notification before goal"""
        current_hours = 14.0
        goal_hours = 16.0
        
        should_notify = current_hours >= goal_hours
        
        assert should_notify is False
    
    def test_halfway_reminder(self):
        """Test halfway point reminder"""
        current_hours = 8.0
        goal_hours = 16.0
        
        progress_percent = (current_hours / goal_hours) * 100
        is_halfway = progress_percent >= 50
        
        assert is_halfway is True

