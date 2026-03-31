/**
 * ResultCard Component
 */

import { AlertCircle, CheckCircle, AlertTriangle, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import ConfidenceBar from './ConfidenceBar';
import { AnalysisResponse } from '@/services/api';

interface ResultCardProps {
  result: AnalysisResponse;
  onDownloadPDF?: () => void;
}

export default function ResultCard({ result, onDownloadPDF }: ResultCardProps) {
  const getPredictionIcon = () => {
    switch (result.prediction) {
      case 'Fake':
        return <AlertCircle className="w-8 h-8 text-red-500" />;
      case 'Real':
        return <CheckCircle className="w-8 h-8 text-green-500" />;
      case 'Misleading':
        return <AlertTriangle className="w-8 h-8 text-yellow-500" />;
      default:
        return null;
    }
  };

  const getPredictionColor = () => {
    switch (result.prediction) {
      case 'Fake':
        return 'border-red-200 bg-red-50';
      case 'Real':
        return 'border-green-200 bg-green-50';
      case 'Misleading':
        return 'border-yellow-200 bg-yellow-50';
      default:
        return 'border-border';
    }
  };

  const getPredictionTextColor = () => {
    switch (result.prediction) {
      case 'Fake':
        return 'text-red-700';
      case 'Real':
        return 'text-green-700';
      case 'Misleading':
        return 'text-yellow-700';
      default:
        return 'text-foreground';
    }
  };

  const getRatingColor = (rating: string) => {
    const lowerRating = rating.toLowerCase();
    if (['false', 'fake', 'inaccurate', 'pants on fire', 'misleading'].some(r => lowerRating.includes(r))) {
      return 'bg-red-100 text-red-700 border-red-200';
    }
    if (['true', 'real', 'verified', 'accurate', 'correct'].some(r => lowerRating.includes(r))) {
      return 'bg-green-100 text-green-700 border-green-200';
    }
    if (['mostly', 'partially', 'mixture', 'uncertain', 'disputed'].some(r => lowerRating.includes(r))) {
      return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    }
    return 'bg-secondary text-foreground';
  };

  return (
    <div className={`border-2 rounded-lg p-6 space-y-6 ${getPredictionColor()}`}>
      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          {getPredictionIcon()}
        </div>
        <div className="flex-1">
          <h3 className={`text-2xl font-bold ${getPredictionTextColor()}`}>
            {result.prediction}
          </h3>
          <p className="text-sm text-muted-foreground mt-1">
            Analysis Result
          </p>
        </div>
        {onDownloadPDF && (
          <Button
            variant="outline"
            size="sm"
            onClick={onDownloadPDF}
            className="flex gap-2"
          >
            <Download size={16} />
            PDF
          </Button>
        )}
      </div>

      {/* Headline */}
      <div>
        <h4 className="text-sm font-semibold text-muted-foreground mb-2">Headline</h4>
        <p className="text-foreground font-medium">{result.headline}</p>
      </div>

      {/* Image Preview */}
      {result.image_url && (
        <div>
          <h4 className="text-sm font-semibold text-muted-foreground mb-2">Image</h4>
          <img
            src={result.image_url}
            alt="Analysis"
            className="w-full h-48 object-cover rounded-lg border border-border"
          />
        </div>
      )}

      {/* Confidence */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <ConfidenceBar confidence={result.confidence} label="Overall Confidence" />
        </div>
        {result.similarity !== undefined && (
          <div>
            <ConfidenceBar confidence={result.similarity} label="Image-Text Similarity" />
          </div>
        )}
      </div>

      {/* Explanation */}
      <div>
        <h4 className="text-sm font-semibold text-muted-foreground mb-2">Explanation</h4>
        <p className="text-foreground leading-relaxed italic border-l-4 border-primary/20 pl-4 py-1">
          {result.explanation}
        </p>
      </div>

      {/* Fact Checks */}
      {result.fact_checks && result.fact_checks.length > 0 && (
        <div className="pt-4 border-t border-border/50">
          <h4 className="text-sm font-semibold text-muted-foreground mb-4 flex items-center gap-2">
            Fact-Check References
            <span className="text-[10px] bg-secondary px-1.5 py-0.5 rounded-full">{result.fact_checks.length}</span>
          </h4>
          <div className="grid grid-cols-1 gap-3">
            {result.fact_checks.map((fc, idx) => (
              <div key={idx} className="bg-background rounded-lg p-4 border border-border transition-all hover:shadow-sm">
                <div className="flex justify-between items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-sm text-foreground truncate">{fc.title}</p>
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2 leading-relaxed">{fc.claim_reviewed}</p>
                  </div>
                  <span className={`flex-shrink-0 text-[10px] uppercase tracking-wider font-extrabold px-2 py-1 rounded border ${getRatingColor(fc.rating)}`}>
                    {fc.rating}
                  </span>
                </div>
                {fc.url && (
                  <div className="mt-3 pt-3 border-t border-border/30">
                    <a
                      href={fc.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:text-blue-800 font-semibold inline-flex items-center gap-1 group"
                    >
                      Verify original report <span className="transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5">↗</span>
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timestamp */}
      <div className="text-[10px] text-muted-foreground pt-4 border-t border-border text-right uppercase tracking-widest">
        Analyzed on {new Date(result.created_at).toLocaleString()}
      </div>
    </div>
  );
}
