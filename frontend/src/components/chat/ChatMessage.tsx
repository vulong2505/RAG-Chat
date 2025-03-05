import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '../../types';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  // Process thinking tags in content
  const processThinkingTags = (content: string) => {
    // Check if content has thinking tags
    const thinkRegex = /<think(?:ing)?>([\s\S]*?)(?:<\/think(?:ing)?>|$)/i;
    const match = content.match(thinkRegex);
    
    if (match) {
      // Extract thinking content and main content
      const thinkingContent = match[1].trim();
      const mainContent = content.replace(thinkRegex, '').trim();
      
      return {
        hasThinking: true,
        thinkingContent,
        mainContent: mainContent || "..." // Fallback if main content is empty
      };
    }
    
    return {
      hasThinking: false,
      mainContent: content
    };
  };
  
  const processedContent = processThinkingTags(message.content);
  
  return (
    <div className={`mb-4 p-4 border-2 border-black ${isUser ? 'ml-8 bg-gray-100' : 'mr-8 bg-white'}`}>
      <div className="mb-2">
        <span className="font-bold uppercase">{isUser ? 'User' : 'Assistant'}</span>
      </div>

      {processedContent.hasThinking && (
        <div className="mt-4 text-sm">
          <details>
            <summary className="font-bold cursor-pointer">Thinking Process</summary>
            <div className="mt-2 p-3 bg-gray-50 border border-gray-200 whitespace-pre-wrap">
              <ReactMarkdown>
              {processedContent.thinkingContent}
              </ReactMarkdown>
            </div>
          </details>
        </div>
      )}

      <div className="whitespace-pre-wrap leading-relaxed">
        <ReactMarkdown>
        {processedContent.mainContent}
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