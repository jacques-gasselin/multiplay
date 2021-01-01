package org.multiplay.client.response;

import java.util.ArrayList;
import java.util.List;

public class LocalPlayerFriendsResponse {
    public static final class Friend {
        private String remotePlayerToken;
        private String displayName;

        public Friend(String remotePlayerToken, String displayName) {
            this.remotePlayerToken = remotePlayerToken;
            this.displayName = displayName;
        }

        public String getRemotePlayerToken() {
            return remotePlayerToken;
        }

        public String getDisplayName() {
            return displayName;
        }
    }
    private List<Friend> friends = new ArrayList<>();

    public LocalPlayerFriendsResponse() {

    }

    public void addFriend(Friend friend) {
        friends.add(friend);
    }

    public List<Friend> getFriends() {
        return friends;
    }

    public String toString() {
        return "friends: " + friends;
    }
}
