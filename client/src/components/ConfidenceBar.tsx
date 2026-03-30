/**
 * ConfidenceBar Component
 */

interface ConfidenceBarProps {
  confidence: number;
  label?: string;
  showPercentage?: boolean;
}

export default function ConfidenceBar({
  confidence,
  label = "Confidence",
  showPercentage = true
}: ConfidenceBarProps) {
  const percentage = Math.round(confidence * 100);
  
  // Determine color based on confidence level
  let barColor = 'bg-red-500';
  let bgColor = 'bg-red-100';
  
  if (confidence >= 0.7) {
    barColor = 'bg-green-500';
    bgColor = 'bg-green-100';
  } else if (confidence >= 0.5) {
    barColor = 'bg-yellow-500';
    bgColor = 'bg-yellow-100';
  }

  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium">{label}</span>
        {showPercentage && <span className="text-sm font-semibold text-foreground">{percentage}%</span>}
      </div>
      <div className={`w-full h-3 rounded-full overflow-hidden ${bgColor}`}>
        <div
          className={`h-full ${barColor} transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
