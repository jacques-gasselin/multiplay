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

    @Override
    public boolean equals(Object obj) {
        if (obj == this) {
            return true;
        }
        if (obj instanceof Token) {
            Token t = (Token) obj;
            return t.uuid.equals(uuid);
        }
        return false;
    }
}
