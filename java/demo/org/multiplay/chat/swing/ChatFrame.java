package org.multiplay.chat.swing;

import org.multiplay.chat.Chat;
import org.multiplay.chat.UserInterface;
import org.multiplay.chat.response.MessagesResponse;
import org.multiplay.client.Friend;
import org.multiplay.client.LocalPlayer;
import org.multiplay.client.LocalSession;
import org.multiplay.client.Session;

import javax.swing.*;
import java.awt.*;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import javax.swing.ScrollPaneConstants;

public class ChatFrame extends JFrame implements UserInterface {
    private final Chat chat;

    private JButton loginButton = new JButton("Login");
    private JLabel guestLabel = new JLabel("Guest account: ");
    private JLabel playerName = new JLabel();

    private DefaultListModel<Session> channelsListModel = new DefaultListModel<Session>();
    private JList channelsList = new JList(channelsListModel);
    private JButton addChannelButton = new JButton("+");
    private JButton joinChannelButton = new JButton("Join");

    private DefaultListModel<Friend> friendsListModel = new DefaultListModel<Friend>();
    private JList friendsList = new JList(friendsListModel);
    private JButton addFriendButton = new JButton("+");

    private JPanel channelsAndFriendsPanel = new JPanel();
    private JScrollPane channelsAndFriendsPanelScrollPane = new JScrollPane(channelsAndFriendsPanel);

    private JPanel chatPanel = new JPanel();
    private JPanel messagesPane = new JPanel();
    private JScrollPane messagesScrollPane = new JScrollPane(messagesPane);
    private JTextField messageEntryField = new JTextField();

    private LocalPlayer player;
    private Session localSession = null;

