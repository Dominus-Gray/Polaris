import React, { useState, useEffect, useRef } from 'react';

// Voice Input Hook with Speech Recognition
export function useVoiceInput(onResult, language = 'en-US') {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Check if speech recognition is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSupported(!!SpeechRecognition);

    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = language;

      recognitionRef.current.onstart = () => {
        setIsListening(true);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        const fullTranscript = finalTranscript || interimTranscript;
        setTranscript(fullTranscript);

        if (finalTranscript && onResult) {
          onResult(finalTranscript.trim());
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [language, onResult]);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setTranscript('');
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  return {
    isListening,
    isSupported,
    transcript,
    startListening,
    stopListening
  };
}

// Voice Input Field Component
export function VoiceInputField({ 
  value, 
  onChange, 
  placeholder = "Start typing or click to speak...",
  className = "",
  disabled = false,
  ...props 
}) {
  const [localValue, setLocalValue] = useState(value || '');
  const { isListening, isSupported, transcript, startListening, stopListening } = useVoiceInput(
    (result) => {
      setLocalValue(result);
      onChange?.({ target: { value: result } });
    }
  );

  useEffect(() => {
    setLocalValue(value || '');
  }, [value]);

  useEffect(() => {
    if (transcript && isListening) {
      setLocalValue(transcript);
    }
  }, [transcript, isListening]);

  const handleInputChange = (e) => {
    setLocalValue(e.target.value);
    onChange?.(e);
  };

  const toggleVoiceInput = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div className="relative">
      <input
        {...props}
        value={localValue}
        onChange={handleInputChange}
        placeholder={placeholder}
        disabled={disabled}
        className={`w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${className}`}
      />
      
      {isSupported && (
        <button
          type="button"
          onClick={toggleVoiceInput}
          disabled={disabled}
          className={`absolute right-2 top-2 p-1.5 rounded transition-all duration-200 ${
            isListening
              ? 'bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400 animate-pulse'
              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-600'
          }`}
          title={isListening ? 'Stop recording' : 'Start voice input'}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </button>
      )}
      
      {/* Voice input status indicator */}
      {isListening && (
        <div className="absolute top-full left-0 right-0 mt-1 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-red-800 dark:text-red-300">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span>Listening... Speak clearly</span>
            <button 
              onClick={stopListening}
              className="ml-auto text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
            >
              Stop
            </button>
          </div>
          {transcript && (
            <div className="text-xs text-red-700 dark:text-red-400 mt-1">
              "{transcript}"
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Voice Search Component
export function VoiceSearch({ onSearch, placeholder = "Search or speak your query..." }) {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleVoiceResult = (transcript) => {
    setQuery(transcript);
    performSearch(transcript);
  };

  const performSearch = async (searchQuery) => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      // Perform intelligent search with voice input optimization
      const results = await onSearch(searchQuery);
      setSearchResults(results || []);
    } catch (error) {
      console.error('Voice search error:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      performSearch(query);
    }
  };

  return (
    <div className="space-y-3">
      <VoiceInputField
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
      />
      
      {isSearching && (
        <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <span>Searching...</span>
        </div>
      )}
      
      {searchResults.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg max-h-64 overflow-y-auto">
          {searchResults.map((result, index) => (
            <div 
              key={index}
              className="p-3 border-b border-slate-100 dark:border-slate-700 last:border-b-0 hover:bg-slate-50 dark:hover:bg-slate-700 cursor-pointer"
            >
              <div className="font-medium text-slate-900 dark:text-slate-100">{result.title}</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">{result.description}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Accessibility Voice Navigation
export function VoiceNavigation() {
  const [isListening, setIsListening] = useState(false);
  const [commands, setCommands] = useState([]);

  const voiceCommands = {
    'go to dashboard': () => window.location.href = '/home',
    'start assessment': () => window.location.href = '/assessment',
    'find help': () => window.location.href = '/service-request',
    'open knowledge base': () => window.location.href = '/knowledge',
    'show profile': () => window.location.href = '/profile',
    'help': () => {
      const helpButton = document.querySelector('[title="Get Help"]');
      if (helpButton) helpButton.click();
    },
    'scroll up': () => window.scrollTo({ top: 0, behavior: 'smooth' }),
    'scroll down': () => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
  };

  const { isListening: voiceActive, isSupported, transcript, startListening, stopListening } = useVoiceInput(
    (result) => {
      const command = result.toLowerCase().trim();
      if (voiceCommands[command]) {
        voiceCommands[command]();
        
        // Show success feedback
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        toast.textContent = `✅ Executed: "${command}"`;
        document.body.appendChild(toast);
        
        setTimeout(() => {
          toast.style.opacity = '0';
          setTimeout(() => {
            if (toast.parentNode) {
              document.body.removeChild(toast);
            }
          }, 300);
        }, 2000);
      } else {
        // Show available commands
        setCommands(Object.keys(voiceCommands));
      }
    }
  );

  if (!isSupported) return null;

  return (
    <div className="fixed bottom-4 left-52 z-40">
      <button
        onClick={voiceActive ? stopListening : startListening}
        className={`w-12 h-12 rounded-full shadow-lg transition-all duration-200 flex items-center justify-center ${
          voiceActive
            ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
            : 'bg-indigo-600 hover:bg-indigo-700 text-white'
        }`}
        title={voiceActive ? 'Stop voice navigation' : 'Start voice navigation'}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
      </button>

      {/* Voice commands help */}
      {commands.length > 0 && (
        <div className="absolute bottom-14 left-0 w-64 bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <div className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-2">
            Try these voice commands:
          </div>
          <div className="space-y-1">
            {commands.slice(0, 5).map((command) => (
              <div key={command} className="text-xs text-slate-600 dark:text-slate-400">
                • "{command}"
              </div>
            ))}
          </div>
          <button
            onClick={() => setCommands([])}
            className="mt-2 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}