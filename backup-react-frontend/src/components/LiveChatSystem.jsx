import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function LiveChatSystem({ context, contextId, participants = [] }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');
  const chatId = `${context}_${contextId}`;

  useEffect(() => {
    if (isOpen) {
      loadMessages();
      // Poll for new messages every 3 seconds when chat is open
      const interval = setInterval(loadMessages, 3000);
      return () => clearInterval(interval);
    }
  }, [isOpen, chatId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      const response = await axios.get(`${API}/chat/messages/${chatId}`);
      setMessages(response.data.messages || []);
      
      // Load online users
      const onlineResponse = await axios.get(`${API}/chat/online/${chatId}`);
      setOnlineUsers(onlineResponse.data.users || []);
    } catch (error) {
      console.warn('Failed to load chat messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !me) return;

    const messageData = {
      chat_id: chatId,
      sender_id: me.id,
      sender_name: me.name || me.email,
      sender_role: me.role,
      content: newMessage.trim(),
      context: context,
      context_id: contextId,
      timestamp: new Date().toISOString()
    };

    try {
      setLoading(true);
      await axios.post(`${API}/chat/send`, messageData);
      setNewMessage('');
      await loadMessages(); // Refresh messages after sending
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'client': return '🏢';
      case 'provider': return '🛠️';
      case 'navigator': return '🧭';
      case 'agency': return '🏛️';
      default: return '👤';
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'client': return 'text-blue-600';
      case 'provider': return 'text-green-600';
      case 'navigator': return 'text-purple-600';
      case 'agency': return 'text-indigo-600';
      default: return 'text-slate-600';
    }
  };

  if (!me) {
    return null;
  }

  return (
    <>
      {/* Chat Toggle Button */}
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="relative w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center"
        >
          {isOpen ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          )}
          
          {messages.filter(m => !m.read && m.sender_id !== me.id).length > 0 && (
            <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {messages.filter(m => !m.read && m.sender_id !== me.id).length}
            </div>
          )}
        </button>
      </div>

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 w-80 h-96 bg-white rounded-lg shadow-2xl border z-50 flex flex-col">
          {/* Chat Header */}
          <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-purple-50">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-slate-900">
                  {context === 'service_request' ? 'Service Discussion' : 
                   context === 'assessment' ? 'Assessment Support' :
                   context === 'rp_lead' ? 'RP Lead Discussion' : 'General Chat'}
                </h3>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex -space-x-1">
                    {onlineUsers.slice(0, 3).map((user, index) => (
                      <div
                        key={user.id}
                        className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-xs border-2 border-white"
                        title={user.name}
                      >
                        {getRoleIcon(user.role)}
                      </div>
                    ))}
                  </div>
                  <span className="text-xs text-slate-500">
                    {onlineUsers.length} online
                  </span>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-500 hover:text-slate-700 p-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {loading ? (
              <div className="text-center text-slate-500">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-sm">Loading messages...</p>
              </div>
            ) : messages.length === 0 ? (
              <div className="text-center text-slate-500 py-8">
                <svg className="w-8 h-8 mx-auto mb-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p className="text-sm">Start the conversation!</p>
              </div>
            ) : (
              messages.map((message, index) => {
                const isMe = message.sender_id === me.id;
                return (
                  <div
                    key={index}
                    className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-xs ${isMe ? 'order-2' : 'order-1'}`}>
                      {!isMe && (
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm">{getRoleIcon(message.sender_role)}</span>
                          <span className={`text-xs font-medium ${getRoleColor(message.sender_role)}`}>
                            {message.sender_name}
                          </span>
                        </div>
                      )}
                      <div
                        className={`p-3 rounded-lg ${
                          isMe
                            ? 'bg-blue-600 text-white'
                            : 'bg-slate-100 text-slate-900'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${isMe ? 'text-blue-100' : 'text-slate-500'}`}>
                          {formatTimestamp(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <div className="p-4 border-t">
            <div className="flex items-center gap-2">
              <div className="flex-1">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  className="w-full p-2 border border-slate-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows="2"
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={!newMessage.trim() || loading}
                className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
            
            {isTyping && (
              <div className="flex items-center gap-2 mt-2 text-xs text-slate-500">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                Someone is typing...
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}