package org.multiplay.client.response;

import java.util.ArrayList;
import java.util.List;

public final class LocalPlayerSessionsResponse {
    public static final class Session {
        private String localSessionToken;
        private String displayName;
        private String shareCode;

        public Session() {

        }

        public void setLocalSessionToken(String localSessionToken) {
            this.localSessionToken = localSessionToken;
        }

        public String getLocalSessionToken() {
            return localSessionToken;
        }

        public void setDisplayName(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }

        public void setShareCode(String shareCode) {
            this.shareCode = shareCode;
        }

        public String getShareCode() {
            return shareCode;
        }

        public String toString() {
            return "localSessionToken: " + localSessionToken + ", displayName: " + displayName + ", shareCode: " + shareCode;
        }
    }

    private List<Session> sessions = new ArrayList<>();

    public LocalPlayerSessionsResponse() {

    }

    public void setSessions(List<Session> sessions) {
        this.sessions = sessions;
    }

    public void addSession(Session session) {
        sessions.add(session);
    }

    public List<Session> getSessions() {
        return sessions;
    }

    public String toString() {
        return "sessions: " + sessions;
    }
}
