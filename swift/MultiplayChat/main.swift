//
//  File.swift
//  
//
//  Created by Domenico Porcino on 1/1/21.
//

// Run any SwiftUI view as a Mac app.

import Cocoa
import SwiftUI
@testable import Multiplay

struct User : Hashable {
    var name: String
    var avatar: String
    var isCurrentUser: Bool = false
}

struct Message : Hashable {
    static func == (lhs: Message, rhs: Message) -> Bool {
        return lhs.content == rhs.content && lhs.user.name == rhs.user.name
    }
    
    var content: String
    var user: User
}

struct ContentMessageView: View {
    var contentMessage: String
    var isCurrentUser: Bool
    
    var body: some View {
        Text(contentMessage)
            .padding(10)
            .foregroundColor(isCurrentUser ? Color.white : Color.black)
            .background(isCurrentUser ? Color.blue : Color.green)
            .cornerRadius(10)
    }
}

struct MessageView : View {
    var currentMessage: Message
    var body: some View {
        HStack(alignment: .bottom, spacing: 15) {
            if !currentMessage.user.isCurrentUser {
                Image(currentMessage.user.avatar)
                .resizable()
                .frame(width: 40, height: 40, alignment: .center)
                .cornerRadius(20)
            } else {
                Spacer()
            }
            ContentMessageView(contentMessage: currentMessage.content,
                               isCurrentUser: currentMessage.user.isCurrentUser)
        }
    }
}

struct ChannelView : View {
    var channel: String
    var shareCode: String
    var friends: [String]
    
    var body: some View {
        HStack {
            Text(channel)
                .padding(10)
                .foregroundColor(Color.white)
                .background(Color.blue)
                .cornerRadius(10)
            Text(shareCode)
                .padding(10)
                .foregroundColor(Color.white)
                .background(Color.blue)
                .cornerRadius(10)
            Button("-> Clipboard", action: copyShareCode(code: shareCode))
        }
        HStack {
            Text("Friends: ")
                .padding(10)
                .foregroundColor(Color.white)
                .background(Color.blue)
            
            ForEach(friends, id: \.self) { friend in
                HStack {
                    Text(friend)
                }
            }
        }
    }
    
    func copyShareCode(code: String) ->() ->() {
        return {
            NSPasteboard.general.clearContents()
            NSPasteboard.general.setString(code, forType: .string)
        }
    }
}

struct ChatView: View {
    @State var ui_baseUrl: String = "http://multiplay.ludo.digital:12345"
    @State var ui_playerName: String = "Guest"
    @State var ui_friendCode: String = "???"
    @State var ui_currentMessage: String = "Type here"
    @State var ui_newChannel: String = "Chat_1"
    @State var ui_channelCode: String = "GSFPJBZS"

    @State var connection: Connection?
    @State var channels: [String] = []
    @State var channelSessions: [Session] = []
    @State var channelCodes: [String] = []
    
    @State var friends: [String] = [ "Foo", "Baz" ]

    var messages: [Message] = []

    init() {
    }
    
    func viewDidLoad()
    {
        print("yay")
    }
    
    var body: some View {
        VStack {
            HStack {
                Text("Multiplay Server: ")
                    .padding()
                    .frame(minHeight: CGFloat(30))

                // https://www.simpleswiftguide.com/swiftui-textfield-complete-tutorial/
                TextField("Server:", text: $ui_baseUrl, onEditingChanged:{ (changed) in
                    print("$baseUrl edited - \(changed)")
                }) {
                    self.connect()
                }
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: CGFloat(30))
            }
            HStack {
                Text("Name: ")
                    .padding()
                    .frame(minHeight: CGFloat(30))

                // https://www.simpleswiftguide.com/swiftui-textfield-complete-tutorial/
                TextField("Name:", text: $ui_playerName, onEditingChanged:{ (changed) in
                    print("$playerName edited - \(changed)")
                }) {
                    print("$playerName committed \(self.ui_playerName)")
                }
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: CGFloat(30))
            }
            HStack {
                Text("Friend Code: ")
                    .padding()
                    .frame(minHeight: CGFloat(30))

                TextField("FriendCode:", text: $ui_friendCode, onEditingChanged:{ (changed) in
                    print("$friendCode edited - \(changed)")
                }) {
                    print("$friendCode committed \(self.ui_friendCode)")
                }
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: CGFloat(30))
                
