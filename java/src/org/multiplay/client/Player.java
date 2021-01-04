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

    protected final void setDisplayName(String displayName) {
        this.displayName = displayName;
    }

    @Override
    public String toString() {
        return displayName;
    }
}
