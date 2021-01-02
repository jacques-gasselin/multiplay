package org.multiplay.chat;

import org.multiplay.client.LocalPlayer;

public interface UserInterface {
    void updatePlayer(LocalPlayer player);
    void updateChannels();
    void updateFriends();
    void updateMessages();
}
