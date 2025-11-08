import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';
import '../../providers/auth_provider.dart';

/// Feedback Analytics Screen - User-Facing
/// Phase 1: Analytics Dashboard
/// 
/// Shows user their own feedback summary:
/// - Total feedback given
/// - Satisfaction score
/// - Category breakdown
/// - How we're improving based on their feedback
/// 
/// Risk: VERY LOW (read-only, isolated, new feature)
class FeedbackAnalyticsScreen extends StatefulWidget {
  const FeedbackAnalyticsScreen({Key? key}) : super(key: key);

  @override
  State<FeedbackAnalyticsScreen> createState() => _FeedbackAnalyticsScreenState();
}

class _FeedbackAnalyticsScreenState extends State<FeedbackAnalyticsScreen> {
  Map<String, dynamic>? _analyticsData;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadAnalytics();
  }

  Future<void> _loadAnalytics() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      debugPrint('📊 [ANALYTICS] Loading analytics...');
      
      final api = ApiService(
        context.read<AuthProvider>(),
        onUnauthorized: () => Navigator.of(context).pushReplacementNamed('/login'),
      );
      
      final data = await api.getFeedbackSummary();
      
      setState(() {
        _analyticsData = data;
        _isLoading = false;
      });
      
      debugPrint('✅ [ANALYTICS] Loaded successfully');
    } catch (e) {
      debugPrint('❌ [ANALYTICS] Error: $e');
      
      // User-friendly error message
      String friendlyMessage = 'Unable to load analytics';
      
      if (e.toString().contains('500')) {
        friendlyMessage = 'Server error. Please try again in a moment.';
      } else if (e.toString().contains('timeout') || e.toString().contains('timed out')) {
        friendlyMessage = 'Request timed out. Please check your connection.';
      } else if (e.toString().contains('404')) {
        friendlyMessage = 'Analytics feature not available yet.';
      } else if (e.toString().contains('network') || e.toString().contains('connection')) {
        friendlyMessage = 'Network error. Please check your connection.';
      }
      
      setState(() {
        _errorMessage = friendlyMessage;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Feedback'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAnalytics,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? _buildError()
              : _buildAnalyticsContent(),
    );
  }

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
            const SizedBox(height: 16),
            const Text(
              'Oops! Something went wrong',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Text(
              _errorMessage ?? 'Unable to load analytics',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16, color: Colors.black87),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton.icon(
                onPressed: _loadAnalytics,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry', style: TextStyle(fontSize: 16)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalyticsContent() {
    if (_analyticsData == null) return const SizedBox();

    final summary = _analyticsData!['summary'] as Map<String, dynamic>;
    final categoryBreakdown = _analyticsData!['category_breakdown'] as Map<String, dynamic>;
    final totalFeedback = summary['total_feedback'] as int;

    // Show empty state if no feedback yet
    if (totalFeedback == 0) {
      return _buildEmptyState();
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Overview Metrics
          _buildOverviewMetrics(summary),
          const SizedBox(height: 24),
          
          // How We're Improving Section
          _buildImprovementSection(categoryBreakdown),
          const SizedBox(height: 24),
          
          // Category Breakdown
          if (categoryBreakdown.isNotEmpty) ...[
            _buildCategoryBreakdown(categoryBreakdown),
            const SizedBox(height: 24),
          ],
          
          // Recent Feedback
          _buildRecentFeedback(),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.feedback_outlined, size: 80, color: Colors.grey[400]),
            const SizedBox(height: 24),
            const Text(
              'No Feedback Yet',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Text(
              'Start using the app and give feedback to see your analytics here!',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => Navigator.pop(context),
              icon: const Icon(Icons.chat),
              label: const Text('Go to Chat'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverviewMetrics(Map<String, dynamic> summary) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Your Feedback Summary',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildMetricCard(
                'Total Feedback',
                summary['total_feedback'].toString(),
                Icons.feedback,
                Colors.blue,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildMetricCard(
                'Satisfaction',
                '${summary['satisfaction_score']}%',
                Icons.thumb_up,
                Colors.green,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildMetricCard(
                'Helpful',
                summary['helpful_count'].toString(),
                Icons.check_circle,
                Colors.green,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildMetricCard(
                'Not Helpful',
                summary['not_helpful_count'].toString(),
                Icons.cancel,
                Colors.red,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: const TextStyle(fontSize: 14, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImprovementSection(Map<String, dynamic> categoryBreakdown) {
    // Find categories with low satisfaction
    final lowSatisfactionCategories = categoryBreakdown.entries
        .where((entry) {
          final stats = entry.value as Map<String, dynamic>;
          final satisfaction = stats['satisfaction'] as num;
          return satisfaction < 70;
        })
        .toList();

    if (lowSatisfactionCategories.isEmpty) {
      return Card(
        color: Colors.green[50],
        elevation: 2,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(Icons.celebration, color: Colors.green[700], size: 32),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Great Feedback!',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.green[700],
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'You\'re happy with all features. We\'ll keep improving!',
                      style: TextStyle(color: Colors.green[700]),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
    }

    return Card(
      color: Colors.orange[50],
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.construction, color: Colors.orange[700], size: 28),
                const SizedBox(width: 12),
                Text(
                  'How We\'re Improving',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange[700],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...lowSatisfactionCategories.map((entry) {
              final category = entry.key;
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.arrow_right, color: Colors.orange[700], size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'We noticed you found $category confusing. We\'re working on a fix!',
                        style: TextStyle(color: Colors.orange[700]),
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildCategoryBreakdown(Map<String, dynamic> categoryBreakdown) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Category Performance',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        ...categoryBreakdown.entries.map((entry) {
          final category = entry.key;
          final stats = entry.value as Map<String, dynamic>;
          final satisfaction = stats['satisfaction'] as num;
          final total = stats['total'] as int;
          
          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      category.toUpperCase(),
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    Row(
                      children: [
                        Text(
                          '${satisfaction.toStringAsFixed(0)}%',
                          style: TextStyle(
                            color: satisfaction >= 80 ? Colors.green : 
                                   satisfaction >= 60 ? Colors.orange : Colors.red,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '($total)',
                          style: const TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: satisfaction / 100,
                    minHeight: 8,
                    backgroundColor: Colors.grey[300],
                    color: satisfaction >= 80 ? Colors.green : 
                           satisfaction >= 60 ? Colors.orange : Colors.red,
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ],
    );
  }

  Widget _buildRecentFeedback() {
    final recentFeedback = _analyticsData!['recent_feedback'] as List;
    
    if (recentFeedback.isEmpty) {
      return const SizedBox();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Recent Feedback',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        ...recentFeedback.map((feedback) {
          final rating = feedback['rating'] as String;
          final userInput = feedback['user_input'] as String? ?? 'No input';
          final comment = feedback['comment'] as String? ?? '';
          
          return Card(
            elevation: 1,
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: Icon(
                rating == 'helpful' ? Icons.thumb_up : Icons.thumb_down,
                color: rating == 'helpful' ? Colors.green : Colors.red,
                size: 28,
              ),
              title: Text(
                userInput,
                style: const TextStyle(fontWeight: FontWeight.w500),
              ),
              subtitle: comment.isNotEmpty
                  ? Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Text(comment),
                    )
                  : null,
            ),
          );
        }).toList(),
      ],
    );
  }
}

