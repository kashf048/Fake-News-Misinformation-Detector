/**
 * Analytics Page
 * Dashboard with analytics data
 */

import { useState, useEffect } from 'react';
import { Loader2, BarChart3, TrendingUp } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import ErrorAlert from '@/components/ErrorAlert';
import { apiService, AnalyticsResponse } from '@/services/api';
import { toast } from 'sonner';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function Analytics() {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.getAnalytics();
      setAnalytics(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load analytics';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col min-h-screen bg-background">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </main>
        <Footer />
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="flex flex-col min-h-screen bg-background">
        <Navbar />
        <main className="flex-1 container mx-auto px-4 py-12">
          {error && <ErrorAlert message={error} onClose={() => setError(null)} />}
        </main>
        <Footer />
      </div>
    );
  }

  const predictionData = [
    { name: 'Fake', value: analytics.fake_count, fill: '#dc2626' },
    { name: 'Real', value: analytics.real_count, fill: '#16a34a' },
    { name: 'Misleading', value: analytics.misleading_count, fill: '#ea580c' },
  ];

  const trendData = Object.entries(analytics.predictions_by_date).map(([date, count]) => ({
    date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    count,
  }));

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Navbar />

      <main className="flex-1">
        {/* Header Section */}
        <section className="bg-gradient-to-br from-blue-50 to-indigo-50 border-b border-border py-12">
          <div className="container mx-auto px-4">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-8 h-8 text-blue-600" />
              <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                Analytics Dashboard
              </h1>
            </div>
            <p className="text-lg text-muted-foreground">
              Insights and statistics from your analysis history
            </p>
          </div>
        </section>

        {/* Content Section */}
        <section className="py-12">
          <div className="container mx-auto px-4">
            {error && (
              <div className="mb-6">
                <ErrorAlert
                  message={error}
                  onClose={() => setError(null)}
                />
              </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
              {/* Total Analyses */}
              <div className="bg-card border border-border rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-muted-foreground">Total Analyses</p>
                  <div className="text-2xl">📊</div>
                </div>
                <p className="text-3xl font-bold text-foreground">
                  {analytics.total_analyses}
                </p>
              </div>

              {/* Fake Count */}
              <div className="bg-card border border-border rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-muted-foreground">Fake News</p>
                  <div className="text-2xl">🚫</div>
                </div>
                <p className="text-3xl font-bold text-red-600">
                  {analytics.fake_count}
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  {analytics.total_analyses > 0 
                    ? `${((analytics.fake_count / analytics.total_analyses) * 100).toFixed(1)}%`
                    : '0%'
                  }
                </p>
              </div>

              {/* Real Count */}
              <div className="bg-card border border-border rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-muted-foreground">Real News</p>
                  <div className="text-2xl">✓</div>
                </div>
                <p className="text-3xl font-bold text-green-600">
                  {analytics.real_count}
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  {analytics.total_analyses > 0 
                    ? `${((analytics.real_count / analytics.total_analyses) * 100).toFixed(1)}%`
                    : '0%'
                  }
                </p>
              </div>

              {/* Misleading Count */}
              <div className="bg-card border border-border rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-muted-foreground">Misleading</p>
                  <div className="text-2xl">⚠️</div>
                </div>
                <p className="text-3xl font-bold text-yellow-600">
                  {analytics.misleading_count}
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  {analytics.total_analyses > 0 
                    ? `${((analytics.misleading_count / analytics.total_analyses) * 100).toFixed(1)}%`
                    : '0%'
                  }
                </p>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
              {/* Pie Chart */}
              <div className="bg-card border border-border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4">
                  Prediction Distribution
                </h3>
                {analytics.total_analyses > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={predictionData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: ${value}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {predictionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    No data available
                  </div>
                )}
              </div>

              {/* Bar Chart */}
              <div className="bg-card border border-border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                  <TrendingUp size={20} />
                  Analyses Over Time
                </h3>
                {trendData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#3b82f6" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    No data available
                  </div>
                )}
              </div>
            </div>

            {/* Additional Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Average Confidence */}
              <div className="bg-card border border-border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4">
                  Average Confidence
                </h3>
                <div className="flex items-end gap-4">
                  <div className="text-5xl font-bold text-blue-600">
                    {(analytics.average_confidence * 100).toFixed(1)}%
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">
                    Average confidence score across all analyses
                  </p>
                </div>
              </div>

              {/* Top Headlines */}
              <div className="bg-card border border-border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4">
                  Recent Headlines
                </h3>
                <div className="space-y-2">
                  {analytics.top_headlines.length > 0 ? (
                    analytics.top_headlines.map((headline, idx) => (
                      <div key={idx} className="text-sm text-foreground truncate">
                        {idx + 1}. {headline}
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">No headlines yet</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
