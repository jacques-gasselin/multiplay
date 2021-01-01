import XCTest
@testable import Multiplay

final class MultiplayTests: XCTestCase {

    func testLogin() {
        let gameUUID = UUID().uuidString
        let baseUrl = "http://localhost:12345"
        let connection = MPConnection(gameUUID:gameUUID, baseUrl:baseUrl)
        XCTAssertTrue(connection.connect())
        XCTAssertTrue(connection.isConnected)
        let localPlayer = connection.login()
        XCTAssertNotNil(localPlayer)
        XCTAssertTrue(connection.isLoggedIn)
//        XCTAssertTrue(localPlayer!.httpAuthenticate())
//        XCTAssertTrue(localPlayer!.authenticated)
        XCTAssertNotNil(localPlayer?.friendCode)
        
    }

    static var allTests = [
        ("test login", testLogin),
    ]
}
