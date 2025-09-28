import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AICoachingInterface() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [userContext, setUserContext] = useState(null);
  const messagesEndRef = useRef(null);
  
  const me = JSON.parse(localStorage.getItem('polaris_me')||'null');

  useEffect(() => {
    initializeCoachingSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeCoachingSession = () => {
    const newSessionId = `coach_${me?.id}_${Date.now()}`;
    setSessionId(newSessionId);
    
    // Load conversation history if available
    loadConversationHistory(newSessionId);
    
    // Add welcome message
    const welcomeMessage = {
      id: 'welcome',
      type: 'ai',
      content: `Hello! I'm your AI procurement readiness coach. 🤖\n\nI'm here to help you navigate your journey to become procurement-ready. I can assist with:\n\n• Assessment guidance and explanations\n• Step-by-step action plans\n• Compliance requirements\n• Resource recommendations\n• Progress tracking insights\n\nWhat would you like to work on today?`,
      timestamp: new Date().toISOString(),
      suggestions: [
        "Help me understand the assessment process",
        "What should I focus on first?",
        "How do I improve my readiness score?",
        "What are the most important compliance requirements?"
      ]
    };
    
    setMessages([welcomeMessage]);
  };

  const loadConversationHistory = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/ai/coach/history/${sessionId}`);
      const history = response.data.history || [];
      
      if (history.length > 0) {
        const conversationMessages = history.map((item, index) => ([
          {
            id: `user_${index}`,
            type: 'user',
            content: item.user_message,
            timestamp: item.timestamp
          },
          {
            id: `ai_${index}`,
            type: 'ai',
            content: item.ai_response,
            timestamp: item.timestamp
          }
        ])).flat();
        
        setMessages(conversationMessages);
      }
    } catch (error) {
      console.warn('Failed to load conversation history:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await axios.post(`${API}/ai/coach/conversation`, {
        message: userMessage.content,
        session_id: sessionId,
        context_area: 'general'
      });

      const aiMessage = {
        id: `ai_${Date.now()}`,
        type: 'ai',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        suggestions: response.data.suggestions || []
      };

      setMessages(prev => [...prev, aiMessage]);
      setSuggestions(response.data.suggestions || []);
      setUserContext(response.data.context);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      
      const errorMessage = {
        id: `error_${Date.now()}`,
        type: 'ai',
        content: "I apologize, but I'm having trouble connecting right now. Please try again in a moment, or you can browse our Knowledge Base for immediate assistance.",
        timestamp: new Date().toISOString(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const useSuggestion = (suggestion) => {
    setInputMessage(suggestion);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const clearConversation = () => {
    if (window.confirm('Are you sure you want to start a new conversation? This will clear your current chat history.')) {
      setMessages([]);
      initializeCoachingSession();
    }
  };

  return (
    <div className="bg-white rounded-lg border shadow-sm flex flex-col h-96">
      {/* Header */}
      <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-slate-900">AI Procurement Coach</h3>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-slate-600">Online & Ready to Help</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {userContext && (
              <div className="text-xs text-slate-600 text-right">
                <div>Progress: {userContext.completion_percentage?.toFixed(1) || 0}%</div>
                <div>{userContext.assessment_completion || 0}/10 areas</div>
              </div>
            )}
            <button
              onClick={clearConversation}
              className="text-slate-500 hover:text-slate-700 p-1"
              title="Start new conversation"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-xs lg:max-w-sm ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
              {message.type === 'ai' && (
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-6 h-6 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <span className="text-xs text-slate-600 font-medium">AI Coach</span>
                </div>
              )}
              
              <div
                className={`p-3 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.isError
                    ? 'bg-red-50 text-red-800 border border-red-200'
                    : 'bg-slate-100 text-slate-900'
                }`}
              >
                <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                <div className={`text-xs mt-2 ${
                  message.type === 'user' ? 'text-blue-100' : 'text-slate-500'
                }`}>
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
              
              {/* Suggestions for AI messages */}
              {message.type === 'ai' && message.suggestions && message.suggestions.length > 0 && (
                <div className="mt-2 space-y-1">
                  {message.suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => useSuggestion(suggestion)}
                      className="block w-full text-left p-2 text-xs text-blue-600 bg-blue-50 hover:bg-blue-100 rounded border border-blue-200 transition-colors"
                    >
                      💡 {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="max-w-xs bg-slate-100 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <span className="text-xs text-slate-600">AI Coach is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t">
        {/* Quick Suggestions */}
        {suggestions.length > 0 && (
          <div className="mb-3">
            <div className="flex flex-wrap gap-2">
              {suggestions.slice(0, 3).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => useSuggestion(suggestion)}
                  className="px-3 py-1.5 text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-full border transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Message Input */}
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about procurement readiness..."
              className="w-full p-3 border border-slate-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              rows="2"
              disabled={isLoading}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="p-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex-shrink-0"
          >
            {isLoading ? (
              <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
        
        {/* Character Count */}
        <div className="flex justify-between items-center mt-2 text-xs text-slate-500">
          <span>
            {userContext?.completion_percentage !== undefined && (
              `Your progress: ${userContext.completion_percentage.toFixed(1)}% complete`
            )}
          </span>
          <span className={inputMessage.length > 400 ? 'text-red-500' : ''}>
            {inputMessage.length}/500
          </span>
        </div>
      </div>
    </div>
  );
}

// Floating AI Coach Button Component
export function FloatingAICoach() {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <>
      {/* Floating Coach Button */}
      <div className="fixed bottom-4 left-4 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-14 h-14 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center"
          title="AI Procurement Coach"
        >
          {isOpen ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          )}
        </button>
      </div>

      {/* AI Coach Panel */}
      {isOpen && (
        <div className="fixed bottom-20 left-4 w-80 h-96 z-50">
          <AICoachingInterface />
        </div>
      )}
    </>
  );
}