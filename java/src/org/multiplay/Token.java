package org.multiplay;

import java.util.UUID;

public abstract class Token {
    private UUID uuid = null;

    public Token(String tokenString) {
        this.uuid = UUID.fromString(tokenString);
    }

    @Override
    public final String toString() {
        return uuid.toString();
    }
}
