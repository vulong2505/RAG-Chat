import React from 'react';
import Sidebar from '../layout/Sidebar';
import ChatContainer from './ChatContainer';
import { useChat } from '../../contexts/ChatContext';

const ChatLayout: React.FC = () => {
  const { 
    loadConversation,
    startNewConversation,
    currentConversationId
  } = useChat();

  const handleSelectConversation = (conversationId: number) => {
    loadConversation(conversationId);
  };

  const handleNewChat = () => {
    startNewConversation();
  };

  return (
    <div className="flex flex-1 overflow-hidden">
      <Sidebar 
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        currentConversationId={currentConversationId}
      />
      <ChatContainer />
    </div>
  );
};

export default ChatLayout;