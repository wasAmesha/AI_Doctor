'use client';

import React from 'react';
import { Plus, MessageSquare, Trash2 } from 'lucide-react';
import { useChat } from '@/contexts/ChatContext';
import { useAuth } from '@/contexts/AuthContext';

export const Sidebar: React.FC = () => {
  const { chats, currentChat, selectChat, createNewChat, deleteChat } = useChat();
  const { user } = useAuth();

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
    }).format(new Date(date));
  };

  return (
    <div className="w-64 bg-gray-900 text-white h-full flex flex-col">
      <div className="p-4">
        <button
          onClick={createNewChat}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md flex items-center justify-center gap-2"
        >
          <Plus size={16} />
          New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="px-4 py-2 text-xs text-gray-400 uppercase tracking-wider">
          Recent Chats
        </div>
        <nav className="space-y-1 px-2">
          {chats.map((chat) => (
            <div
              key={chat.id}
              className={`group flex items-center justify-between p-2 rounded-md cursor-pointer hover:bg-gray-800 ${
                currentChat?.id === chat.id ? 'bg-gray-800' : ''
              }`}
            >
              <div
                className="flex items-center flex-1 min-w-0"
                onClick={() => selectChat(chat.id)}
              >
                <MessageSquare size={16} className="flex-shrink-0 mr-2" />
                <span className="truncate text-sm">
                  {chat.title || 'New Chat'}
                </span>
              </div>
              <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100">
                <span className="text-xs text-gray-400">
                  {formatDate(chat.updatedAt)}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteChat(chat.id);
                  }}
                  className="text-gray-400 hover:text-red-400"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </nav>
      </div>

      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.name}</p>
            <p className="text-xs text-gray-400 truncate">{user?.email}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;