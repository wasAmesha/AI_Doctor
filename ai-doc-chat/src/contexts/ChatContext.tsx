'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { Chat, Message, ChatContextType } from '@/types';
import { chatsAPI, messagesAPI } from '@/lib/api';
import { useAuth } from './AuthContext';

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChat, setCurrentChat] = useState<Chat | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      loadChats();
    }
  }, [user]);

  const loadChats = async () => {
    try {
      setIsLoading(true);
      const chatData = await chatsAPI.getAll();
      setChats(chatData);
      if (chatData.length > 0 && !currentChat) {
        setCurrentChat(chatData[0]);
      }
    } catch (error) {
      console.error('Failed to load chats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const selectChat = async (chatId: string) => {
    const chat = chats.find(c => c.id === chatId);
    if (chat) {
      setCurrentChat(chat);
    }
  };

  const createNewChat = async () => {
    try {
      const newChat = await chatsAPI.create();
      setChats(prev => [newChat, ...prev]);
      setCurrentChat(newChat);
      return newChat;
    } catch (error) {
      console.error('Failed to create chat:', error);
      throw error;
    }
  };

  const sendMessage = async (content: string) => {
    if (!currentChat) {
      const newChat = await createNewChat();
      await messagesAPI.send(newChat.id, content);
    } else {
      await messagesAPI.send(currentChat.id, content);
    }
    await loadChats(); // Refresh to get updated messages
  };

  const deleteChat = async (chatId: string) => {
    await chatsAPI.delete(chatId);
    setChats(prev => prev.filter(chat => chat.id !== chatId));
    if (currentChat?.id === chatId) {
      setCurrentChat(chats.length > 1 ? chats[0] : null);
    }
  };

  return (
    <ChatContext.Provider value={{
      chats,
      currentChat,
      selectChat,
      createNewChat,
      sendMessage,
      deleteChat,
      isLoading
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};