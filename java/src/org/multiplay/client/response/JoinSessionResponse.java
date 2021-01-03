package org.multiplay.client.response;

public final class JoinSessionResponse {
    private String localSessionToken = null;
    private String displayName = "";
    private String shareCode = "";

    public String getLocalSessionToken() {
        return localSessionToken;
    }

    public void setLocalSessionToken(String localSessionToken) {
        this.localSessionToken = localSessionToken;
    }

    public String getDisplayName() {
        return displayName;
    }

    public void setDisplayName(String displayName) {
        this.displayName = displayName;
    }

    public String getShareCode() {
        return shareCode;
    }

    public void setShareCode(String shareCode) {
        this.shareCode = shareCode;
    }

    public String toString() {
        return "localSessionToken: " + localSessionToken + ", displayName: " + displayName + ", shareCode: " + shareCode;
    }
}
