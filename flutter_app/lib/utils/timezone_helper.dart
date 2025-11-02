import 'package:flutter/foundation.dart';
import 'package:flutter_timezone/flutter_timezone.dart';

/// Universal timezone detection that works on Web, iOS, and Android
class TimezoneHelper {
  /// Get user's timezone in IANA format (e.g., "Asia/Kolkata")
  static Future<String> getLocalTimezone() async {
    debugPrint('🔍 TimezoneHelper.getLocalTimezone() called');
    debugPrint('🔍 Platform: ${kIsWeb ? "WEB" : "MOBILE"}');
    
    try {
      if (kIsWeb) {
        // Web: Infer from UTC offset (JavaScript Intl API not easily accessible in Flutter web)
        final offset = DateTime.now().timeZoneOffset;
        debugPrint('🔍 UTC Offset detected: $offset');
        final timezone = _timezoneFromOffset(offset);
        debugPrint('✅ Web timezone (from offset): $timezone (offset: $offset)');
        return timezone;
      } else {
        // Mobile (iOS/Android): Use flutter_timezone package
        debugPrint('🔍 Attempting flutter_timezone...');
        try {
          final timezone = await FlutterTimezone.getLocalTimezone();
          debugPrint('✅ Mobile timezone detected: $timezone');
          return timezone;
        } catch (e) {
          debugPrint('⚠️  flutter_timezone failed: $e, using offset');
          return _timezoneFromOffset(DateTime.now().timeZoneOffset);
        }
      }
    } catch (e) {
      debugPrint('❌ Timezone detection FAILED: $e, returning UTC');
      return 'UTC';
    }
  }

  /// Map UTC offset to common IANA timezones
  /// This is a fallback method when proper timezone detection fails
  static String _timezoneFromOffset(Duration offset) {
    final hours = offset.inHours;
    final minutes = offset.inMinutes.remainder(60);
    
    // Format: "+5:30" or "-8:00"
    final offsetKey = '${hours >= 0 ? '+' : ''}$hours:${minutes.abs().toString().padLeft(2, '0')}';
    
    debugPrint('🌍 Mapping offset $offsetKey to timezone');
    
    // Common timezone mappings based on UTC offset
    final offsetMap = {
      // Asia
      '+5:30': 'Asia/Kolkata',      // IST (India)
      '+5:45': 'Asia/Kathmandu',     // NPT (Nepal)
      '+6:00': 'Asia/Dhaka',         // BST (Bangladesh)
      '+6:30': 'Asia/Yangon',        // MMT (Myanmar)
      '+7:00': 'Asia/Bangkok',       // ICT (Thailand, Vietnam)
      '+8:00': 'Asia/Singapore',     // SGT (Singapore, Malaysia, Philippines)
      '+9:00': 'Asia/Tokyo',         // JST (Japan, Korea)
      '+9:30': 'Australia/Darwin',   // ACST (Australia Central)
      '+10:00': 'Australia/Sydney',  // AEST (Australia East)
      '+11:00': 'Pacific/Noumea',    // NCT (New Caledonia)
      '+12:00': 'Pacific/Auckland',  // NZST (New Zealand)
      
      // Middle East
      '+3:00': 'Europe/Moscow',      // MSK (Russia, East Africa)
      '+3:30': 'Asia/Tehran',        // IRST (Iran)
      '+4:00': 'Asia/Dubai',         // GST (UAE, Oman)
      '+4:30': 'Asia/Kabul',         // AFT (Afghanistan)
      
      // Europe
      '+0:00': 'Europe/London',      // GMT (UK, Portugal)
      '+1:00': 'Europe/Paris',       // CET (Central Europe)
      '+2:00': 'Europe/Athens',      // EET (Eastern Europe)
      
      // Americas
      '-3:00': 'America/Sao_Paulo',  // BRT (Brazil)
      '-4:00': 'America/New_York',   // EDT (US Eastern)
      '-5:00': 'America/Chicago',    // CST (US Central)
      '-6:00': 'America/Denver',     // MST (US Mountain)
      '-7:00': 'America/Los_Angeles', // PST (US Pacific)
      '-8:00': 'America/Anchorage',  // AKST (Alaska)
      '-10:00': 'Pacific/Honolulu',  // HST (Hawaii)
    };
    
    final result = offsetMap[offsetKey] ?? 'UTC';
    debugPrint('🌍 Mapped to: $result');
    return result;
  }
}
