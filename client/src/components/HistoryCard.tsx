/**
 * HistoryCard Component
 */

import { AlertCircle, CheckCircle, AlertTriangle, Trash2, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { AnalysisResponse } from '@/services/api';

interface HistoryCardProps {
  analysis: AnalysisResponse;
  onDelete?: (id: string) => void;
  onDownload?: (id: string) => void;
  onClick?: () => void;
}

export default function HistoryCard({ analysis, onDelete, onDownload, onClick }: HistoryCardProps) {
  const getPredictionIcon = () => {
    switch (analysis.prediction) {
      case 'Fake':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'Real':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'Misleading':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default:
        return null;
    }
  };

  const getPredictionBadgeColor = () => {
    switch (analysis.prediction) {
      case 'Fake':
        return 'bg-red-100 text-red-700';
      case 'Real':
        return 'bg-green-100 text-green-700';
      case 'Misleading':
        return 'bg-yellow-100 text-yellow-700';
      default:
        return 'bg-secondary text-foreground';
    }
  };

  return (
    <div
      onClick={onClick}
      className="border border-border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          {/* Headline */}
          <p className="font-medium text-foreground truncate mb-2">
            {analysis.headline}
          </p>

          {/* Prediction Badge */}
          <div className="flex items-center gap-2 mb-3">
            {getPredictionIcon()}
            <span className={`text-xs font-semibold px-2 py-1 rounded ${getPredictionBadgeColor()}`}>
              {analysis.prediction}
            </span>
            <span className="text-xs text-muted-foreground">
              {Math.round(analysis.confidence * 100)}% confidence
            </span>
          </div>

          {/* Date */}
          <p className="text-xs text-muted-foreground">
            {new Date(analysis.created_at).toLocaleString()}
          </p>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2">
          {onDownload && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onDownload(analysis._id);
              }}
              className="text-blue-500 hover:text-blue-700 hover:bg-blue-50"
            >
              <Download size={16} />
            </Button>
          )}

          {onDelete && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(analysis._id);
              }}
              className="text-red-500 hover:text-red-700 hover:bg-red-50"
            >
              <Trash2 size={16} />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
