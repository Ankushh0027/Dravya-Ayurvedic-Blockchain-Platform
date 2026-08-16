import Foundation

// MARK: - Auth Service

/// Service layer for authentication API calls.
///
/// Matches the exact request/response schema of the Dravya backend:
///
///   POST /api/auth/login
///     Request:  { "email": "...", "password": "..." }
///     Response: { "success": true, "message": "...", "data": { "user": {...}, "token": "..." } }
///
///   GET /api/auth/me
///     Headers:  Authorization: Bearer <JWT>
///     Response: { "success": true, "message": "...", "data": { "user": {...} } }
///
/// Verified against:
///   - server/src/routes/auth.routes.ts
///   - server/src/controllers/auth.controller.ts
///   - server/src/lib/validators.ts (loginSchema)
///   - server/src/lib/response.ts (sendSuccess / sendError)
enum AuthService {
    
    // MARK: - Login
    
    /// Authenticates a user with email and password.
    ///
    /// - Parameters:
    ///   - email: The user's email address.
    ///   - password: The user's password.
    ///   - apiClient: The API client to use (defaults to shared).
    /// - Returns: A `LoginResponseData` containing the user and JWT token.
    /// - Throws: `APIError` on network, decoding, or authentication failures.
    static func login(
        email: String,
        password: String,
        apiClient: APIClient = .shared
    ) async throws -> LoginResponseData {
        let body = LoginRequest(email: email, password: password)
        
        let response: APIResponse<LoginResponseData> = try await apiClient.post(
            APIConfiguration.loginEndpoint,
            body: body
        )
        
        guard response.success, let data = response.data else {
            throw APIError.apiError(message: response.message)
        }
        
        return data
    }
    
    // MARK: - Register
    
    /// Registers a new user and authenticates them.
    ///
    /// - Parameters:
    ///   - request: The registration payload containing name, email, password, etc.
    ///   - apiClient: The API client to use (defaults to shared).
    /// - Returns: A `LoginResponseData` containing the newly created user and JWT token.
    /// - Throws: `APIError` on network, decoding, or validation failures.
    static func register(
        request: RegistrationRequest,
        apiClient: APIClient = .shared
    ) async throws -> LoginResponseData {
        let response: APIResponse<LoginResponseData> = try await apiClient.post(
            APIConfiguration.registerEndpoint,
            body: request
        )
        
        guard response.success, let data = response.data else {
            throw APIError.apiError(message: response.message)
        }
        
        return data
    }
    
    
    // MARK: - Get Current User
    
    /// Retrieves the currently authenticated user's profile.
    ///
    /// Requires a valid JWT in the Keychain (provided by `APIClient`'s
    /// `tokenProvider`).
    ///
    /// - Parameter apiClient: The API client to use (defaults to shared).
    /// - Returns: The authenticated `User`.
    /// - Throws: `APIError` on network, decoding, or authentication failures.
    static func getMe(apiClient: APIClient = .shared) async throws -> User {
        let response: APIResponse<MeResponseData> = try await apiClient.get(
            APIConfiguration.meEndpoint
        )
        
        guard response.success, let data = response.data else {
            throw APIError.apiError(message: response.message)
        }
        
        return data.user
    }
}

// MARK: - Request Models

/// Request body for `POST /api/auth/login`.
///
/// Matches the backend's `loginSchema` (Zod):
///   email: z.string().email()
///   password: z.string().min(1)
struct LoginRequest: Encodable {
    let email: String
    let password: String
}

/// Request body for `POST /api/auth/register`.
///
/// Matches the backend's `registerSchema` (Zod).
struct RegistrationRequest: Encodable {
    let name: String
    let email: String
    let password: String
    let role: String?
    let organization: String?
    let phone: String?
}
