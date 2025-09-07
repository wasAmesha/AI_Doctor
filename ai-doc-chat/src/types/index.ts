export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: Date;
  lastLoginAt:Date;
}

export interface ChatSession {
  id: string;
  userId: string;
  title: string;
  createdAt: Date;
  lastUpdatedAt: Date;
  status:string;
  messages: Message[];
}

export interface Message {
  id: string;
  chatId: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

export interface ChatContextType {
  chats: ChatSession[];
  currentChat: ChatSession | null;
  selectChat: (chatId: string) => void;
  createNewChat: () => void;
  sendMessage: (content: string) => Promise<void>;
  deleteChat: (chatId: string) => Promise<void>;
  isLoading: boolean;
}