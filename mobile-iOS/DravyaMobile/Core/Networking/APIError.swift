import Foundation

// MARK: - API Error

/// Typed errors for API client operations.
///
/// Maps HTTP status codes and networking failures to specific cases,
/// allowing Views and Services to handle errors appropriately without
/// exposing raw backend details to users.
enum APIError: Error, LocalizedError {
    
    /// The constructed URL was invalid.
    case invalidURL
    
    /// A network-level failure (no connectivity, timeout, DNS, etc.).
    case networkError(Error)
    
    /// HTTP 401 — the JWT is missing, expired, or invalid.
    case unauthorized
    
    /// HTTP 403 — the user does not have permission for this action.
    case forbidden
    
    /// HTTP 404 — the requested resource does not exist.
    case notFound
    
    /// HTTP 5xx — the backend encountered an internal error.
    case serverError(statusCode: Int)
    
    /// The response body could not be decoded into the expected type.
    case decodingError(Error)
    
    /// The backend returned `{ "success": false, "message": "..." }`.
    case apiError(message: String)
    
    /// An error that does not fit any other category.
    case unknown
    
    // MARK: - LocalizedError
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "The request URL is invalid."
        case .networkError:
            return "Unable to connect to the server. Please check your network connection."
        case .unauthorized:
            return "Your session has expired. Please log in again."
        case .forbidden:
            return "You do not have permission to perform this action."
        case .notFound:
            return "The requested resource was not found."
        case .serverError:
            return "The server encountered an error. Please try again later."
        case .decodingError:
            return "Received an unexpected response from the server."
        case .apiError(let message):
            return message
        case .unknown:
            return "An unexpected error occurred."
        }
    }
}
