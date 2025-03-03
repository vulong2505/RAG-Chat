import React, { useRef } from 'react';

const FileUpload: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    // Handle file upload to backend
    const formData = new FormData();
    formData.append('file', files[0]);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      console.log('File uploaded:', data);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div>
      <button 
        onClick={handleUploadClick}
        className="px-4 py-2 bg-white border-2 border-black hover:bg-gray-100 font-mono cursor-pointer"
      >
        Upload Document
      </button>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.txt,.docx"
      />
    </div>
  );
};

export default FileUpload;