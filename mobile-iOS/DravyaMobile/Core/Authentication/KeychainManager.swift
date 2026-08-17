import Foundation
import Security

// MARK: - Keychain Manager

/// Lightweight wrapper around Apple's Keychain Services for secure
/// JWT token storage.
///
/// Tokens are stored as `kSecClassGenericPassword` items, scoped to
/// the service identifier `com.dravya.mobile.auth`.
///
/// ## Security
/// - Tokens are encrypted at rest by the Secure Enclave.
/// - Never stored in UserDefaults, plain files, or source code.
/// - Automatically cleared on `deleteToken()` (logout).
enum KeychainManager {
    
    // MARK: - Constants
    
    private static let service = "com.dravya.mobile.auth"
    private static let tokenKey = "jwt_token"
    
    // MARK: - Save
    
    /// Stores a JWT token in the Keychain.
    ///
    /// If a token already exists, it is updated in place.
    ///
    /// - Parameter token: The JWT string to store.
    /// - Throws: `KeychainError` if the operation fails.
    @discardableResult
    static func saveToken(_ token: String) throws -> Bool {
        guard let data = token.data(using: .utf8) else {
            throw KeychainError.encodingFailed
        }
        
        // Try to update an existing item first
        let query = baseQuery()
        let attributes: [String: Any] = [
            kSecValueData as String: data
        ]
        
        let updateStatus = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        
        if updateStatus == errSecSuccess {
            return true
        }
        
        if updateStatus == errSecItemNotFound {
            // No existing item — add a new one
            var addQuery = baseQuery()
            addQuery[kSecValueData as String] = data
            addQuery[kSecAttrAccessible as String] = kSecAttrAccessibleWhenUnlockedThisDeviceOnly
            
            let addStatus = SecItemAdd(addQuery as CFDictionary, nil)
            guard addStatus == errSecSuccess else {
                throw KeychainError.saveFailed(status: addStatus)
            }
            return true
        }
        
        throw KeychainError.saveFailed(status: updateStatus)
    }
    
    // MARK: - Retrieve
    
    /// Retrieves the stored JWT token from the Keychain.
    ///
    /// - Returns: The JWT string, or `nil` if no token is stored.
    static func getToken() -> String? {
        var query = baseQuery()
        query[kSecReturnData as String] = kCFBooleanTrue
        query[kSecMatchLimit as String] = kSecMatchLimitOne
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data,
              let token = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        return token
    }
    
    // MARK: - Delete
    
    /// Removes the stored JWT token from the Keychain.
    ///
    /// - Throws: `KeychainError` if the deletion fails (ignores
    ///   `errSecItemNotFound` since there is nothing to delete).
    static func deleteToken() throws {
        let query = baseQuery()
        let status = SecItemDelete(query as CFDictionary)
        
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.deleteFailed(status: status)
        }
    }
    
    // MARK: - Check
    
    /// Whether a JWT token exists in the Keychain.
    static var hasToken: Bool {
        getToken() != nil
    }
    
    // MARK: - Private Helpers
    
    private static func baseQuery() -> [String: Any] {
        [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: tokenKey,
        ]
    }
}

// MARK: - Keychain Error

/// Errors specific to Keychain operations.
enum KeychainError: Error, LocalizedError {
    case encodingFailed
    case saveFailed(status: OSStatus)
    case deleteFailed(status: OSStatus)
    
    var errorDescription: String? {
        switch self {
        case .encodingFailed:
            return "Failed to encode the token for Keychain storage."
        case .saveFailed(let status):
            return "Failed to save token to Keychain (status: \(status))."
        case .deleteFailed(let status):
            return "Failed to delete token from Keychain (status: \(status))."
        }
    }
}
