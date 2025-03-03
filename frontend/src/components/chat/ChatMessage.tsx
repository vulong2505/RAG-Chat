import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '../../types';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`mb-4 p-4 border-2 border-black ${isUser ? 'ml-8 bg-gray-100' : 'mr-8 bg-white'}`}>
      <div className="mb-2">
        <span className="font-bold uppercase">{isUser ? 'User' : 'Assistant'}</span>
      </div>
      <div className="prose prose-sm max-w-none whitespace-pre-wrap">
        <ReactMarkdown>
          {message.content}
        </ReactMarkdown>
      </div>
      {message.sources && message.sources.length > 0 && (
        <div className="mt-4 text-sm">
          <details>
            <summary className="font-bold cursor-pointer">Sources ({message.sources.length})</summary>
            <ul className="mt-2 pl-4">
              {message.sources.map((source, index) => (
                <li key={index} className="mb-2">
                  <div className="mb-1">{source.content}</div>
                  {source.source && <div className="text-xs text-gray-600">{source.source}</div>}
                </li>
              ))}
            </ul>
          </details>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;