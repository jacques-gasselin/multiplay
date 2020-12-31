package org.multiplay;

import java.util.UUID;

public class GameToken {
    private UUID uuid;

    public GameToken(UUID uuid) {
        this.uuid = uuid;
    }

    @Override
    public final String toString() {
        return uuid.toString();
    }
}
