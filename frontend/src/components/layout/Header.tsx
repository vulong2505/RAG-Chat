import React from 'react';
import FileUpload from '../documents/FileUpload';

const Header: React.FC = () => {
    return (
        <header className="flex justify-between items-center p-4 border-b-2">
            <h1 className="text-xl font-bold text-black">
                Local RAG Chat
            </h1>
            <FileUpload />
        </header>
    );
};

export default Header;