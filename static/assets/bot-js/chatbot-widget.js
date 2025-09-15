(function(window, document) {
  'use strict';

  // Default configuration
  const defaultConfig = {
    apiUrl: 'http://172.20.10.2:5000',
    theme: 'green',
    position: 'bottom-right',
    botName: 'AI Assistant',
    welcomeMessage: "Hi! I'm your AI assistant. How can I help you today?",
    enableSound: true,
    showTypingIndicator: true,
    maxMessages: 50,
    autoConnect: true,
    showAvatar: true,
    allowMinimize: true,
    allowClose: true
  };

  // Global chatbot instance
  let chatbotInstance = null;

  class ChatBotWidget {
    constructor(config = {}) {
      this.config = { ...defaultConfig, ...config };
      this.isOpen = false;
      this.isMinimized = false;
      this.messages = [];
      this.conversationId = this.generateUUID();
      this.unreadCount = 0;
      this.isLoading = false;
      this.socket = null;
      this.isConnected = false;
      this.typingTimeout = null;
      
      this.init();
    }

    generateUUID() {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
    }

    init() {
      this.loadCSS();
      this.createWidget();
      this.bindEvents();
      this.initializeSocket();
      this.addWelcomeMessage();
    }

    // loadCSS() {
    //   if (document.getElementById('chatbot-widget-styles')) return;

    //   const link = document.createElement('link');
    //   link.id = 'chatbot-widget-styles';
    //   link.rel = 'stylesheet';
    //   link.type = 'text/css';
    //   link.href = `${this.config.apiUrl}/chatbot-widget.css`;
    //   document.head.appendChild(link);

    //   // Add inline critical CSS for immediate rendering
    //   const inlineCSS = document.createElement('style');
    //   inlineCSS.innerHTML = `
    //     .chatbot-widget-container {
    //       position: fixed;
    //       z-index: 10000;
    //       font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    //     }
    //     .chatbot-widget-container.chatbot-widget--bottom--right {
    //       bottom: 20px;
    //       right: 20px;
    //     }
    //     .chatbot-toggle-btn {
    //       width: 60px;
    //       height: 60px;
    //       border-radius: 50%;
    //       border: none;
    //       cursor: pointer;
    //       display: flex;
    //       align-items: center;
    //       justify-content: center;
    //       background: linear-gradient(135deg, #25eb9fff, #3b82f6);
    //       color: white;
    //       box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1);
    //       transition: all 0.3s ease;
    //     }
    //     .chatbot-toggle-btn:hover {
    //       transform: translateY(-2px);
    //       box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    //     }
    //   `;
    //   document.head.appendChild(inlineCSS);
    // }






loadCSS() {
  if (document.getElementById('chatbot-widget-styles')) return;

  // Try to use the local CSS first, fallback to API URL
  const localCSS = '/static/assets/css/ChatBotWidget.css';
  
  // Create inline CSS as fallback
  const inlineCSS = document.createElement('style');
  inlineCSS.innerHTML = `
    .chatbot-widget-container {
      position: fixed;
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }
    /* Add all the CSS from your inline styles here */
    ${this.getFullCSS()}
  `;
  document.head.appendChild(inlineCSS);
  
  // Also try to load the external CSS
  const link = document.createElement('link');
  link.id = 'chatbot-widget-styles';
  link.rel = 'stylesheet';
  link.type = 'text/css';
  link.href = localCSS;
  document.head.appendChild(link);
}

getFullCSS() {
  // Return all the CSS that was in your inline style tag
  return `
    .chatbot-widget-container.chatbot-widget--bottom--right {
      bottom: 20px;
      right: 20px;
    }
    .chatbot-toggle-btn {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #25eb9fff, #a5f63bff);
      color: white;
      box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
    }
    .chatbot-toggle-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
    /* Add more styles as needed */
  `;
}



    createWidget() {
      // Remove existing widget if any
      const existingWidget = document.getElementById('chatbot-widget-container');
      if (existingWidget) {
        existingWidget.remove();
      }

      const container = document.createElement('div');
      container.id = 'chatbot-widget-container';
      container.className = `chatbot-widget-container chatbot-widget--${this.config.position.replace('-', '--')}`;
      
      container.innerHTML = this.renderToggleButton();
      document.body.appendChild(container);

      this.container = container;
    }

    renderToggleButton() {
      const unreadBadge = this.unreadCount > 0 ? 
        `<span class="chatbot-unread-badge">${this.unreadCount > 99 ? '99+' : this.unreadCount}</span>` : '';
      
      return `
        <button class="chatbot-toggle-btn chatbot-widget--${this.config.theme}" title="Chat with ${this.config.botName}">
          ${this.getSVGIcon('message-circle')}
          ${unreadBadge}
        </button>
      `;
    }

    renderWidget() {
      const connectionStatus = this.isConnected ? 
        `${this.getSVGIcon('wifi', 12)} Online` : 
        `${this.getSVGIcon('wifi-off', 12)} Offline`;

      return `
        <div class="chatbot-widget chatbot-widget--${this.config.theme} ${this.isMinimized ? 'minimized' : ''}">
          <!-- Header -->
          <div class="chatbot-header">
            <div class="chatbot-header-info">
              ${this.getSVGIcon('bot', 20)}
              <div class="chatbot-header-text">
                <h3>${this.config.botName}</h3>
                <span class="chatbot-status">${connectionStatus}</span>
              </div>
            </div>
            <div class="chatbot-header-controls">
              <button class="chatbot-control-btn" data-action="toggle-sound" title="${this.config.enableSound ? 'Disable sound' : 'Enable sound'}">
                ${this.getSVGIcon(this.config.enableSound ? 'volume-2' : 'volume-x', 16)}
              </button>
              <button class="chatbot-control-btn" data-action="clear" title="Clear conversation">
                ${this.getSVGIcon('refresh-cw', 16)}
              </button>
              ${this.config.allowMinimize ? `
                <button class="chatbot-control-btn" data-action="minimize" title="Minimize">
                  ${this.getSVGIcon('minimize-2', 16)}
                </button>
              ` : ''}
              ${this.config.allowClose ? `
                <button class="chatbot-control-btn" data-action="close" title="Close">
                  ${this.getSVGIcon('x', 16)}
                </button>
              ` : ''}
            </div>
          </div>

          <!-- Messages -->
          <div class="chatbot-messages" id="chatbot-messages">
            ${this.renderMessages()}
          </div>

          <!-- Input -->
          <form class="chatbot-input-form" id="chatbot-form">
            <div class="chatbot-input-container">
              <input
                type="text"
                id="chatbot-input"
                placeholder="Type your message..."
                class="chatbot-message-input"
                ${this.isLoading ? 'disabled' : ''}
              />
              <button type="submit" class="chatbot-send-button" ${!this.isLoading ? '' : 'disabled'}>
                ${this.isLoading ? this.getSVGIcon('loader', 18, 'spinning') : this.getSVGIcon('send', 18)}
              </button>
            </div>
          </form>
        </div>

        ${this.isMinimized ? this.renderMinimizedButton() : ''}
      `;
    }

    renderMinimizedButton() {
      const unreadBadge = this.unreadCount > 0 ? 
        `<span class="chatbot-unread-badge">${this.unreadCount > 99 ? '99+' : this.unreadCount}</span>` : '';
      const connectionIcon = this.isConnected ? this.getSVGIcon('wifi', 14) : this.getSVGIcon('wifi-off', 14);

      return `
        <button class="chatbot-minimized-btn chatbot-widget--${this.config.theme}" data-action="restore" title="Restore chat">
          ${this.getSVGIcon('message-circle', 20)}
          <span class="chatbot-minimized-text">Chat with ${this.config.botName}</span>
          ${connectionIcon}
          ${unreadBadge}
        </button>
      `;
    }

    renderMessages() {
      return this.messages.map((message, index) => {
        const avatar = this.config.showAvatar ? 
          `<div class="chatbot-message-avatar">
            ${message.role === 'user' ? this.getSVGIcon('user', 16) : this.getSVGIcon('bot', 16)}
          </div>` : '';

        return `
          <div class="chatbot-message ${message.role} ${message.isError ? 'error' : ''} ${message.isWelcome ? 'welcome' : ''}">
            ${avatar}
            <div class="chatbot-message-content">
              <p>${this.formatMessage(message.content)}</p>
              <div class="chatbot-message-timestamp">
                ${this.formatTimestamp(message.timestamp)}
              </div>
            </div>
          </div>
        `;
      }).join('') + (this.isLoading ? this.renderTypingIndicator() : '');
    }

    renderTypingIndicator() {
      const avatar = this.config.showAvatar ? 
        `<div class="chatbot-message-avatar">${this.getSVGIcon('bot', 16)}</div>` : '';

      return `
        <div class="chatbot-message assistant typing">
          ${avatar}
          <div class="chatbot-message-content">
            <div class="chatbot-typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      `;
    }

    formatMessage(content) {
      // Basic markdown-like formatting
      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
    }

    formatTimestamp(timestamp) {
      return new Date(timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    }

    getSVGIcon(name, size = 24, className = '') {
      const icons = {
        'message-circle': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/></svg>`,
        'send': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>`,
        'bot': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>`,
        'user': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
        'x': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>`,
        'minimize-2': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><polyline points="4,14 10,14 10,20"/><polyline points="20,10 14,10 14,4"/><line x1="14" y1="10" x2="21" y2="3"/><line x1="3" y1="21" x2="10" y2="14"/></svg>`,
        'volume-2': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="m15.54 8.46 2.92 2.92"/><path d="m20.07 4.93-2.53 2.53"/></svg>`,
        'volume-x': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><path d="M11 5 6 9H2v6h4l5 4V5Z"/><line x1="22" y1="9" x2="16" y2="15"/><line x1="16" y1="9" x2="22" y2="15"/></svg>`,
        'refresh-cw': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><path d="M3 2v6h6"/><path d="M21 12A9 9 0 0 0 6 5.3L3 8"/><path d="M21 22v-6h-6"/><path d="M3 12a9 9 0 0 0 15 6.7l3-2.7"/></svg>`,
        'wifi': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>`,
        'wifi-off': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><line x1="2" y1="2" x2="22" y2="22"/><path d="M8.5 16.429a5 5 0 0 1 7 0"/><path d="M3.27 6.96c4.29-4.023 11.17-4.02 15.46.04l-2.16 2.16C14.37 6.9 9.63 6.9 7.43 9.1l-4.16-2.14Z"/></svg>`,
        'loader': `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${className}"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>`
      };
      return icons[name] || '';
    }

    bindEvents() {
      this.container.addEventListener('click', (e) => {
        const action = e.target.closest('[data-action]')?.dataset.action;
        
        switch (action) {
          case 'toggle':
            this.toggleWidget();
            break;
          case 'close':
            this.closeWidget();
            break;
          case 'minimize':
            this.minimizeWidget();
            break;
          case 'restore':
            this.restoreWidget();
            break;
          case 'clear':
            this.clearConversation();
            break;
          case 'toggle-sound':
            this.toggleSound();
            break;
        }

        if (e.target.closest('.chatbot-toggle-btn')) {
          this.toggleWidget();
        }
      });

      // Form submission
      document.addEventListener('submit', (e) => {
        if (e.target.id === 'chatbot-form') {
          e.preventDefault();
          this.sendMessage();
        }
      });

      // Input events
      document.addEventListener('input', (e) => {
        if (e.target.id === 'chatbot-input') {
          this.handleTyping();
        }
      });

      // Keyboard shortcuts
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isOpen) {
          this.closeWidget();
        }
      });
    }

    // initializeSocket() {
    //   if (!this.config.autoConnect) return;

    //   try {
    //     // Load socket.io client if not already loaded
    //     if (typeof io === 'undefined') {
    //       const script = document.createElement('script');
    //       script.src = `${this.config.apiUrl}/socket.io/socket.io.js`;
    //       script.onload = () => this.connectSocket();
    //       document.head.appendChild(script);
    //     } else {
    //       this.connectSocket();
    //     }
    //   } catch (error) {
    //     console.warn('Socket.IO not available, using HTTP fallback');
    //   }
    // }


  // Update the initializeSocket method in your chatbot-widget.js
// initializeSocket() {
//   if (!this.config.autoConnect) return;

//   try {
//     // Connect to Django Channels WebSocket
//     this.socket = new WebSocket(
//       `ws://${window.location.host}/ws/chat/${this.conversationId}/`
//     );

//     console.log(`Connecting to WebSocket: ws://${window.location.host}/ws/chat/${this.conversationId}/`);
    

//     this.socket.onopen = () => {
//       this.isConnected = true;
//       this.updateConnectionStatus();
//       console.log('WebSocket connection established');
//     };
    
//     this.socket.onclose = () => {
//       this.isConnected = false;
//       this.updateConnectionStatus();
//       console.log('WebSocket connection closed');
//     };
    
//     this.socket.onerror = (error) => {
//       console.error('WebSocket error:', error);
//       this.isConnected = false;
//       this.updateConnectionStatus();
//     };
    
//     this.socket.onmessage = (e) => {
//       const data = JSON.parse(e.data);
      
//       if (data.type === 'chat_message') {
//         this.addMessage({
//           role: data.role,
//           content: data.message,
//           timestamp: new Date().toISOString()
//         });
//         this.isLoading = false;
//         this.updateWidget();
//       } else if (data.type === 'typing_indicator') {
//         // Handle typing indicator if needed
//       }
//     };
//   } catch (error) {
//     console.warn('WebSocket not available, using HTTP fallback');
//   }
// }

// // Update the sendMessage method to use WebSocket
// async sendMessage() {
//   const input = document.getElementById('chatbot-input');
//   if (!input || !input.value.trim() || this.isLoading) return;

//   const message = input.value.trim();
//   input.value = '';

//   this.addMessage({
//     role: 'user',
//     content: message,
//     timestamp: new Date().toISOString()
//   });

//   this.isLoading = true;
//   this.updateWidget();

//   try {
//     if (this.socket && this.socket.readyState === WebSocket.OPEN) {
//       // Send via WebSocket
//       this.socket.send(JSON.stringify({
//         type: 'chat_message',
//         message: message,
//         conversationId: this.conversationId
//       }));
//     } else {
//       // Fallback to HTTP
//       const response = await fetch(`${this.config.apiUrl}/api/chat/`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           'X-CSRFToken': this.config.csrfToken
//         },
//         body: JSON.stringify({
//           message: message,
//           conversationId: this.conversationId
//         })
//       });

//       const data = await response.json();
      
//       this.addMessage({
//         role: 'assistant',
//         content: data.message,
//         timestamp: data.timestamp
//       });
//       this.isLoading = false;
//       this.updateWidget();
//     }
//   } catch (error) {
//     console.error('Error sending message:', error);
//     this.addMessage({
//       role: 'assistant',
//       content: '❌ **Error:** Failed to send message. Please try again.',
//       timestamp: new Date().toISOString(),
//       isError: true
//     });
//     this.isLoading = false;
//     this.updateWidget();
//   }
// }




// In your ChatBotWidget class
initializeSocket() {
  if (!this.config.autoConnect) return;

  try {
    // Use the correct WebSocket URL - note the different port
    const backendHost = this.config.apiUrl.replace('http://', '').replace('https://', '');
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${backendHost}/ws/chat/${this.conversationId}/`;
    
    console.log(`Connecting to WebSocket: ${wsUrl}`);
    
    this.socket = new WebSocket(wsUrl);
    
    this.socket.onopen = () => {
      this.isConnected = true;
      this.updateConnectionStatus();
      console.log('WebSocket connection established');
    };
    
    this.socket.onclose = (event) => {
      this.isConnected = false;
      this.updateConnectionStatus();
      console.log('WebSocket connection closed', event.code, event.reason);
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.isConnected = false;
      this.updateConnectionStatus();
    };
    
    this.socket.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        
        if (data.type === 'chat_message') {
          this.addMessage({
            role: data.role,
            content: data.message,
            timestamp: new Date().toISOString()
          });
          this.isLoading = false;
          this.updateWidget();
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  } catch (error) {
    console.warn('WebSocket not available, using HTTP fallback');
  }
}

// Update sendMessage method to use WebSocket
async sendMessage() {
  const input = document.getElementById('chatbot-input');
  if (!input || !input.value.trim() || this.isLoading) return;

  const message = input.value.trim();
  input.value = '';

  this.addMessage({
    role: 'user',
    content: message,
    timestamp: new Date().toISOString()
  });

  this.isLoading = true;
  this.updateWidget();

  try {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      // Send via WebSocket
      this.socket.send(JSON.stringify({
        type: 'chat_message',
        message: message,
        conversationId: this.conversationId
      }));
    } else {
      // Fallback to HTTP
      const response = await fetch(`${this.config.apiUrl}/api/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          message: message,
          conversationId: this.conversationId
        })
      });

      const data = await response.json();
      
      this.addMessage({
        role: 'assistant',
        content: data.message,
        timestamp: data.timestamp
      });
      this.isLoading = false;
      this.updateWidget();
    }
  } catch (error) {
    console.error('Error sending message:', error);
    this.addMessage({
      role: 'assistant',
      content: '❌ **Error:** Failed to send message. Please try again.',
      timestamp: new Date().toISOString(),
      isError: true
    });
    this.isLoading = false;
    this.updateWidget();
  }
}


