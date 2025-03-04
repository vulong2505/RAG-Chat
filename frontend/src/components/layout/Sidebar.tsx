import React, { useEffect, useState } from 'react';
import { useChat } from '../../contexts/ChatContext';

type ChatHistoryItem = {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
};

interface SidebarProps {
  onSelectConversation: (conversationId: number) => void;
  onNewChat: () => void;
  currentConversationId: number | null;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  onSelectConversation, 
  onNewChat,
  currentConversationId
}) => {
  const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Get refresh trigger from context
  const { messages } = useChat();

  // Fetch chat history whenever currentConversationId changes or a new message is added
  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/conversations');
        
        if (!response.ok) {
          throw new Error('Failed to fetch chat history');
        }
        
        const data = await response.json();
        setChatHistory(data);
      } catch (err) {
        console.error('Error fetching chat history:', err);
        setError('Failed to load chat history');
      } finally {
        setLoading(false);
      }
    };

    fetchChatHistory();
  }, [currentConversationId, messages.length]); // Refresh when conversation changes or messages are added

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <div className="w-1/5 border-r-2 border-black overflow-y-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">Chat History</h2>
        <button 
          onClick={onNewChat}
          className="px-3 py-1 bg-white border-2 border-black hover:bg-gray-100 font-mono text-sm"
        >
          + New Chat
        </button>
      </div>
      
      <div className="flex flex-col gap-2">
        {loading ? (
          <div className="text-center py-4">Loading...</div>
        ) : error ? (
          <div className="text-center py-4 text-red-500">{error}</div>
        ) : chatHistory.length === 0 ? (
          <div className="text-center py-4">No chat history found</div>
        ) : (
          chatHistory.map((chat) => (
            <div 
              key={chat.id} 
              className={`p-3 border-2 border-black hover:bg-gray-100 cursor-pointer ${
                currentConversationId === chat.id ? 'bg-gray-200' : ''
              }`}
              onClick={() => onSelectConversation(chat.id)}
            >
              <div className="font-bold">{chat.title}</div>
              <div className="text-xs mt-1">{formatDate(chat.updated_at)}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Sidebar;