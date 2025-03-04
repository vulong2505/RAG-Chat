import React, { createContext, useState, useContext, useCallback, ReactNode } from 'react';
import { Message, Source } from '../types';

interface ChatContextType {
  messages: Message[];
  isLoading: boolean;
  currentConversationId: number | null;
  conversationTitle: string;
  sendMessage: (content: string) => Promise<void>;
  loadConversation: (conversationId: number) => Promise<void>;
  startNewConversation: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [conversationTitle, setConversationTitle] = useState<string>('');

  // Load messages when a conversation is selected
  const loadConversation = useCallback(async (conversationId: number) => {
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/conversations/${conversationId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load conversation');
      }
      
      const data = await response.json();
      
      // Convert API message format to our app's format
      const formattedMessages: Message[] = data.messages.map((msg: any) => ({
        role: msg.role,
        content: msg.content,
        sources: msg.sources.map((src: any) => ({
          content: src.content,
          source: src.source
        }))
      }));
      
      setMessages(formattedMessages);
      setCurrentConversationId(conversationId);
      setConversationTitle(data.title);
    } catch (error) {
      console.error('Error loading conversation:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Reset for a new conversation
  const startNewConversation = useCallback(() => {
    setMessages([]);
    setCurrentConversationId(null);
    setConversationTitle('');
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Add user message to chat
    const userMessage: Message = { role: 'user', content };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Prepare request data based on whether it's a new or existing conversation
      const requestData = {
        message: content,
        ...(currentConversationId ? { conversation_id: currentConversationId } : {})
      };  

      console.log(requestData.conversation_id)

      // Call your backend API
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      
      // Update conversation ID if this was a new conversation
      if (!currentConversationId && data.conversation_id) {
        setCurrentConversationId(data.conversation_id);
        setConversationTitle(data.title || 'New Conversation');
      }
      
      // Prepare sources if available
      let sources: Source[] = [];
      if (data.sources && data.sources.length > 0) {
        sources = data.sources.map((src: any) => ({
          content: src.content,
          source: src.source
        }));
      }

      // Add assistant message to chat
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        sources: sources.length > 0 ? sources : undefined
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, there was an error processing your request.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [currentConversationId]);

  const value = {
    messages,
    isLoading,
    currentConversationId,
    conversationTitle,
    sendMessage,
    loadConversation,
    startNewConversation
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

// Hook to use the chat context
export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};