// Update the handleTyping method
handleTyping() {
  if (this.socket && this.socket.readyState === WebSocket.OPEN) {
    this.socket.send(JSON.stringify({
      type: 'typing',
      conversationId: this.conversationId,
      isTyping: true
    }));

    clearTimeout(this.typingTimeout);
    this.typingTimeout = setTimeout(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({
          type: 'typing',
          conversationId: this.conversationId,
          isTyping: false
        }));
      }
    }, 1000);
  }
}

    

    connectSocket() {
      if (typeof io === 'undefined') return;

      this.socket = io(this.config.apiUrl);
      
      this.socket.on('connect', () => {
        this.isConnected = true;
        this.socket.emit('join-conversation', this.conversationId);
        this.updateConnectionStatus();
      });

      this.socket.on('disconnect', () => {
        this.isConnected = false;
        this.updateConnectionStatus();
      });

      this.socket.on('ai-message', (data) => {
        if (data.conversationId === this.conversationId) {
          this.addMessage({
            role: 'assistant',
            content: data.message,
            timestamp: data.timestamp
          });
          this.isLoading = false;
          this.updateWidget();
        }
      });
    }

    updateConnectionStatus() {
      if (this.isOpen) {
        const statusElement = this.container.querySelector('.chatbot-status');
        if (statusElement) {
          const connectionStatus = this.isConnected ? 
            `${this.getSVGIcon('wifi', 12)} Online` : 
            `${this.getSVGIcon('wifi-off', 12)} Offline`;
          statusElement.innerHTML = connectionStatus;
        }
      }
    }

    addWelcomeMessage() {
      this.addMessage({
        role: 'assistant',
        content: this.config.welcomeMessage,
        timestamp: new Date().toISOString(),
        isWelcome: true
      });
    }

    addMessage(message) {
      this.messages.push(message);
      if (this.messages.length > this.config.maxMessages) {
        this.messages = this.messages.slice(-this.config.maxMessages);
      }

      // Update unread count if widget is closed
      if (!this.isOpen && message.role === 'assistant' && !message.isWelcome) {
        this.unreadCount++;
        this.playNotificationSound();
      }
    }

    toggleWidget() {
      this.isOpen = !this.isOpen;
      if (this.isOpen) {
        this.unreadCount = 0;
        this.isMinimized = false;
      }
      this.updateWidget();
    }

    closeWidget() {
      this.isOpen = false;
      this.updateWidget();
    }

    minimizeWidget() {
      this.isMinimized = true;
      this.updateWidget();
    }

    restoreWidget() {
      this.isMinimized = false;
      this.updateWidget();
    }

    clearConversation() {
      this.messages = [];
      this.conversationId = this.generateUUID();
      this.unreadCount = 0;
      this.addWelcomeMessage();
      
      if (this.socket) {
        this.socket.emit('join-conversation', this.conversationId);
      }
      
      this.updateWidget();
    }

    toggleSound() {
      this.config.enableSound = !this.config.enableSound;
      this.updateWidget();
    }

    // async sendMessage() {
    //   const input = document.getElementById('chatbot-input');
    //   if (!input || !input.value.trim() || this.isLoading) return;

    //   const message = input.value.trim();
    //   input.value = '';

    //   this.addMessage({
    //     role: 'user',
    //     content: message,
    //     timestamp: new Date().toISOString()
    //   });

    //   this.isLoading = true;
    //   this.updateWidget();

    //   try {
    //     const response = await fetch(`${this.config.apiUrl}/api/chat`, {
    //       method: 'POST',
    //       headers: {
    //         'Content-Type': 'application/json'
    //       },
    //       body: JSON.stringify({
    //         message: message,
    //         conversationId: this.conversationId
    //       })
    //     });

    //     const data = await response.json();

    //     if (!this.isConnected) {
    //       // Fallback to HTTP response if no real-time connection
    //       this.addMessage({
    //         role: 'assistant',
    //         content: data.data.message,
    //         timestamp: data.data.timestamp
    //       });
    //       this.isLoading = false;
    //       this.updateWidget();
    //     }
    //   } catch (error) {
    //     console.error('Error sending message:', error);
    //     this.addMessage({
    //       role: 'assistant',
    //       content: '❌ **Error:** Failed to send message. Please try again.',
    //       timestamp: new Date().toISOString(),
    //       isError: true
    //     });
    //     this.isLoading = false;
    //     this.updateWidget();
    //   }
    // }


    // In your chatbot-widget.js, update the sendMessage method:

