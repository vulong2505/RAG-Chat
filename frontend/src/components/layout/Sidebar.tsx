import React from 'react';

type ChatHistoryItem = {
  id: number;
  title: string;
  date: string;
};

const Sidebar: React.FC = () => {

  // This would be populated from PostgreSQL later
  const chatHistory: ChatHistoryItem[] = [
    { id: 1, title: 'Chat about RAG systems', date: '2025-02-27' },
    { id: 2, title: 'DeepSeek model capabilities', date: '2025-02-26' },
  ];

  return (
    <div className="w-1/5 border-r-2 border-black overflow-y-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">Chat History</h2>
        <button className="px-3 py-1 bg-white border-2 border-black hover:bg-gray-100 font-mono text-sm cursor-pointer">
          + New Chat
        </button>
      </div>
      
      <div className="flex flex-col gap-2">
        {chatHistory.map((chat) => (
          <div key={chat.id} className="p-3 border-2 border-black hover:bg-gray-100 cursor-pointer">
            <div className="font-bold">{chat.title}</div>
            <div className="text-xs mt-1">{chat.date}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;