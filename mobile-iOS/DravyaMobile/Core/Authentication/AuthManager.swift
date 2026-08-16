import Foundation
import Combine

// MARK: - Auth Manager

/// Application-level authentication state manager.
///
/// Responsibilities:
/// - Maintains `isAuthenticated` and `currentUser` as published state
/// - Stores/retrieves JWT through `KeychainManager`
/// - Connects to `APIClient` as a token provider
/// - Handles login, logout, and session restoration
///
/// Injected into the SwiftUI environment by `DravyaMobileApp`.
@MainActor
final class AuthManager: ObservableObject {
    
    // MARK: - Published State
    
    /// Whether the user is currently authenticated.
    @Published private(set) var isAuthenticated = false
    
    /// The currently authenticated user, or `nil` if not logged in.
    @Published private(set) var currentUser: User?
    
    /// The most recent authentication error, if any.
    @Published var authError: String?
    
    // MARK: - Private
    
    private let apiClient: APIClient
    
    // MARK: - Init
    
    init(apiClient: APIClient = .shared) {
        self.apiClient = apiClient
        
        // Wire up the API client's token provider
        self.apiClient.tokenProvider = { [weak self] in
            self?.token
        }
        
        // Restore session from Keychain
        restoreSession()
    }
    
    // MARK: - Token Access
    
    /// The current JWT token from the Keychain.
    /// Used by `APIClient` for Authorization headers.
    var token: String? {
        KeychainManager.getToken()
    }
    
    // MARK: - Login
    
    /// Authenticates with the Dravya backend.
    ///
    /// On success, stores the JWT in the Keychain and updates
    /// `isAuthenticated` and `currentUser`.
    ///
    /// - Parameters:
    ///   - email: The user's email address.
    ///   - password: The user's password.
    func login(email: String, password: String) async {
        authError = nil
        
        do {
            let response = try await AuthService.login(
                email: email,
                password: password,
                apiClient: apiClient
            )
            
            // Store token securely
            try KeychainManager.saveToken(response.token)
            
            // Update state
            currentUser = response.user
            isAuthenticated = true
        } catch let error as APIError {
            authError = error.localizedDescription
            isAuthenticated = false
            currentUser = nil
        } catch {
            authError = "An unexpected error occurred."
            isAuthenticated = false
            currentUser = nil
        }
    }
    
    // MARK: - Register
    
    /// Registers a new user and authenticates them.
    ///
    /// On success, stores the JWT in the Keychain and updates
    /// `isAuthenticated` and `currentUser`.
    ///
    /// - Parameter request: The registration payload.
    func register(request: RegistrationRequest) async {
        authError = nil
        
        do {
            let response = try await AuthService.register(
                request: request,
                apiClient: apiClient
            )
            
            // Store token securely
            try KeychainManager.saveToken(response.token)
            
            // Update state
            currentUser = response.user
            isAuthenticated = true
        } catch let error as APIError {
            authError = error.localizedDescription
            isAuthenticated = false
            currentUser = nil
        } catch {
            authError = "An unexpected error occurred."
            isAuthenticated = false
            currentUser = nil
        }
    }
    
    // MARK: - Logout
    
    /// Clears the stored JWT and resets authentication state.
    func logout() {
        try? KeychainManager.deleteToken()
        isAuthenticated = false
        currentUser = nil
        authError = nil
    }
    
    // MARK: - Session Restoration
    
    /// Checks the Keychain for an existing JWT on app launch.
    ///
    /// If a token exists, attempts to validate it by calling
    /// `GET /api/auth/me`. If the token is expired or invalid,
    /// the session is cleared.
    func restoreSession() {
        guard KeychainManager.hasToken else {
            isAuthenticated = false
            currentUser = nil
            return
        }
        
        // Mark as tentatively authenticated while we validate
        isAuthenticated = true
        
        Task {
            do {
                let user = try await AuthService.getMe(apiClient: apiClient)
                currentUser = user
                isAuthenticated = true
            } catch {
                // Token is invalid or expired — clear session
                logout()
            }
        }
    }
}
