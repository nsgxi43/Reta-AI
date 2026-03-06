export interface Message {
    id: string;
    sender: 'user' | 'ai';
    text: string;
    timestamp: Date;
    suggestions?: string[]; // For product suggestions
}

export type ChatState = {
    messages: Message[];
    isTyping: boolean;
};
