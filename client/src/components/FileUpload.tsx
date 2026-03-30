/**
 * FileUpload Component
 */

import { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onImageUrlChange: (url: string) => void;
  selectedImage?: string;
}

export default function FileUpload({ onFileSelect, onImageUrlChange, selectedImage }: FileUploadProps) {
  const [uploadMode, setUploadMode] = useState<'url' | 'file'>('url');
  const [imageUrl, setImageUrl] = useState('');
  const [preview, setPreview] = useState<string | null>(selectedImage || null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setPreview(result);
        onFileSelect(file);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleUrlChange = (url: string) => {
    setImageUrl(url);
    setPreview(url);
    onImageUrlChange(url);
  };

  const clearImage = () => {
    setPreview(null);
    setImageUrl('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full space-y-4">
      <div className="flex gap-2 mb-4">
        <Button
          variant={uploadMode === 'url' ? 'default' : 'outline'}
          onClick={() => setUploadMode('url')}
          className="flex-1"
        >
          URL
        </Button>
        <Button
          variant={uploadMode === 'file' ? 'default' : 'outline'}
          onClick={() => setUploadMode('file')}
          className="flex-1"
        >
          Upload
        </Button>
      </div>

      {uploadMode === 'url' ? (
        <div className="space-y-2">
          <label className="text-sm font-medium">Image URL</label>
          <input
            type="url"
            placeholder="https://example.com/image.jpg"
            value={imageUrl}
            onChange={(e) => handleUrlChange(e.target.value)}
            className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      ) : (
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            className="hidden"
          />
          <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
          <p className="text-sm font-medium">Drag and drop your image here</p>
          <p className="text-xs text-muted-foreground">or click to browse</p>
        </div>
      )}

      {preview && (
        <div className="relative rounded-lg overflow-hidden bg-secondary p-2">
          <img
            src={preview}
            alt="Preview"
            className="w-full h-48 object-cover rounded"
          />
          <button
            onClick={clearImage}
            className="absolute top-4 right-4 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
          >
            <X size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
