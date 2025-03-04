import React, { useRef, useState, useEffect } from 'react';
import { LoadingBox } from "../loading/LoadingBox";

const FileUpload: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadStatus({ type: null, message: '' });

    // Handle file upload to backend
    const formData = new FormData();
    formData.append('file', files[0]);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Error uploading file');
      }
      
      setUploadStatus({
        type: 'success',
        message: data.message || `Successfully uploaded ${files[0].name}`
      });
      console.log('File uploaded:', data);
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus({
        type: 'error',
        message: error instanceof Error ? error.message : 'Failed to upload file'
      });
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Automatically hide the status message after 8 seconds
  useEffect(() => {
    if (uploadStatus.type) {
      const timeout = setTimeout(() => {
        setUploadStatus({ type: null, message: '' });
      }, 8000);

      return () => clearTimeout(timeout);
    }
  }, [uploadStatus.type]);
  
  return (
    <div className="relative">
      <button 
        onClick={handleUploadClick}
        disabled={isUploading}
        className={`px-4 py-2 bg-white border-2 border-black hover:bg-gray-100 font-mono ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        {isUploading ? 'Uploading...' : 'Upload Document'}
      </button>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.txt,.docx"
        disabled={isUploading}
      />
      
      {/* Status message */}
      {uploadStatus.type && (
        <div 
          className={`absolute right-0 top-full mt-2 p-2 text-sm border-2 z-10 ${
            uploadStatus.type === 'success' 
              ? 'border-green-500 bg-green-50 text-green-700' 
              : 'border-red-500 bg-red-50 text-red-700'
          }`}
        >
          {uploadStatus.message}
        </div>
      )}
      
      {/* Overlay when uploading */}
      {isUploading && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded border-2 border-black font-mono">
            <div className="flex flex-col items-center">
              <div className="text-xl mb-4 flex items-center gap-2">
                Uploading Document <LoadingBox />
              </div>
              <div className="text-sm">This might take a moment depending on file size</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;