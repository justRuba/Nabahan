# frontend/components/chat_interface.py
# Chat Interface Component for Nabahan
# =====================================

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional, Callable


def get_chat_css() -> str:
    """Return CSS styles for the chat interface."""
    return """
    <style>
        /* Chat Container */
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Message Bubbles */
        .message-bubble {
            padding: 12px 18px;
            border-radius: 18px;
            margin: 8px 0;
            max-width: 85%;
            word-wrap: break-word;
            direction: rtl;
            text-align: right;
        }

        .user-bubble {
            background: linear-gradient(135deg, #1f77b4 0%, #0d47a1 100%);
            color: white;
            margin-left: auto;
            margin-right: 0;
            border-bottom-right-radius: 4px;
        }

        .bot-bubble {
            background-color: #f0f2f6;
            color: #333;
            margin-right: auto;
            margin-left: 0;
            border-bottom-left-radius: 4px;
        }

        /* Message Header */
        .message-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
            font-weight: bold;
        }

        .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }

        .user-avatar {
            background-color: #1f77b4;
            color: white;
        }

        .bot-avatar {
            background-color: #4caf50;
            color: white;
        }

        /* Typing Indicator */
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 15px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background-color: #1f77b4;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 100% {
                transform: translateY(0);
                opacity: 0.4;
            }
            50% {
                transform: translateY(-5px);
                opacity: 1;
            }
        }

        /* Data Preview Card */
        .data-preview-card {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 15px;
            margin-top: 10px;
        }

        .data-preview-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }

        .data-preview-title {
            font-weight: bold;
            color: #333;
        }

        .data-preview-count {
            background-color: #1f77b4;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }

        /* SQL Code Block */
        .sql-code-block {
            background-color: #282c34;
            color: #abb2bf;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            overflow-x: auto;
            direction: ltr;
            text-align: left;
        }

        /* Insight Card */
        .insight-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin: 15px 0;
        }

        .insight-card h4 {
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Quick Actions */
        .quick-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 15px 0;
        }

        .quick-action-btn {
            background-color: #f0f2f6;
            border: 1px solid #1f77b4;
            color: #1f77b4;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }

        .quick-action-btn:hover {
            background-color: #1f77b4;
            color: white;
        }
    </style>
    """


class ChatMessage:
    """Represents a single chat message."""

    def __init__(
            self,
            role: str,
            content: str,
            data: Optional[pd.DataFrame] = None,
            plot_type: Optional[str] = None,
            sql: Optional[str] = None,
            status: Optional[str] = None
    ):
        self.role = role
        self.content = content
        self.data = data
        self.plot_type = plot_type
        self.sql = sql
        self.status = status


class ChatInterface:
    """
    A reusable chat interface component for Nabahan.
    """

    def __init__(
            self,
            agent_function: Callable,
            filters: Optional[Dict] = None
    ):
        """
        Initialize the chat interface.

        Args:
            agent_function: The function to call for generating responses
            filters: Optional filters to apply to queries
        """
        self.agent_function = agent_function
        self.filters = filters or {}
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state for chat history."""
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []

        if 'processing' not in st.session_state:
            st.session_state.processing = False

    def add_message(self, message: ChatMessage):
        """Add a message to the chat history."""
        st.session_state.chat_messages.append(message)

    def clear_history(self):
        """Clear chat history."""
        st.session_state.chat_messages = []

    def render_message(self, message: ChatMessage):
        """Render a single chat message."""
        if message.role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(message.content)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message.content)

                # Render data if available
                if message.data is not None and not message.data.empty:
                    with st.expander(f"📊 عرض البيانات ({len(message.data)} صف)", expanded=False):
                        st.dataframe(
                            message.data.head(50),
                            use_container_width=True
                        )

                # Render SQL if available
                if message.sql:
                    with st.expander("🔧 عرض استعلام SQL", expanded=False):
                        st.code(message.sql, language="sql")

    def render_quick_suggestions(self):
        """Render quick action suggestions."""
        suggestions = [
            "كم عدد المناقصات الحالية؟",
            "أعلى 5 جهات حكومية من حيث عدد المناقصات",
            "توزيع المشاريع حسب المنطقة",
            "ما هي المناقصات المجانية؟"
        ]

        st.markdown("#### 💡 اقتراحات سريعة")
        cols = st.columns(2)

        for i, suggestion in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                    return suggestion

        return None

    def process_query(self, query: str) -> ChatMessage:
        """
        Process a user query and get response from agent.

        Args:
            query: The user's question

        Returns:
            ChatMessage with the agent's response
        """
        # Call the agent function
        response = self.agent_function(query, self.filters if self.filters else None)

        return ChatMessage(
            role="assistant",
            content=response.get('insights', 'عذراً، حدث خطأ أثناء معالجة السؤال.'),
            data=response.get('data'),
            plot_type=response.get('plot'),
            sql=response.get('sql'),
            status=response.get('status')
        )

    def render(self):
        """Render the complete chat interface."""
        # Inject CSS
        st.markdown(get_chat_css(), unsafe_allow_html=True)

        # Header
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h2 style="color: #1f77b4;">💬 محادثة نبهان</h2>
            <p style="color: #666;">اسأل نبهان عن أي شيء متعلق بالمناقصات والمشاريع الحكومية</p>
        </div>
        """, unsafe_allow_html=True)

        # Quick suggestions (only show if no messages)
        if len(st.session_state.chat_messages) == 0:
            suggestion = self.render_quick_suggestions()
            if suggestion:
                # Add user message
                user_msg = ChatMessage(role="user", content=suggestion)
                self.add_message(user_msg)

                # Get and add bot response
                with st.spinner("نبهان يفكر..."):
                    bot_msg = self.process_query(suggestion)
                    self.add_message(bot_msg)

                st.rerun()

        # Display chat history
        for message in st.session_state.chat_messages:
            self.render_message(message)

        # Chat input
        user_input = st.chat_input("اكتب سؤالك هنا...")

        if user_input:
            # Add user message
            user_msg = ChatMessage(role="user", content=user_input)
            self.add_message(user_msg)
            self.render_message(user_msg)

            # Get and add bot response
            with st.spinner("نبهان يفكر..."):
                bot_msg = self.process_query(user_input)
                self.add_message(bot_msg)

            st.rerun()

        # Clear history button
        if len(st.session_state.chat_messages) > 0:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🗑️ مسح المحادثة", use_container_width=True):
                    self.clear_history()
                    st.rerun()


def render_chat_interface(agent_function: Callable, filters: Optional[Dict] = None):
    """
    Convenience function to render the chat interface.

    Args:
        agent_function: The function to call for generating responses
        filters: Optional filters to apply to queries
    """
    chat = ChatInterface(agent_function, filters)
    chat.render()
