import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:async';
import 'dart:math' as math;
import 'package:shared_preferences/shared_preferences.dart';
import '../../services/api_service.dart';
import '../../services/fasting_api_service.dart';
import '../../providers/auth_provider.dart';

/// Stunning Fasting Timer UI
/// Inspired by: Calm, Zero, Headspace
class FastingTab extends StatefulWidget {
  FastingTab({Key? key}) : super(key: key);

  @override
  State<FastingTab> createState() => _FastingTabState();
}

class _FastingTabState extends State<FastingTab> with TickerProviderStateMixin {
  bool _isFasting = false;
  bool _isLoading = false;
  DateTime? _startTime;
  Duration _elapsed = Duration.zero;
  Timer? _timer;
  String _selectedProtocol = '16:8';
  String? _currentSessionId;
  late AnimationController _pulseController;
  late AnimationController _rotationController;
  FastingApiService? _fastingApi;

  final List<Map<String, dynamic>> _protocols = [
    {'name': '16:8', 'hours': 16, 'icon': Icons.wb_twilight, 'color': Color(0xFF6366F1)},
    {'name': '18:6', 'hours': 18, 'icon': Icons.nightlight_round, 'color': Color(0xFF8B5CF6)},
    {'name': '20:4', 'hours': 20, 'icon': Icons.dark_mode, 'color': Color(0xFFA855F7)},
    {'name': 'OMAD', 'hours': 23, 'icon': Icons.star, 'color': Color(0xFFEC4899)},
  ];

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);
    
    _rotationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 60),
    )..repeat();
    
    // Load saved state from local storage first
    _loadLocalState();
    
    // Initialize API service and load current session
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeApiService();
    });
  }
  
  void _initializeApiService() {
    try {
      // Get AuthProvider and create ApiService directly
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final apiService = ApiService(authProvider);
      _fastingApi = FastingApiService(apiService);
      _loadCurrentSession();
    } catch (e) {
      print('⚠️ [FASTING] Could not initialize API service: $e');
      // Continue without API - user can still see UI in local mode
    }
  }
  
  /// Load fasting state from local storage (persists across app restarts)
  Future<void> _loadLocalState() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final startTimeStr = prefs.getString('fasting_start_time');
      final protocol = prefs.getString('fasting_protocol');
      
      if (startTimeStr != null && mounted) {
        final startTime = DateTime.parse(startTimeStr);
        
        setState(() {
          _isFasting = true;
          _startTime = startTime;
          _selectedProtocol = protocol ?? '16:8';
          _elapsed = DateTime.now().difference(startTime);
        });
        
        _startLocalTimer();
        
        print('✅ [FASTING] Resumed from local storage: ${_formatDuration(_elapsed)}');
      }
    } catch (e) {
      print('⚠️ [FASTING] Error loading local state: $e');
    }
  }
  
  /// Save fasting state to local storage
  Future<void> _saveLocalState() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      if (_isFasting && _startTime != null) {
        await prefs.setString('fasting_start_time', _startTime!.toIso8601String());
        await prefs.setString('fasting_protocol', _selectedProtocol);
      } else {
        await prefs.remove('fasting_start_time');
        await prefs.remove('fasting_protocol');
      }
    } catch (e) {
      print('⚠️ [FASTING] Error saving local state: $e');
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _pulseController.dispose();
    _rotationController.dispose();
    super.dispose();
  }

  /// Load current fasting session from backend
  Future<void> _loadCurrentSession() async {
    if (_fastingApi == null) return;
    
    setState(() => _isLoading = true);
    
    try {
      final session = await _fastingApi!.getCurrentSession();
      
      if (session != null && mounted) {
        final startTime = DateTime.parse(session['start_time']);
        final protocol = session['protocol'] ?? '16:8';
        
        setState(() {
          _isFasting = true;
          _startTime = startTime;
          _currentSessionId = session['id'];
          _selectedProtocol = protocol;
          _elapsed = DateTime.now().difference(startTime);
        });
        
        // Start local timer
        _startLocalTimer();
        
        print('✅ Loaded active fasting session: $_currentSessionId');
      }
    } catch (e) {
      print('❌ Error loading session: $e');
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  /// Start local timer (updates UI every second)
  void _startLocalTimer() {
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_startTime != null && mounted) {
        setState(() {
          _elapsed = DateTime.now().difference(_startTime!);
        });
      }
    });
  }

  /// Start fasting session (API call)
  Future<void> _startFasting() async {
    if (_isLoading) return;
    
      // Check if API is initialized - if not, use local-only mode
      if (_fastingApi == null) {
        // LOCAL MODE: Just start the timer without backend
        setState(() {
          _isFasting = true;
          _startTime = DateTime.now();
          _elapsed = Duration.zero;
        });
        
        // Save to local storage so it persists across app restarts
        await _saveLocalState();
        
        _startLocalTimer();
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('🎉 Started $_selectedProtocol fast! (Local mode)'),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 2),
            ),
          );
        }
        return;
      }
    
    setState(() => _isLoading = true);
    
    try {
      final protocol = _protocols.firstWhere((p) => p['name'] == _selectedProtocol);
      final targetHours = protocol['hours'] as int;
      
      final session = await _fastingApi!.startFasting(
        targetDurationHours: targetHours,
        protocol: _selectedProtocol,
        notes: 'Started from app',
      );
      
      if (mounted) {
        final startTime = DateTime.parse(session['start_time']);
        
        setState(() {
          _isFasting = true;
          _startTime = startTime;
          _currentSessionId = session['id'];
          _elapsed = Duration.zero;
        });
        
        _startLocalTimer();
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('🎉 Started $_selectedProtocol fast!'),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Failed to start fast: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  /// Stop fasting session (API call)
  Future<void> _stopFasting() async {
    if (_isLoading) return;
    
    // Show confirmation dialog
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('End Fast?'),
        content: Text(
          'Are you sure you want to end your fast?\n\n'
          'Duration: ${_formatDuration(_elapsed)}\n'
          'Stage: $_currentStage',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('End Fast'),
          ),
        ],
      ),
    );
    
    // User cancelled
    if (confirmed != true) return;
    
      // If no API, just stop locally
      if (_fastingApi == null || _currentSessionId == null) {
        final completedDuration = _elapsed;
        
        setState(() {
          _isFasting = false;
          _startTime = null;
          _currentSessionId = null;
          _elapsed = Duration.zero;
        });
        
        // Clear local storage
        await _saveLocalState();
        
        _timer?.cancel();
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('✅ Fast completed! Duration: ${_formatDuration(completedDuration)} (Local mode)'),
              backgroundColor: Colors.blue,
              duration: const Duration(seconds: 3),
            ),
          );
        }
        return;
      }
    
    setState(() => _isLoading = true);
    
    try {
      await _fastingApi!.endFasting(
        sessionId: _currentSessionId!,
        breakReason: 'planned',
        energyLevel: 4,
        hungerLevel: 3,
        notes: 'Ended from app',
      );
      
      if (mounted) {
        setState(() {
          _isFasting = false;
          _startTime = null;
          _currentSessionId = null;
          _elapsed = Duration.zero;
        });
        
        _timer?.cancel();
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Fast completed! Duration: ${_formatDuration(_elapsed)}'),
            backgroundColor: Colors.blue,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Failed to end fast: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  double get _progress {
    if (!_isFasting) return 0.0;
    final protocol = _protocols.firstWhere((p) => p['name'] == _selectedProtocol);
    final targetHours = protocol['hours'] as int;
    final targetSeconds = targetHours * 3600;
    return (_elapsed.inSeconds / targetSeconds).clamp(0.0, 1.0);
  }

  String get _currentStage {
    final hours = _elapsed.inHours;
    if (hours < 4) return 'Anabolic State';
    if (hours < 16) return 'Catabolic State';
    if (hours < 24) return 'Autophagy (Light)';
    if (hours < 48) return 'Autophagy (Deep)';
    return 'Growth Hormone Peak';
  }

  Color get _stageColor {
    final hours = _elapsed.inHours;
    if (hours < 4) return const Color(0xFF10B981);
    if (hours < 16) return const Color(0xFF3B82F6);
    if (hours < 24) return const Color(0xFF8B5CF6);
    if (hours < 48) return const Color(0xFFA855F7);
    return const Color(0xFFEC4899);
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            // Protocol Selector
            if (!_isFasting) _buildProtocolSelector(),
            
            const SizedBox(height: 32),
            
            // Circular Timer
            _buildCircularTimer(),
            
            const SizedBox(height: 40),
            
            // Start/Stop Button
            _buildActionButton(),
            
            const SizedBox(height: 32),
            
            // Stats Cards
            if (_isFasting) _buildStatsCards(),
            
            const SizedBox(height: 24),
            
            // Benefits Section
            _buildBenefitsSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildProtocolSelector() {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(16, 16, 16, 12),
            child: Text(
              'Choose Your Protocol',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1F2937),
              ),
            ),
          ),
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            padding: const EdgeInsets.all(8),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 1.5,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
            ),
            itemCount: _protocols.length,
            itemBuilder: (context, index) {
              final protocol = _protocols[index];
              final isSelected = _selectedProtocol == protocol['name'];
              
              return GestureDetector(
                onTap: () {
                  setState(() {
                    _selectedProtocol = protocol['name'];
                  });
                },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  curve: Curves.easeInOut,
                  decoration: BoxDecoration(
                    gradient: isSelected
                        ? LinearGradient(
                            colors: [
                              protocol['color'],
                              protocol['color'].withOpacity(0.7),
                            ],
                          )
                        : null,
                    color: isSelected ? null : const Color(0xFFF3F4F6),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isSelected
                          ? protocol['color']
                          : Colors.transparent,
                      width: 2,
                    ),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        protocol['icon'],
                        color: isSelected ? Colors.white : protocol['color'],
                        size: 32,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        protocol['name'],
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: isSelected ? Colors.white : const Color(0xFF1F2937),
                        ),
                      ),
                      Text(
                        '${protocol['hours']}h fast',
                        style: TextStyle(
                          fontSize: 12,
                          color: isSelected ? Colors.white70 : const Color(0xFF6B7280),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildCircularTimer() {
    return Container(
      width: 280,
      height: 280,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: _isFasting
                ? _stageColor.withOpacity(0.3)
                : Colors.black.withOpacity(0.1),
            blurRadius: 40,
            spreadRadius: 5,
          ),
        ],
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Animated Background Circles
          if (_isFasting)
            AnimatedBuilder(
              animation: _pulseController,
              builder: (context, child) {
                return Container(
                  width: 280 + (_pulseController.value * 20),
                  height: 280 + (_pulseController.value * 20),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _stageColor.withOpacity(0.1 - _pulseController.value * 0.1),
                  ),
                );
              },
            ),
          
          // Progress Ring
          CustomPaint(
            size: const Size(240, 240),
            painter: _CircularProgressPainter(
              progress: _progress,
              color: _isFasting ? _stageColor : const Color(0xFFE5E7EB),
              strokeWidth: 16,
            ),
          ),
          
          // Center Content
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (_isFasting) ...[
                Text(
                  _currentStage,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: _stageColor,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 12),
              ],
              Text(
                _formatDuration(_elapsed),
                style: const TextStyle(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                  letterSpacing: -1,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                _isFasting ? 'Fasting Time' : 'Ready to Start',
                style: const TextStyle(
                  fontSize: 16,
                  color: Color(0xFF6B7280),
                  fontWeight: FontWeight.w500,
                ),
              ),
              if (_isFasting) ...[
                const SizedBox(height: 16),
                Text(
                  '${(_progress * 100).toInt()}% Complete',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: _stageColor,
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton() {
    return GestureDetector(
      onTap: _isLoading ? null : (_isFasting ? _stopFasting : _startFasting),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        width: double.infinity,
        height: 64,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: _isLoading
                ? [Colors.grey, Colors.grey.shade600]
                : _isFasting
                    ? [const Color(0xFFEF4444), const Color(0xFFDC2626)]
                    : [const Color(0xFF10B981), const Color(0xFF059669)],
          ),
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: (_isFasting ? const Color(0xFFEF4444) : const Color(0xFF10B981))
                  .withOpacity(0.4),
              blurRadius: 20,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (_isLoading)
              const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  color: Colors.white,
                  strokeWidth: 2,
                ),
              )
            else
              Icon(
                _isFasting ? Icons.stop_rounded : Icons.play_arrow_rounded,
                color: Colors.white,
                size: 28,
              ),
            const SizedBox(width: 12),
            Text(
              _isLoading
                  ? 'Loading...'
                  : _isFasting
                      ? 'End Fast'
                      : 'Start Fasting',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsCards() {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'Target',
            _selectedProtocol,
            Icons.flag_rounded,
            const Color(0xFF3B82F6),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildStatCard(
            'Remaining',
            _formatDuration(_getRemainingTime()),
            Icons.timer_outlined,
            const Color(0xFF8B5CF6),
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              color: Color(0xFF6B7280),
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBenefitsSection() {
    final benefits = [
      {'icon': Icons.favorite, 'title': 'Heart Health', 'color': Color(0xFFEF4444)},
      {'icon': Icons.psychology, 'title': 'Mental Clarity', 'color': Color(0xFF8B5CF6)},
      {'icon': Icons.fitness_center, 'title': 'Fat Burning', 'color': Color(0xFFF59E0B)},
      {'icon': Icons.auto_awesome, 'title': 'Autophagy', 'color': Color(0xFF10B981)},
    ];

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Benefits of Fasting',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
            ),
          ),
          const SizedBox(height: 20),
          ...benefits.map((benefit) => Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: (benefit['color'] as Color).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(
                        benefit['icon'] as IconData,
                        color: benefit['color'] as Color,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Text(
                      benefit['title'] as String,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF374151),
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }

  String _formatDuration(Duration duration) {
    final hours = duration.inHours.toString().padLeft(2, '0');
    final minutes = (duration.inMinutes % 60).toString().padLeft(2, '0');
    final seconds = (duration.inSeconds % 60).toString().padLeft(2, '0');
    return '$hours:$minutes:$seconds';
  }

  Duration _getRemainingTime() {
    if (!_isFasting) return Duration.zero;
    final protocol = _protocols.firstWhere((p) => p['name'] == _selectedProtocol);
    final targetHours = protocol['hours'] as int;
    final target = Duration(hours: targetHours);
    final remaining = target - _elapsed;
    return remaining.isNegative ? Duration.zero : remaining;
  }
}

/// Custom Painter for Circular Progress
class _CircularProgressPainter extends CustomPainter {
  final double progress;
  final Color color;
  final double strokeWidth;

  _CircularProgressPainter({
    required this.progress,
    required this.color,
    required this.strokeWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width - strokeWidth) / 2;

    // Background circle
    final backgroundPaint = Paint()
      ..color = const Color(0xFFF3F4F6)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, backgroundPaint);

    // Progress arc
    if (progress > 0) {
      final progressPaint = Paint()
        ..shader = LinearGradient(
          colors: [color, color.withOpacity(0.6)],
        ).createShader(Rect.fromCircle(center: center, radius: radius))
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth
        ..strokeCap = StrokeCap.round;

      final sweepAngle = 2 * math.pi * progress;
      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        -math.pi / 2,
        sweepAngle,
        false,
        progressPaint,
      );
    }
  }

  @override
  bool shouldRepaint(_CircularProgressPainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.color != color;
  }
}

