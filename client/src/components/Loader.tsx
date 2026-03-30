/**
 * Loader Component
 */

import { Loader2 } from 'lucide-react';

interface LoaderProps {
  message?: string;
  fullScreen?: boolean;
}

export default function Loader({ message = "Analyzing...", fullScreen = false }: LoaderProps) {
  const content = (
    <div className="flex flex-col items-center justify-center gap-4">
      <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
      <p className="text-lg font-medium text-foreground">{message}</p>
      <p className="text-sm text-muted-foreground">Please wait while we analyze your content</p>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center py-12">
      {content}
    </div>
  );
}
