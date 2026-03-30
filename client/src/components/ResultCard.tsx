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
        <p className="text-foreground">{result.headline}</p>
      </div>

      {/* Image Preview */}
      {result.image_url && (
        <div>
          <h4 className="text-sm font-semibold text-muted-foreground mb-2">Image</h4>
          <img
            src={result.image_url}
            alt="Analysis"
            className="w-full h-48 object-cover rounded-lg"
          />
        </div>
      )}

      {/* Confidence */}
      <div>
        <ConfidenceBar confidence={result.confidence} label="Overall Confidence" />
      </div>

      {/* Similarity */}
      {result.similarity !== undefined && (
        <div>
          <ConfidenceBar confidence={result.similarity} label="Image-Text Similarity" />
        </div>
      )}

      {/* Explanation */}
      <div>
        <h4 className="text-sm font-semibold text-muted-foreground mb-2">Explanation</h4>
        <p className="text-foreground leading-relaxed">{result.explanation}</p>
      </div>

      {/* Fact Checks */}
      {result.fact_checks && result.fact_checks.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-muted-foreground mb-3">Fact-Check References</h4>
          <div className="space-y-3">
            {result.fact_checks.map((fc, idx) => (
              <div key={idx} className="bg-background rounded-lg p-3 border border-border">
                <div className="flex justify-between items-start gap-2">
                  <div className="flex-1">
                    <p className="font-medium text-sm">{fc.title}</p>
                    <p className="text-xs text-muted-foreground mt-1">{fc.claim_reviewed}</p>
                  </div>
                  <span className="text-xs font-semibold px-2 py-1 bg-secondary rounded">
                    {fc.rating}
                  </span>
                </div>
                {fc.url && (
                  <a
                    href={fc.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline mt-2 inline-block"
                  >
                    View Source →
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timestamp */}
      <div className="text-xs text-muted-foreground border-t border-border pt-4">
        Analyzed on {new Date(result.created_at).toLocaleString()}
      </div>
    </div>
  );
}
