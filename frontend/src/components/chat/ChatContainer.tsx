import React, { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { useChat } from '../../contexts/ChatContext';
import { LoadingBox } from '../loading/LoadingBox';
import { LoadingMessage } from '../loading/LoadingMessage';

const ChatContainer: React.FC = () => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, sendMessage, isLoading, conversationTitle } = useChat();

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col w-4/5 h-full">
      {conversationTitle && (
        <div className="p-3 border-b-2 border-black bg-gray-100">
          <h2 className="font-bold">{conversationTitle}</h2>
        </div>
      )}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500 font-mono">
              Start a new conversation or select one from the sidebar.
            </p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}

            {/* Show loading animation when waiting for assistant's response */}
            {isLoading && (
              <div className="mb-4 p-4 border-2 border-black bg-white">
                <div className="mb-2 font-bold uppercase">Assistant</div>
                  {/* Thinking line with spinning circle */}
                  <div className="flex items-center space-x-2 mb-2">
                    <LoadingBox />
                    <span className="font-mono">PROCESSING...</span>
                  </div>

                  {/* Brutalist text loading effect */}
                  <LoadingMessage />
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatContainer;