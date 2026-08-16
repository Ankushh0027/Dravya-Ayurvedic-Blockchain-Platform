import Foundation

// MARK: - API Response

/// Generic wrapper for the Dravya backend's standard response format.
///
/// The backend consistently returns:
/// ```json
/// {
///     "success": true,
///     "message": "...",
///     "data": { ... }
/// }
/// ```
///
/// On error:
/// ```json
/// {
///     "success": false,
///     "message": "..."
/// }
/// ```
///
/// `T` is the type of the `data` payload, which varies by endpoint.
struct APIResponse<T: Decodable>: Decodable {
    let success: Bool
    let message: String
    let data: T?
}

// MARK: - Health Check Response

/// Response from `GET /api/health`.
struct HealthCheckResponse: Decodable {
    let status: String
    let timestamp: String
    let service: String
}

// MARK: - Login Response Data

/// The `data` payload returned by `POST /api/auth/login`.
struct LoginResponseData: Decodable {
    let user: User
    let token: String
}

// MARK: - Me Response Data

/// The `data` payload returned by `GET /api/auth/me`.
struct MeResponseData: Decodable {
    let user: User
}
