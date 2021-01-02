package org.multiplay.client.response;

public final class ConnectionResponse {
    private String connectionToken = null;

    public void setConnectionToken(String connectionToken) {
        this.connectionToken = connectionToken;
    }

    public String getConnectionToken() {
        return this.connectionToken;
    }

    public String toString() {
        return "connectionToken: " + connectionToken;
    }
}
