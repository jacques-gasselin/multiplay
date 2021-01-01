package org.multiplay.client;

public class Player {
    private String displayName = "";

    Player(String displayName) {
        if (displayName != null) {
            this.displayName = displayName;
        }
    }

    public final String getDisplayName() {
        return displayName;
    }
}