                Button("-> Clipboard", action: copyFriendCode(code: self.ui_friendCode))
            }
            Text("Channels:")
            List {
                ForEach(channelSessions, id: \.self) { channel in
                    HStack {
                        ChannelView(channel: channel.displayName!, shareCode: channel.shareCode!, friends: self.friends)
                        Button("View", action: activateChannel(name: channel.displayName!))
                    }
                }
            }
            HStack {
                Text("Add Channel: ")
                    .padding()
                    .frame(minHeight: CGFloat(30))

                TextField("Channel:", text: $ui_newChannel, onEditingChanged:{ (changed) in
                    print("$channelName edited - \(changed)")
                }) {
                    print("$channelName committed \(self.ui_newChannel)")
                    addChannel(name:self.ui_newChannel)
                }
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: CGFloat(30))
            }
            HStack {
                Text("Join Channel: ")
                    .padding()
                    .frame(minHeight: CGFloat(30))

                TextField("Channel:", text: $ui_channelCode, onEditingChanged:{ (changed) in
                    print("$channelCode edited - \(changed)")
                }) {
                    print("$channelCode committed \(self.ui_channelCode)")
                    joinChannel(name:self.ui_channelCode)
                }
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: CGFloat(30))
            }
            Text("Messages:")
            List {
                ForEach(messages, id: \.self) { msg in
                   MessageView(currentMessage: msg)
                 }
            }
            HStack {
                TextField("Message", text: $ui_currentMessage, onEditingChanged:{ (changed) in
                    print("$currentMessage edited - \(changed)")
                }) {
                    sendMessage()
                }
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: CGFloat(30))
                Button(action: sendMessage) {
                    Text("Send")
                 }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .onAppear() {
            self.connect()
        }
    }
    
    func sendMessage() {
        print("Sending: \(self.ui_currentMessage)")
    }
    
    func connect() {
        let gameUUID = UUID().uuidString
        let c : Connection? = Connection(gameUUID:gameUUID, baseUrl:ui_baseUrl)
        if c == nil { return }

        self.connection = c
        let _ = c!.connect()
        if let localPlayer = c!.login() {
            ui_playerName = localPlayer.displayName == nil ? "Guest" : localPlayer.displayName!
            ui_friendCode = localPlayer.friendCode == nil ? "???" : localPlayer.friendCode!
        }
    }
    
    func addChannel(name: String) {
        let index = channels.firstIndex(of: name)
        if index == nil {
            guard let connection = connection else { return }
            guard let player = connection.localPlayer else { return }
            guard let session = player.createSession(name: name) else { return }
            channelSessions.append(session)
            channels.append(name)
            channelCodes.append(session.shareCode!)
            
            friends = session.players
        }
    }
        
    func copyFriendCode(code: String) ->() ->() {
        return {
            NSPasteboard.general.clearContents()
            NSPasteboard.general.setString(code, forType: .string)
        }
    }

    func activateChannel(name: String) ->() ->() {
        return {
            guard let index = channels.firstIndex(of: name) else { return }
            let session = channelSessions[index]
        }
    }

    func joinChannel(name: String) {
        let index = channelCodes.firstIndex(of: name)
        if index != nil { return }
        guard let connection = connection else { return }
        guard let player = connection.localPlayer else { return }
        guard let session = player.joinSessionByShareCode(shareCode: name) else { return }
        channels.append(session.displayName!)
        channelSessions.append(session)
        channelCodes.append(name)
        
        friends = session.players
    }

}


NSApplication.shared.run {
    ChatView()
    .frame(maxWidth: .infinity, maxHeight: .infinity)
}

extension NSApplication {
    public func run<V: View>(@ViewBuilder view: () -> V) {
        let appDelegate = AppDelegate(view())
        NSApp.setActivationPolicy(.regular)
        mainMenu = customMenu
        delegate = appDelegate
        run()
    }
}

// Inspired by https://www.cocoawithlove.com/2010/09/minimalist-cocoa-programming.html

extension NSApplication {
    var customMenu: NSMenu {
        let appMenu = NSMenuItem()
        appMenu.submenu = NSMenu()
        let appName = ProcessInfo.processInfo.processName
        appMenu.submenu?.addItem(NSMenuItem(title: "About \(appName)", action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), keyEquivalent: ""))
        appMenu.submenu?.addItem(NSMenuItem.separator())
        let services = NSMenuItem(title: "Services", action: nil, keyEquivalent: "")
        self.servicesMenu = NSMenu()
        services.submenu = self.servicesMenu
        appMenu.submenu?.addItem(services)
        appMenu.submenu?.addItem(NSMenuItem.separator())
        appMenu.submenu?.addItem(NSMenuItem(title: "Hide \(appName)", action: #selector(NSApplication.hide(_:)), keyEquivalent: "h"))
        let hideOthers = NSMenuItem(title: "Hide Others", action: #selector(NSApplication.hideOtherApplications(_:)), keyEquivalent: "h")
        hideOthers.keyEquivalentModifierMask = [.command, .option]
        appMenu.submenu?.addItem(hideOthers)
        appMenu.submenu?.addItem(NSMenuItem(title: "Show All", action: #selector(NSApplication.unhideAllApplications(_:)), keyEquivalent: ""))
        appMenu.submenu?.addItem(NSMenuItem.separator())
        appMenu.submenu?.addItem(NSMenuItem(title: "Quit \(appName)", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
        
        let windowMenu = NSMenuItem()
        windowMenu.submenu = NSMenu(title: "Window")
        windowMenu.submenu?.addItem(NSMenuItem(title: "Minmize", action: #selector(NSWindow.miniaturize(_:)), keyEquivalent: "m"))
        windowMenu.submenu?.addItem(NSMenuItem(title: "Zoom", action: #selector(NSWindow.performZoom(_:)), keyEquivalent: ""))
        windowMenu.submenu?.addItem(NSMenuItem.separator())
        windowMenu.submenu?.addItem(NSMenuItem(title: "Show All", action: #selector(NSApplication.arrangeInFront(_:)), keyEquivalent: "m"))
        
        let mainMenu = NSMenu(title: "Main Menu")
        mainMenu.addItem(appMenu)
        mainMenu.addItem(windowMenu)
        return mainMenu
    }
}

class AppDelegate<V: View>: NSObject, NSApplicationDelegate, NSWindowDelegate {
    init(_ contentView: V) {
        self.contentView = contentView
    }
    var window: NSWindow!
    var hostingView: NSView?
    var contentView: V
    var chatView: ChatView?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 480, height: 300),
            styleMask: [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView],
            backing: .buffered, defer: false)
        window.center()
        window.setFrameAutosaveName("Main Window")
        hostingView = NSHostingView(rootView: contentView)
        window.contentView = hostingView
        window.makeKeyAndOrderFront(nil)
        window.delegate = self
        chatView = ChatView()
        NSApp.activate(ignoringOtherApps: true)
    }
}
