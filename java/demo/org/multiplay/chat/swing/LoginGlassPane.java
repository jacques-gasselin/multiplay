package org.multiplay.chat.swing;

import javax.swing.*;
import java.awt.*;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;

public class LoginGlassPane extends JPanel {

    private JLabel usernameLabel = new JLabel("username");
    private JLabel passwordLabel = new JLabel("password");

    private JTextField usernameField = new JTextField();
    private JPasswordField passwordField = new JPasswordField();

    private JButton cancelButton = new JButton("Cancel");
    private JButton okButton = new JButton("OK");

    private volatile int option = JOptionPane.DEFAULT_OPTION;

    private LoginGlassPane(boolean inDialog) {

        if (inDialog) {
            setLayout(new BorderLayout(10, 10));
            setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        }
        else {
            setLayout(new BorderLayout(20, 20));
            setBorder(BorderFactory.createEmptyBorder(80, 80, 80, 80));
        }

        JComponent usernameBox = Box.createHorizontalBox();
        JComponent passwordBox = Box.createHorizontalBox();

        usernameLabel.setHorizontalAlignment(SwingConstants.RIGHT);
        passwordLabel.setHorizontalAlignment(SwingConstants.RIGHT);

        usernameField.setPreferredSize(new Dimension(100, 20));
        usernameField.setMaximumSize(new Dimension(300, 32));
        usernameField.addKeyListener(new KeyAdapter() {
            @Override
            public void keyTyped(KeyEvent e) {
                super.keyTyped(e);
                updateButtons();
            }
        });

        passwordField.setPreferredSize(new Dimension(100, 20));
        passwordField.setMaximumSize(new Dimension(300, 32));
        passwordField.addKeyListener(new KeyAdapter() {
            @Override
            public void keyTyped(KeyEvent e) {
                super.keyTyped(e);
                updateButtons();
            }
        });

        usernameBox.add(usernameLabel);
        usernameBox.add(Box.createRigidArea(new Dimension(5, 1)));
        usernameBox.add(usernameField);

        passwordBox.add(passwordLabel);
        passwordBox.add(Box.createRigidArea(new Dimension(5, 1)));
        passwordBox.add(passwordField);

        JComponent vbox = Box.createVerticalBox();
        vbox.add(Box.createVerticalGlue());
        vbox.add(usernameBox);
        vbox.add(Box.createRigidArea(new Dimension(1, 10)));
        vbox.add(passwordBox);
        vbox.add(Box.createVerticalGlue());

        add(vbox, BorderLayout.CENTER);

        JComponent buttonBox = Box.createHorizontalBox();
        buttonBox.add(Box.createHorizontalGlue());
        buttonBox.add(okButton);
        buttonBox.add(Box.createRigidArea(new Dimension(10, 1)));
        buttonBox.add(cancelButton);

        add(buttonBox, BorderLayout.PAGE_END);

        okButton.addActionListener(event -> {
            synchronized (this) {
                option = JOptionPane.OK_OPTION;
                this.notify();
            }
        });
        cancelButton.addActionListener(event -> {
            synchronized (this) {
                option = JOptionPane.CANCEL_OPTION;
                this.notify();
            }
        });
    }

    private void updateButtons() {
        String username = usernameField.getText();
        char[] password = passwordField.getPassword();

        boolean isOKEnabled = username.length() > 0 && password.length > 0;
        okButton.setEnabled(isOKEnabled);
        JRootPane rootPane = SwingUtilities.getRootPane(this);
        if (rootPane != null) {
            if (isOKEnabled) {
                rootPane.setDefaultButton(okButton);
            } else {
                rootPane.setDefaultButton(cancelButton);
            }
        }
    }

    private float alpha = 0f;
    private float targetAlpha = 0.85f;
    private float alphaFilter = 0.0025f;

    @Override
    protected void paintComponent(Graphics _g) {
        Graphics2D g = (Graphics2D)_g;
        final Composite formerComposite = g.getComposite();

        AlphaComposite comp = AlphaComposite.SrcOver.derive(alpha);

        alpha = alpha * (1 - alphaFilter) + targetAlpha * alphaFilter;

        g.setComposite(comp);

        Rectangle clip = g.getClipBounds();
        g.setColor(getBackground());
        g.fillRect(clip.x, clip.y, clip.width, clip.height);

        g.setComposite(formerComposite);

        if (Math.abs(alpha - targetAlpha) > 0.001f) {
            repaint();
        }
    }

    public static CompletionStage<LoginGlassPane> showInputDialog(JFrame frame) {
        JDialog dialog = new JDialog(frame, "Login", true);

        final LoginGlassPane pane = new LoginGlassPane(true);

        dialog.add(pane);
        dialog.setMinimumSize(new Dimension(300, 200));

        dialog.pack();
        dialog.addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosed(WindowEvent e) {
                synchronized (pane) {
                    if (pane.option == JOptionPane.DEFAULT_OPTION) {
                        pane.option = JOptionPane.CANCEL_OPTION;
                        pane.notify();
                    }
                }
            }
        });

        return CompletableFuture.supplyAsync(() -> {
            SwingUtilities.invokeLater(() -> {
                pane.updateButtons();
                dialog.setVisible(true);
            });
            while (pane.option == JOptionPane.DEFAULT_OPTION) {
                try {
                    synchronized (pane) {
                        pane.wait();
                    }
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            dialog.setVisible(false);
            return pane;
        });
    }

    public static CompletionStage<LoginGlassPane> showInput(JFrame frame) {
        final LoginGlassPane pane = new LoginGlassPane(false);

        final Component formerGlassPane = frame.getGlassPane();
        frame.setGlassPane(pane);

        pane.setOpaque(false);
        pane.setSize(frame.getSize());
        pane.validate();

        return CompletableFuture.supplyAsync(() -> {
            SwingUtilities.invokeLater(() -> {
                pane.updateButtons();
                pane.setVisible(true);
            });

            while (pane.option == JOptionPane.DEFAULT_OPTION) {
                try {
                    synchronized (pane) {
                        pane.wait();
                    }
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            SwingUtilities.invokeLater(() -> {
                pane.setVisible(false);
                frame.setGlassPane(formerGlassPane);
            });
            return pane;
        });
    }

    public int getOption() {
        return option;
    }

    public String getUsername() {
        return usernameField.getText();
    }

    public String getPassword() {
        return String.copyValueOf(passwordField.getPassword());
    }
}
