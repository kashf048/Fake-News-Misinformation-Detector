/**
 * Home Page
 * Main analysis interface
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import FileUpload from '@/components/FileUpload';
import TextInput from '@/components/TextInput';
import Loader from '@/components/Loader';
import ResultCard from '@/components/ResultCard';
import ErrorAlert from '@/components/ErrorAlert';
import { apiService, AnalysisResponse } from '@/services/api';
import { toast } from 'sonner';

export default function Home() {
  const [headline, setHeadline] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!headline.trim()) {
      setError('Please enter a headline to analyze');
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      const response = await apiService.analyze({
        headline: headline.trim(),
        image_url: imageUrl || undefined,
      });

      setResult(response);
      toast.success('Analysis completed successfully!');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze. Please try again.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!result) return;
    
    try {
      // In a real implementation, this would call a backend endpoint to generate PDF
      toast.info('PDF download feature coming soon');
    } catch (err) {
      toast.error('Failed to download PDF');
    }
  };

  const handleNewAnalysis = () => {
    setHeadline('');
    setImageUrl('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Navbar />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="bg-gradient-to-br from-blue-50 to-indigo-50 border-b border-border py-12">
          <div className="container mx-auto px-4">
            <div className="text-center max-w-2xl mx-auto">
              <div className="flex items-center justify-center gap-2 mb-4">
                <Sparkles className="w-6 h-6 text-blue-600" />
                <span className="text-sm font-semibold text-blue-600">AI-Powered Detection</span>
              </div>
              <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
                Detect Misinformation
              </h1>
              <p className="text-lg text-muted-foreground">
                Analyze headlines and images with advanced AI to detect fake news and misinformation
              </p>
            </div>
          </div>
        </section>

        {/* Analysis Section */}
        <section className="py-12">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto">
              {!result ? (
                <div className="space-y-6">
                  {error && (
                    <ErrorAlert
                      message={error}
                      onClose={() => setError(null)}
                      title="Analysis Error"
                    />
                  )}

                  {/* Input Form */}
                  <div className="bg-card border border-border rounded-lg p-6 space-y-6">
                    <TextInput
                      value={headline}
                      onChange={setHeadline}
                      placeholder="Enter a news headline or claim..."
                      label="Headline"
                    />

                    <FileUpload
                      onFileSelect={() => {}}
                      onImageUrlChange={setImageUrl}
                      selectedImage={imageUrl}
                    />

                    <Button
                      onClick={handleAnalyze}
                      disabled={isLoading || !headline.trim()}
                      className="w-full h-12 text-base font-semibold"
                    >
                      {isLoading ? 'Analyzing...' : 'Analyze Now'}
                    </Button>
                  </div>

                  {/* Info Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-secondary rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600 mb-2">🧠</div>
                      <h3 className="font-semibold text-foreground mb-1">AI Analysis</h3>
                      <p className="text-sm text-muted-foreground">
                        Advanced NLP and vision models
                      </p>
                    </div>
                    <div className="bg-secondary rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-green-600 mb-2">✓</div>
                      <h3 className="font-semibold text-foreground mb-1">Fact Checking</h3>
                      <p className="text-sm text-muted-foreground">
                        Integrated fact-check references
                      </p>
                    </div>
                    <div className="bg-secondary rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-purple-600 mb-2">📊</div>
                      <h3 className="font-semibold text-foreground mb-1">Analytics</h3>
                      <p className="text-sm text-muted-foreground">
                        Track analysis history
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  <ResultCard result={result} onDownloadPDF={handleDownloadPDF} />

                  <Button
                    onClick={handleNewAnalysis}
                    variant="outline"
                    className="w-full h-12"
                  >
                    Analyze Another Headline
                  </Button>
                </div>
              )}

              {isLoading && <Loader message="Analyzing your content..." />}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
