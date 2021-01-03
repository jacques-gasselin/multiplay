package org.multiplay.client;

import org.multiplay.SessionToken;

import java.util.concurrent.CompletionStage;

public class LocalSession extends Session {
    private String shareCode;

    LocalSession(Connection connection, SessionToken localSessionToken, String displayName, String shareCode) {
        super(connection, localSessionToken, displayName);
        this.shareCode = shareCode;
    }

    String getShareCode() {
        return this.shareCode;
    }

    @Override
    public String toString() {
        return getDisplayName() + " #" + getShareCode();
    }
}
