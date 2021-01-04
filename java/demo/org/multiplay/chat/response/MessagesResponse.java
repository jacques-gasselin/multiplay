package org.multiplay.chat.response;

import org.multiplay.JSONSerializable;

import java.util.ArrayList;
import java.util.List;

public class MessagesResponse implements JSONSerializable {
    public static final class Message {
        private String sender;
        private String message;

        public String getSender() {
            return sender;
        }

        public void setSender(String sender) {
            this.sender = sender;
        }

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }

        @Override
        public String toString() {
            return sender + ":" + message;
        }
    }

    private List<Message> messages = new ArrayList<>();

    public List<Message> getMessages() {
        return messages;
    }

    public void setMessages(List<Message> messages) {
        this.messages = messages;
    }

    @Override
    public String toString() {
        return messages.toString();
    }

    @Override
    public String toJSONString() {
        StringBuilder b = new StringBuilder();
        b.append("{");
        b.append("\"messages\":[");
        boolean firstMessage = true;
        for (Message m : messages) {
            if (!firstMessage) {
                b.append(",");
            }
            b.append("{\"sender\":\"");
            b.append(m.sender);
            b.append("\",\"message\":\"");
            b.append(m.message);
            b.append("\"}");
            firstMessage = false;
        }
        b.append("]");
        b.append("}");
        return b.toString();
    }
}