async sendMessage() {
  const input = document.getElementById('chatbot-input');
  if (!input || !input.value.trim() || this.isLoading) return;

  const message = input.value.trim();
  input.value = '';

  this.addMessage({
    role: 'user',
    content: message,
    timestamp: new Date().toISOString()
  });

  this.isLoading = true;
  this.updateWidget();

  try {
    // Use the correct API endpoint with website ID
    const response = await fetch(`${this.config.apiUrl}/api/chat/${this.config.websiteId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.getCSRFToken()
      },
      body: JSON.stringify({
        message: message,
        conversationId: this.conversationId
      })
    });

    const data = await response.json();

    if (!this.isConnected || !response.ok) {
      // Fallback to HTTP response if no real-time connection or error
      this.addMessage({
        role: 'assistant',
        content: data.response || data.error || 'Sorry, I encountered an error.',
        timestamp: new Date().toISOString()
      });
      this.isLoading = false;
      this.updateWidget();
    }
  } catch (error) {
    console.error('Error sending message:', error);
    this.addMessage({
      role: 'assistant',
      content: '❌ **Error:** Failed to send message. Please try again.',
      timestamp: new Date().toISOString(),
      isError: true
    });
    this.isLoading = false;
    this.updateWidget();
  }
}

// Also update the connectSocket method:
// connectSocket() {
//   if (typeof io === 'undefined') return;

//   this.socket = io(this.config.apiUrl, {
//     path: '/api/socket.io/'
//   });
  
//   this.socket.on('connect', () => {
//     this.isConnected = true;
//     this.socket.emit('join-conversation', { conversationId: this.conversationId });
//     this.updateConnectionStatus();
//   });

//   this.socket.on('disconnect', () => {
//     this.isConnected = false;
//     this.updateConnectionStatus();
//   });

//   this.socket.on('ai-message', (data) => {
//     if (data.conversationId === this.conversationId) {
//       this.addMessage({
//         role: 'assistant',
//         content: data.message,
//         timestamp: data.timestamp || new Date().toISOString()
//       });
//       this.isLoading = false;
//       this.updateWidget();
//     }
//   });
// }
    handleTyping() {
      if (this.socket && this.conversationId) {
        this.socket.emit('typing', {
          conversationId: this.conversationId,
          isTyping: true
        });

        clearTimeout(this.typingTimeout);
        this.typingTimeout = setTimeout(() => {
          if (this.socket) {
            this.socket.emit('typing', {
              conversationId: this.conversationId,
              isTyping: false
            });
          }
        }, 1000);
      }
    }

    playNotificationSound() {
      if (!this.config.enableSound) return;

      try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
      } catch (error) {
        console.log('Audio not available');
      }
    }

    updateWidget() {
      if (this.isOpen) {
        this.container.innerHTML = this.renderWidget();
        setTimeout(() => this.scrollToBottom(), 100);
        
        // Focus input
        const input = document.getElementById('chatbot-input');
        if (input && !this.isMinimized) {
          input.focus();
        }
      } else {
        this.container.innerHTML = this.renderToggleButton();
      }
    }

    scrollToBottom() {
      const messagesContainer = document.getElementById('chatbot-messages');
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }

    // Public API methods
    open() {
      this.isOpen = true;
      this.unreadCount = 0;
      this.updateWidget();
    }

    close() {
      this.isOpen = false;
      this.updateWidget();
    }

    sendMessageProgrammatically(message) {
      this.addMessage({
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      });
      this.updateWidget();
      // Trigger API call...
    }

    destroy() {
      if (this.socket) {
        this.socket.disconnect();
      }
      if (this.container) {
        this.container.remove();
      }
      clearTimeout(this.typingTimeout);
    }
  }

  // Global initialization function
  window.initChatBot = function(config) {
    if (chatbotInstance) {
      chatbotInstance.destroy();
    }
    chatbotInstance = new ChatBotWidget(config);
    return chatbotInstance;
  };

  // Auto-initialize if configuration is provided
  if (window.ChatBotConfig) {
    window.initChatBot(window.ChatBotConfig);
  }

  // Expose the ChatBot class globally
  window.ChatBotWidget = ChatBotWidget;

})(window, document);