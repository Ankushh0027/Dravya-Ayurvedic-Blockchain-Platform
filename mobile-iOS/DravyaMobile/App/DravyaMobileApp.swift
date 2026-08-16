import SwiftUI

// MARK: - App Entry Point

/// Dravya Mobile application entry point.
///
/// Uses the SwiftUI App lifecycle with `@main`.
/// Initializes `AuthManager` as application-level state and
/// injects it into the SwiftUI environment for all child views.
@main
struct DravyaMobileApp: App {
    
    @StateObject private var authManager = AuthManager()
    
    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(authManager)
        }
    }
}
