import React, { useState, useRef } from 'react';
import { Upload, AlertTriangle, FileText, Check, X, Settings, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const AccessibilityProcessor = () => {
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      file => file.type === 'application/pdf'
    );
    
    setFiles(prev => [...prev, ...droppedFiles]);
  };

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files).filter(
      file => file.type === 'application/pdf'
    );
    setFiles(prev => [...prev, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const processFiles = () => {
    setProcessing(true);
    setError(null);
    // Simulated processing - replace with actual API call
    setTimeout(() => {
      setProcessing(false);
      setResults(files.map(file => ({
        filename: file.name,
        status: 'success',
        violations: Math.floor(Math.random() * 5)
      })));
    }, 2000);
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>PDF Accessibility Processor</CardTitle>
        </CardHeader>
        <CardContent>
          {/* File Upload Area */}
          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className="border-2 border-dashed rounded-lg p-8 text-center mb-4 hover:border-blue-500 transition-colors"
          >
            <Upload className="mx-auto mb-4 text-gray-400" size={48} />
            <p className="mb-2">Drag and drop PDF files here, or</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="text-blue-500 hover:text-blue-700"
            >
              browse to upload
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              multiple
              accept=".pdf"
              className="hidden"
            />
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="mb-4">
              <h3 className="text-lg font-semibold mb-2">Selected Files</h3>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                    <div className="flex items-center">
                      <FileText size={20} className="mr-2 text-gray-500" />
                      <span>{file.name}</span>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <X size={20} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Process Button */}
          {files.length > 0 && (
            <button
              onClick={processFiles}
              disabled={processing}
              className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:bg-blue-300 flex items-center justify-center"
            >
              {processing ? (
                <>
                  <RefreshCw className="animate-spin mr-2" size={20} />
                  Processing...
                </>
              ) : (
                'Process Files'
              )}
            </button>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Processing Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {results.map((result, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded">
                  <div className="flex items-center">
                    {result.status === 'success' ? (
                      <Check className="text-green-500 mr-2" size={20} />
                    ) : (
                      <AlertTriangle className="text-yellow-500 mr-2" size={20} />
                    )}
                    <span>{result.filename}</span>
                  </div>
                  <span className="text-sm">
                    {result.violations} accessibility violations found
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert variant="destructive" className="mt-4">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {error}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default AccessibilityProcessor;
