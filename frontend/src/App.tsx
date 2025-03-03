import React from 'react';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import ChatContainer from './components/chat/ChatContainer';

const App: React.FC = () => {
  return (
    <div className="flex flex-col h-screen font-mono">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <ChatContainer />
      </div>
    </div>
  );
};

export default App;