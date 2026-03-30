/**
 * TextInput Component
 */

interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  label?: string;
  maxLength?: number;
}

export default function TextInput({
  value,
  onChange,
  placeholder = "Enter headline text...",
  label = "Headline",
  maxLength = 1000
}: TextInputProps) {
  const characterCount = value.length;
  const isNearLimit = characterCount > maxLength * 0.8;

  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium">{label}</label>
        <span className={`text-xs ${isNearLimit ? 'text-orange-500' : 'text-muted-foreground'}`}>
          {characterCount} / {maxLength}
        </span>
      </div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value.slice(0, maxLength))}
        placeholder={placeholder}
        maxLength={maxLength}
        rows={4}
        className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
      />
      <p className="text-xs text-muted-foreground">
        Enter a news headline or claim to analyze for misinformation.
      </p>
    </div>
  );
}
