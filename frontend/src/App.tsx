import React from 'react';
import Header from './components/layout/Header';
import ChatLayout from './components/chat/ChatLayout';

const App: React.FC = () => {
  return (
    <div className="flex flex-col h-screen font-mono">
      <Header />
      <ChatLayout />
    </div>
  );
};

export default App;