import Foundation

// MARK: - API Configuration

/// Centralized API configuration for the Dravya backend.
///
/// # Networking Notes
///
/// ## iOS Simulator
/// `localhost` refers to the Mac running the simulator, so
/// `http://localhost:8000/api` works out of the box when the
/// backend is running locally.
///
/// ## Physical iPhone
/// `localhost` refers to the iPhone itself. To reach the Mac's
/// backend, use the Mac's LAN IP address instead:
///
///     http://192.168.x.x:8000/api
///
/// Both the iPhone and Mac **must be on the same Wi-Fi network**.
///
/// Find the Mac's IP:
///   System Settings → Wi-Fi → Details → IP Address
///
/// ## Backend CORS
/// Native iOS `URLSession` requests do not include an `Origin`
/// header, so the backend's CORS middleware does not apply.
/// No backend changes are required for the iOS app.
enum APIConfiguration {
    
    // MARK: - Environment
    
    /// Deployment environment for the application.
    enum Environment {
        case development
        case staging
        case production
        
        var baseURL: String {
            switch self {
            case .development:
                // iOS Simulator: localhost reaches the Mac.
                // Physical device: replace with your Mac's LAN IP.
                //
                // To use a LAN IP, change this to:
                //   return "http://192.168.x.x:8000/api"
                // where x.x is your Mac's actual LAN address.
                return "http://localhost:8000/api"
            case .staging:
                // TODO: Configure staging URL when available
                return "https://staging-api.dravya.in/api"
            case .production:
                // TODO: Configure production URL when available
                return "https://api.dravya.in/api"
            }
        }
    }
    
    // MARK: - Current Configuration
    
    /// The active environment. Change this to switch API targets.
    /// In a production workflow, this would be driven by build
    /// configurations (Debug vs Release) or xcconfig files.
    static let currentEnvironment: Environment = .development
    
    /// The base URL for all API requests.
    static var baseURL: String {
        currentEnvironment.baseURL
    }
    
    // MARK: - Endpoints
    
    /// Builds a full URL string for the given API path.
    ///
    /// - Parameter path: Relative path without leading slash.
    ///   Example: `"auth/login"` → `"http://localhost:8000/api/auth/login"`
    static func url(for path: String) -> String {
        "\(baseURL)/\(path)"
    }
    
    // MARK: - Well-Known Endpoints
    
    /// Health check endpoint. Returns `{ status, timestamp, service }`.
    static let healthEndpoint = "health"
    
    /// Login endpoint. POST with `{ email, password }`.
    static let loginEndpoint = "auth/login"
    
    /// Registration endpoint. POST with `{ name, email, password, role, organization, phone }`.
    static let registerEndpoint = "auth/register"
    
    /// Current user profile. GET with Authorization header.
    static let meEndpoint = "auth/me"
}
