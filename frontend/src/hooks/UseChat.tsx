import { useState, useCallback } from 'react';
import { Message, Source } from '../types';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Add user message to chat
    const userMessage: Message = { role: 'user', content };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call your backend API
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content }),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      
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
  }, []);

  return { messages, sendMessage, isLoading };
};