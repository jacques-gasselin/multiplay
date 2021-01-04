package org.multiplay.client.response;

import java.util.ArrayList;
import java.util.List;

public class SessionPlayersResponse {
    private List<String> players = new ArrayList<>();

    public List<String> getPlayers() {
        return players;
    }

    public void setPlayers(List<String> players) {
        this.players = players;
    }

    @Override
    public String toString() {
        return players.toString();
    }
}
