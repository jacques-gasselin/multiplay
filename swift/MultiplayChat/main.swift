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

struct ChatView: View {
    @State var playerName: String = "Guest"
    @State var friendCode: String = "???"

    init() {
    }
    
    func viewDidLoad()
    {
        print("yay")
    }
    
    var body: some View {
        VStack {
            HStack {
                Text("Name: ")
                    .padding()
                    .background(Capsule().fill(Color.blue))
                    .padding()
                    .frame(minHeight: CGFloat(30))

                // https://www.simpleswiftguide.com/swiftui-textfield-complete-tutorial/
                TextField("Player Name:", text: $playerName, onEditingChanged:{ (changed) in
                    print("$playerName changed - \(changed)")
                }) {
                    print("$playerName committed \(playerName)")
                }
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: CGFloat(30))

                TextField("FriendCode:", text: $friendCode, onEditingChanged:{ (changed) in
                    print("$friendCode changed - \(changed)")
                }) {
                    print("$friendCode committed \(friendCode)")
                }
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(minHeight: CGFloat(30))
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .onAppear() {
            let gameUUID = UUID().uuidString
            let baseUrl = "http://localhost:12345"
            let connection = MPConnection(gameUUID:gameUUID, baseUrl:baseUrl)
            let _ = connection.connect()
            if let localPlayer = connection.login() {
                playerName = localPlayer.displayName == nil ? "Guest" : localPlayer.displayName!
                friendCode = localPlayer.friendCode == nil ? "???" : localPlayer.friendCode!
            }
        }
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
