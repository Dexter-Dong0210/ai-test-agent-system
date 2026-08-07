"use client";

import { ReactNode, createContext, useContext } from "react";
import { Assistant } from "@langchain/langgraph-sdk";
import { type StateType, useChat } from "@/hooks/useChat";
import type { UseStreamThread } from "@langchain/langgraph-sdk/react";

interface ChatProviderProps {
  children: ReactNode;
  activeAssistant: Assistant | null;
  onHistoryRevalidate?: () => void;
  thread?: UseStreamThread<StateType>;
  onTestCaseCreated?: () => void; // 测试用例创建后的回调
}
// eslint-disable  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2YVdkWk9BPT06OTgxMTZhOTU=

export function ChatProvider({
  children,
  activeAssistant,
  onHistoryRevalidate,
  thread,
  onTestCaseCreated,
}: ChatProviderProps) {
  const chat = useChat({ activeAssistant, onHistoryRevalidate, thread, onTestCaseCreated });
  return <ChatContext.Provider value={chat}>{children}</ChatContext.Provider>;
}

export type ChatContextType = ReturnType<typeof useChat>;

export const ChatContext = createContext<ChatContextType | undefined>(
  undefined
);

export function useChatContext() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error("useChatContext must be used within a ChatProvider");
  }
  return context;
}
// FIXME  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2YVdkWk9BPT06OTgxMTZhOTU=
