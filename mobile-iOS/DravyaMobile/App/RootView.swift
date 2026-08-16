import SwiftUI

// MARK: - Root View

/// The main entry point view that handles authentication routing.
///
/// Displays `LoginView` if the user is not authenticated.
/// Displays a placeholder authenticated view if the user is logged in.
struct RootView: View {
    @EnvironmentObject private var authManager: AuthManager
    @State private var showSplash = true
    
    var body: some View {
        Group {
            if showSplash {
                SplashView()
                    .transition(.opacity)
            } else if authManager.isAuthenticated {
                authenticatedPlaceholder
            } else {
                LoginView()
            }
        }
        .animation(.default, value: showSplash)
        .animation(.default, value: authManager.isAuthenticated)
        .onAppear {
            DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                withAnimation {
                    showSplash = false
                }
            }
        }
    }
    
    private var authenticatedPlaceholder: some View {
        VStack(spacing: 24) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 60))
                .foregroundStyle(AppTheme.Colors.primary)
            
            VStack(spacing: 8) {
                if let user = authManager.currentUser {
                    Text("Welcome, \(user.name)")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("Role: \(user.role.displayName)")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                } else {
                    Text("Authenticated successfully.")
                        .font(.title2)
                        .fontWeight(.bold)
                }
            }
            
            Button("Logout") {
                authManager.logout()
            }
            .buttonStyle(.borderedProminent)
            .tint(.red)
            .padding(.top, 40)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(AppTheme.Colors.background.ignoresSafeArea())
    }
}

#Preview {
    RootView()
        .environmentObject(AuthManager())
}

