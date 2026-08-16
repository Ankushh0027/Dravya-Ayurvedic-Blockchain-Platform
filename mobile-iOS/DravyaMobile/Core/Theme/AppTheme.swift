import SwiftUI

/// Centralized design system matching the Dravya web application's modern branding.
enum AppTheme {
    
    /// Color palette aligned with web `globals.css`
    enum Colors {
        /// Primary Dravya Green (derived from oklch(0.627 0.194 149.214))
        static let primary = Color(hex: "#15A34A")
        
        /// Secondary soft green/mint (matches web --ww and muted)
        static let secondary = Color(hex: "#E1E9E1")
        
        /// Background color supporting light/dark mode natively
        static let background = Color(UIColor.systemBackground)
        
        /// Standard text color
        static let foreground = Color(UIColor.label)
        
        /// Muted secondary text
        static let secondaryText = Color(UIColor.secondaryLabel)
    }
    
    /// Layout constants
    enum Layout {
        /// Standard component corner radius matching web 0.625rem
        static let cornerRadius: CGFloat = 10.0
        
        /// Standard outer padding
        static let padding: CGFloat = 24.0
    }
}

extension Color {
    /// Initialize Color from hex string
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
