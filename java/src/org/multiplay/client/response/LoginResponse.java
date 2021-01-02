package org.multiplay.client.response;

import org.multiplay.LocalPlayerToken;

public final class LoginResponse {
    private LocalPlayerToken localPlayerToken = null;
    private String displayName = null;
    private String friendCode = null;
    private boolean authenticated = false;

    public LocalPlayerToken getLocalPlayerToken() {
        return localPlayerToken;
    }

    public void setLocalPlayerToken(String localPlayerToken) {
        this.localPlayerToken = new LocalPlayerToken(localPlayerToken);
    }

    public String getDisplayName() {
        return displayName;
    }

    public void setDisplayName(String displayName) {
        this.displayName = displayName;
    }

    public String getFriendCode() {
        return friendCode;
    }

    public void setFriendCode(String friendCode) {
        this.friendCode = friendCode;
    }

    public boolean isAuthenticated() {
        return authenticated;
    }

    public String getAuthenticated() {
        return authenticated ? "true" : "false";
    }

    public void setAuthenticated(String trueOrFalse) {
        if (trueOrFalse != null && trueOrFalse.equalsIgnoreCase("true")) {
            this.authenticated = true;
        } else {
            this.authenticated = false;
        }
    }

    public String toString() {
        return "localPlayerToken: " + localPlayerToken + ", displayName: " + displayName + ", friendCode: " + friendCode + ", authenticated: " + authenticated;
    }
}
