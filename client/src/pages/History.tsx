/**
 * History Page
 * View analysis history
 */

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Loader2, Filter } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import HistoryCard from '@/components/HistoryCard';
import ErrorAlert from '@/components/ErrorAlert';
import ResultCard from '@/components/ResultCard';
import { apiService, AnalysisResponse } from '@/services/api';
import { toast } from 'sonner';

export default function History() {
  const [analyses, setAnalyses] = useState<AnalysisResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [limit] = useState(10);
  const [filter, setFilter] = useState<string | undefined>(undefined);
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResponse | null>(null);

  const loadHistory = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.getHistory(page, limit, filter);
      setAnalyses(response.items);
      setTotal(response.total);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load history';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [page, filter]);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this analysis?')) {
      return;
    }

    try {
      await apiService.deleteAnalysis(id);
      setAnalyses(analyses.filter(a => a._id !== id));
      setTotal(total - 1);
      toast.success('Analysis deleted successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete analysis';
      toast.error(errorMessage);
    }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Navbar />

      <main className="flex-1">
        {/* Header Section */}
        <section className="bg-gradient-to-br from-blue-50 to-indigo-50 border-b border-border py-12">
          <div className="container mx-auto px-4">
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Analysis History
            </h1>
            <p className="text-lg text-muted-foreground">
              View all your previous analyses and results
            </p>
          </div>
        </section>

        {/* Content Section */}
        <section className="py-12">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Sidebar */}
              <div className="lg:col-span-1">
                <div className="bg-card border border-border rounded-lg p-6 sticky top-24 space-y-4">
                  <div className="flex items-center gap-2 mb-4">
                    <Filter size={20} />
                    <h3 className="font-semibold text-foreground">Filters</h3>
                  </div>

                  <div className="space-y-2">
                    <Button
                      variant={filter === undefined ? 'default' : 'outline'}
                      onClick={() => {
                        setFilter(undefined);
                        setPage(1);
                      }}
                      className="w-full justify-start"
                    >
                      All Results
                    </Button>
                    <Button
                      variant={filter === 'Fake' ? 'default' : 'outline'}
                      onClick={() => {
                        setFilter('Fake');
                        setPage(1);
                      }}
                      className="w-full justify-start"
                    >
                      🚫 Fake
                    </Button>
                    <Button
                      variant={filter === 'Real' ? 'default' : 'outline'}
                      onClick={() => {
                        setFilter('Real');
                        setPage(1);
                      }}
                      className="w-full justify-start"
                    >
                      ✓ Real
                    </Button>
                    <Button
                      variant={filter === 'Misleading' ? 'default' : 'outline'}
                      onClick={() => {
                        setFilter('Misleading');
                        setPage(1);
                      }}
                      className="w-full justify-start"
                    >
                      ⚠️ Misleading
                    </Button>
                  </div>

                  {/* Stats */}
                  <div className="border-t border-border pt-4 mt-4">
                    <p className="text-sm text-muted-foreground mb-2">Total Analyses</p>
                    <p className="text-3xl font-bold text-blue-600">{total}</p>
                  </div>
                </div>
              </div>

              {/* Main Content */}
              <div className="lg:col-span-2">
                {selectedAnalysis ? (
                  <div className="space-y-4">
                    <Button
                      variant="outline"
                      onClick={() => setSelectedAnalysis(null)}
                    >
                      ← Back to List
                    </Button>
                    <ResultCard result={selectedAnalysis} />
                  </div>
                ) : (
                  <div className="space-y-4">
                    {error && (
                      <ErrorAlert
                        message={error}
                        onClose={() => setError(null)}
                      />
                    )}

                    {isLoading ? (
                      <div className="flex items-center justify-center py-12">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                      </div>
                    ) : analyses.length > 0 ? (
                      <>
                        <div className="space-y-3">
                          {analyses.map(analysis => (
                            <HistoryCard
                              key={analysis._id}
                              analysis={analysis}
                              onDelete={handleDelete}
                              onClick={() => setSelectedAnalysis(analysis)}
                            />
                          ))}
                        </div>

                        {/* Pagination */}
                        {totalPages > 1 && (
                          <div className="flex items-center justify-between mt-6 pt-6 border-t border-border">
                            <Button
                              variant="outline"
                              onClick={() => setPage(Math.max(1, page - 1))}
                              disabled={page === 1}
                            >
                              Previous
                            </Button>
                            <span className="text-sm text-muted-foreground">
                              Page {page} of {totalPages}
                            </span>
                            <Button
                              variant="outline"
                              onClick={() => setPage(Math.min(totalPages, page + 1))}
                              disabled={page === totalPages}
                            >
                              Next
                            </Button>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="text-center py-12">
                        <p className="text-lg text-muted-foreground mb-4">
                          No analyses found
                        </p>
                        <Button onClick={() => window.location.href = '/'}>
                          Start Analyzing
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
