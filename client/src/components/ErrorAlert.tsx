/**
 * ErrorAlert Component
 */

import { AlertCircle, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ErrorAlertProps {
  message: string;
  onClose?: () => void;
  title?: string;
}

export default function ErrorAlert({ message, onClose, title = "Error" }: ErrorAlertProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-4">
      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <h4 className="font-semibold text-red-900">{title}</h4>
        <p className="text-sm text-red-700 mt-1">{message}</p>
      </div>
      {onClose && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="text-red-600 hover:text-red-700 hover:bg-red-100"
        >
          <X size={16} />
        </Button>
      )}
    </div>
  );
}
