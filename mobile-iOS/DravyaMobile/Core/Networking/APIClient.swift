import Foundation

// MARK: - API Client

/// Lightweight generic API client for communicating with the Dravya backend.
///
/// Uses `URLSession` with `async/await`. All requests go through a single
/// entry point that handles:
/// - URL construction from `APIConfiguration.baseURL`
/// - JSON encoding of `Codable` request bodies
/// - JSON decoding of `APIResponse<T>` responses
/// - `Content-Type: application/json` header
/// - `Authorization: Bearer <JWT>` header when a token is available
/// - HTTP status code → `APIError` mapping
/// - Backend error message extraction
///
/// ## Usage
/// ```swift
/// let client = APIClient()
/// let response: APIResponse<LoginResponseData> = try await client.post(
///     "auth/login",
///     body: LoginRequest(email: "...", password: "...")
/// )
/// ```
final class APIClient {
    
    // MARK: - Properties
    
    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    
    /// Closure that provides the current JWT token.
    /// Set by `AuthManager` so the client stays decoupled from auth state.
    var tokenProvider: (() -> String?)?
    
    // MARK: - Singleton
    
    /// Shared instance used throughout the app.
    static let shared = APIClient()
    
    // MARK: - Init
    
    init(session: URLSession = .shared) {
        self.session = session
        self.decoder = JSONDecoder()
        self.encoder = JSONEncoder()
    }
    
    // MARK: - Public Methods
    
    /// Performs a GET request.
    func get<T: Decodable>(_ path: String) async throws -> T {
        try await request(path: path, method: "GET")
    }
    
    /// Performs a POST request with a JSON body.
    func post<T: Decodable, B: Encodable>(_ path: String, body: B) async throws -> T {
        try await request(path: path, method: "POST", body: body)
    }
    
    /// Performs a POST request without a body.
    func post<T: Decodable>(_ path: String) async throws -> T {
        try await request(path: path, method: "POST")
    }
    
    /// Performs a PUT request with a JSON body.
    func put<T: Decodable, B: Encodable>(_ path: String, body: B) async throws -> T {
        try await request(path: path, method: "PUT", body: body)
    }
    
    /// Performs a PATCH request with a JSON body.
    func patch<T: Decodable, B: Encodable>(_ path: String, body: B) async throws -> T {
        try await request(path: path, method: "PATCH", body: body)
    }
    
    /// Performs a DELETE request.
    func delete<T: Decodable>(_ path: String) async throws -> T {
        try await request(path: path, method: "DELETE")
    }
    
    // MARK: - Health Check
    
    /// Checks backend connectivity by calling `GET /api/health`.
    /// Returns `true` if the health endpoint responds with `status: "ok"`.
    func checkHealth() async -> Bool {
        do {
            let urlString = APIConfiguration.url(for: APIConfiguration.healthEndpoint)
            guard let url = URL(string: urlString) else { return false }
            
            var urlRequest = URLRequest(url: url)
            urlRequest.httpMethod = "GET"
            urlRequest.timeoutInterval = 5
            
            let (data, response) = try await session.data(for: urlRequest)
            
            guard let httpResponse = response as? HTTPURLResponse,
                  httpResponse.statusCode == 200 else {
                return false
            }
            
            let health = try decoder.decode(HealthCheckResponse.self, from: data)
            return health.status == "ok"
        } catch {
            return false
        }
    }
    
    // MARK: - Core Request Method
    
    private func request<T: Decodable>(
        path: String,
        method: String,
        body: (any Encodable)? = nil
    ) async throws -> T {
        // Build URL
        let urlString = APIConfiguration.url(for: path)
        guard let url = URL(string: urlString) else {
            throw APIError.invalidURL
        }
        
        // Build request
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = method
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("application/json", forHTTPHeaderField: "Accept")
        
        // Attach JWT if available
        if let token = tokenProvider?() {
            urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        // Encode body
        if let body = body {
            do {
                urlRequest.httpBody = try encoder.encode(body)
            } catch {
                throw APIError.decodingError(error)
            }
        }
        
        // Execute request
        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: urlRequest)
        } catch {
            throw APIError.networkError(error)
        }
        
        // Check HTTP status
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.unknown
        }
        
        // Handle error status codes
        switch httpResponse.statusCode {
        case 200...299:
            break // Success — continue to decode
        case 401:
            // Try to extract backend error message
            if let apiError = try? decoder.decode(APIErrorResponse.self, from: data) {
                throw APIError.apiError(message: apiError.message)
            }
            throw APIError.unauthorized
        case 403:
            if let apiError = try? decoder.decode(APIErrorResponse.self, from: data) {
                throw APIError.apiError(message: apiError.message)
            }
            throw APIError.forbidden
        case 404:
            throw APIError.notFound
        case 400, 409, 422:
            // Client errors — extract backend message
            if let apiError = try? decoder.decode(APIErrorResponse.self, from: data) {
                throw APIError.apiError(message: apiError.message)
            }
            throw APIError.unknown
        case 500...599:
            throw APIError.serverError(statusCode: httpResponse.statusCode)
        default:
            throw APIError.unknown
        }
        
        // Decode response
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingError(error)
        }
    }
}

// MARK: - Backend Error Response

/// Minimal model to extract error messages from the backend's
/// `{ "success": false, "message": "..." }` responses.
private struct APIErrorResponse: Decodable {
    let success: Bool
    let message: String
}
