import Foundation

// MARK: - User Role

/// Roles available in the Dravya platform.
///
/// Matches the Prisma `Role` enum defined in
/// `server/prisma/schema.prisma`:
///
///     enum Role {
///       ADMIN
///       PRODUCER
///       LAB
///       DISTRIBUTOR
///       VERIFICATION_AUTHORITY
///     }
///
/// Uses a custom `init(from:)` so that unknown future roles
/// decode as `.unknown` instead of crashing.
enum UserRole: String, Codable, CaseIterable {
    case admin = "ADMIN"
    case producer = "PRODUCER"
    case lab = "LAB"
    case distributor = "DISTRIBUTOR"
    case verificationAuthority = "VERIFICATION_AUTHORITY"
    
    /// Fallback for roles added to the backend in the future.
    case unknown = "UNKNOWN"
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)
        self = UserRole(rawValue: rawValue) ?? .unknown
    }
    
    /// Human-readable display name.
    var displayName: String {
        switch self {
        case .admin: return "Admin"
        case .producer: return "Producer"
        case .lab: return "Lab"
        case .distributor: return "Distributor"
        case .verificationAuthority: return "Verification Authority"
        case .unknown: return "Unknown"
        }
    }
}

// MARK: - User

/// Represents a Dravya platform user.
///
/// Matches the backend's `safeUserSelect` fields returned by
/// `auth.controller.ts`:
///
///     id, name, email, role, organization, phone, isActive
///
/// The `password`, `createdAt`, and `updatedAt` fields are
/// intentionally excluded — the backend never sends the password,
/// and timestamps are not needed in the initial mobile client.
struct User: Codable, Identifiable {
    let id: String
    let name: String
    let email: String
    let role: UserRole
    let organization: String?
    let phone: String?
    let isActive: Bool
}