    public ChatFrame() {
        super("Multiplay Chat");
        chat = new Chat();

        addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosed(WindowEvent e) {
                super.windowClosed(e);
                chat.close();
            }
        });

        configurePanes();
        layoutPanes();

        Timer timer = new Timer(5 * 1000, event -> {
            updateMessages();
        });
        timer.start();
    }

    private void configurePanes() {
        Dimension minChannelsDimension = new Dimension(200, 400);
        Dimension minChatDimension = new Dimension(400, 400);

        Dimension minChatMessageScrollDimension = new Dimension(400, 368);
        Dimension minChatMessageEntryDimension = new Dimension(400, 32);

        Dimension buttonSize = new Dimension(32, 24);

        channelsList.addListSelectionListener(event -> {
            List<LocalSession> sessions = player.getLocalSessions();
            int index = channelsList.getSelectedIndex();
            localSession = sessions.get(index);
            System.out.println("selected channel " + localSession);
            updateMessages();
        });

        addChannelButton.setMinimumSize(buttonSize);
        addChannelButton.setPreferredSize(buttonSize);
        addChannelButton.setMaximumSize(buttonSize);
        addChannelButton.addActionListener(actionEvent -> {
            createChannel();
        });

        joinChannelButton.setMinimumSize(buttonSize);
        joinChannelButton.setPreferredSize(buttonSize);
        joinChannelButton.setMaximumSize(buttonSize);
        joinChannelButton.addActionListener(actionEvent -> {
            joinChannel();
        });

        addFriendButton.setMinimumSize(buttonSize);
        addFriendButton.setPreferredSize(buttonSize);
        addFriendButton.setMaximumSize(buttonSize);
        addFriendButton.addActionListener(actionEvent -> {
            addFriend();
        });

        channelsAndFriendsPanel.setMinimumSize(minChannelsDimension);
        channelsAndFriendsPanel.setPreferredSize(minChannelsDimension);
        channelsAndFriendsPanel.setBackground(Color.LIGHT_GRAY);

        chatPanel.setMinimumSize(minChatDimension);
        chatPanel.setBackground(Color.WHITE);

        messagesScrollPane.setMinimumSize(minChatMessageScrollDimension);
        messagesScrollPane.setWheelScrollingEnabled(true);
        messagesScrollPane.setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS);

        messageEntryField.setMinimumSize(minChatMessageEntryDimension);
        messageEntryField.setPreferredSize(minChatMessageEntryDimension);
        messageEntryField.setEnabled(false);
        messageEntryField.addActionListener(event -> {
            sendMessage(messageEntryField.getText());
            messageEntryField.setText("");
        });
    }

    private void layoutPanes() {
        Container pane = getContentPane();

        JPanel topPanel = new JPanel();
        topPanel.setLayout(new BoxLayout(topPanel, BoxLayout.LINE_AXIS));
        topPanel.setBorder(BorderFactory.createEmptyBorder(5, 5,5,5));
        topPanel.setAlignmentX(0f);
        topPanel.add(loginButton);
        topPanel.add(guestLabel);
        topPanel.add(playerName);

        channelsAndFriendsPanel.setLayout(new BoxLayout(channelsAndFriendsPanel, BoxLayout.PAGE_AXIS));
        channelsAndFriendsPanel.setAlignmentX(0f);
        channelsAndFriendsPanel.setBorder(BorderFactory.createEmptyBorder(5, 5,5,5));
        Box channelsTitleBox = Box.createHorizontalBox();
        channelsTitleBox.add(new JLabel("Channels"));
        channelsTitleBox.add(Box.createRigidArea(new Dimension(10, 1)));
        channelsTitleBox.add(addChannelButton);
        channelsTitleBox.add(joinChannelButton);
        channelsTitleBox.add(Box.createHorizontalGlue());
        channelsAndFriendsPanel.add(channelsTitleBox);
        Box channelsBox = Box.createHorizontalBox();
        channelsBox.add(channelsList);
        channelsBox.add(Box.createHorizontalGlue());
        channelsAndFriendsPanel.add(channelsBox);
        channelsAndFriendsPanel.add(Box.createRigidArea(new Dimension(1, 10)));
        Box friendsBox = Box.createHorizontalBox();
        friendsBox.add(new JLabel("Friends"));
        friendsBox.add(Box.createRigidArea(new Dimension(10, 1)));
        friendsBox.add(addFriendButton);
        friendsBox.add(Box.createHorizontalGlue());
        channelsAndFriendsPanel.add(friendsBox);
        channelsAndFriendsPanel.add(friendsList);

        messagesPane.setLayout(new BoxLayout(messagesPane, BoxLayout.PAGE_AXIS));
        messagesPane.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));
        messageEntryField.setBorder(BorderFactory.createEtchedBorder());
        chatPanel.setLayout(new BorderLayout());
        chatPanel.add(messagesScrollPane, BorderLayout.CENTER);
        Box messageEntryBox = Box.createHorizontalBox();
        messageEntryBox.add(Box.createRigidArea(new Dimension(2, 1)));
        messageEntryBox.add(messageEntryField);
        messageEntryBox.add(new JButton("Send"));
        chatPanel.add(messageEntryBox, BorderLayout.PAGE_END);

        pane.add(topPanel, BorderLayout.PAGE_START);
        pane.add(channelsAndFriendsPanelScrollPane, BorderLayout.LINE_START);
        pane.add(chatPanel, BorderLayout.CENTER);
    }

    public void start(String[] args) throws IOException {
        chat.setUserInterface(this);
        chat.start(args);
    }

    public static void main(String[] args) throws IOException {
        ChatFrame frame = new ChatFrame();
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(800, 600);
        frame.start(args);
        frame.setVisible(true);
    }

    @Override
    public void updatePlayer(LocalPlayer player) {
        this.player = player;
        playerName.setText(player.getDisplayName());
        if (player.isAuthenticated()) {
            guestLabel.setVisible(false);
            loginButton.setText("Logout");
        }
        else {
            guestLabel.setVisible(true);
            loginButton.setText("Login");
        }
    }

    void createChannel() {
        String name = (String)JOptionPane.showInputDialog(
                addChannelButton,
                "New channel name:",
                "Add Channel",
                JOptionPane.PLAIN_MESSAGE,
                null,
                null,
                "");
        if (name != null) {
            player.createSessionWithNameAsync(name).thenAccept(channel -> {
                // FIXME the new channel is returned, just update the UI incrementally
                updateChannels();
                updateMessages();
            });
        }
    }

    void joinChannel() {
        String sessionCode = (String)JOptionPane.showInputDialog(
                joinChannelButton,
                "Existing channel share code:",
                "Join Channel",
                JOptionPane.PLAIN_MESSAGE,
                null,
                null,
                "");
        if (sessionCode != null) {
            player.joinSessionWithCodeAsync(sessionCode).thenAccept(channel -> {
                // FIXME the new channel is returned, just update the UI incrementally
                updateChannels();
                updateMessages();
            });
        }
    }

    void addFriend() {
        String friendCode = (String)JOptionPane.showInputDialog(
                addFriendButton,
                "Friend code:",
                "Add Friend",
                JOptionPane.PLAIN_MESSAGE,
                null,
                null,
                "");
        if (friendCode != null) {
            player.addFriendWithCodeAsync(friendCode).thenAccept(friend -> {
                updateFriends();
            });
        }
    }

    @Override
    public void updateChannels() {
        player.fetchSessionsAsync().thenAccept(sessions -> {
            channelsListModel.clear();
            for (Session session : sessions) {
                channelsListModel.addElement(session);
            }
        });
    }

    @Override
    public void updateFriends() {
        player.fetchFriendsAsync().thenAccept(friends -> {
            friendsListModel.clear();
            for (Friend friend : friends) {
                friendsListModel.addElement(friend);
            }
        });
    }

    private void updateMessagesFromResponse(MessagesResponse response) {
        messagesPane.removeAll();
        String lastDisplayName = "";
        for (MessagesResponse.Message m : response.getMessages()) {
            JLabel message = new JLabel(m.getMessage());

            String displayName = m.getSender();
            boolean isMe = player.getDisplayName().equals(displayName);

            if (!displayName.equals(lastDisplayName)) {
                lastDisplayName = displayName;

                JComponent senderBox = Box.createHorizontalBox();
                JLabel sender = new JLabel((isMe ? "Me" : m.getSender()) + ":");
                sender.setForeground(Color.LIGHT_GRAY);
                if (isMe) {
                    senderBox.add(Box.createHorizontalGlue());
                }
                senderBox.add(sender);
                if (!isMe) {
                    senderBox.add(Box.createHorizontalGlue());
                }
                messagesPane.add(senderBox);
            }
            JComponent box = Box.createHorizontalBox();
            if (isMe) {
                box.add(Box.createHorizontalGlue());
                box.add(message);
            }
            else {
                box.add(Box.createRigidArea(new Dimension(5, 1)));
                box.add(message);
                box.add(Box.createHorizontalGlue());
            }
            messagesPane.add(box);
        }
        messagesPane.validate();
        messagesScrollPane.validate();
    }

    @Override
    public void updateMessages() {
        if (localSession == null) {
            messageEntryField.setEnabled(false);
            return;
        }
        messageEntryField.setEnabled(true);

        localSession.fetchJSONDataIntoAsync(new MessagesResponse()).thenAccept(r -> {
            SwingUtilities.invokeLater(() -> {
                updateMessagesFromResponse(r);
            });
        });
    }

    public void sendMessage(String message) {
        if (localSession == null) {
            return;
        }

        MessagesResponse response = new MessagesResponse();
        localSession.fetchJSONDataIntoAsync(response).thenAccept(r -> {
            MessagesResponse.Message m = new MessagesResponse.Message();
            m.setMessage(message);
            m.setSender(player.getDisplayName());
            r.getMessages().add(m);
            SwingUtilities.invokeLater(() -> {
                updateMessagesFromResponse(r);
                JScrollBar sb = messagesScrollPane.getVerticalScrollBar();
                sb.setValue(sb.getMaximum());
            });
            localSession.sendJSONDataAsync(response);
        });
    }
}
