import SwiftUI

/// A styled text field component for the authentication flow.
struct AuthTextField: View {
    let title: String
    @Binding var text: String
    var isSecure: Bool = false
    var keyboardType: UIKeyboardType = .default
    var textInputAutocapitalization: TextInputAutocapitalization? = nil
    
    @State private var isPasswordVisible: Bool = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundStyle(.secondary)
            
            HStack {
                if isSecure && !isPasswordVisible {
                    SecureField(title, text: $text)
                        .accessibilityLabel("\(title) Secure Field")
                } else {
                    TextField(title, text: $text)
                        .keyboardType(keyboardType)
                        .textInputAutocapitalization(textInputAutocapitalization)
                        .accessibilityLabel("\(title) Text Field")
                }
                
                if isSecure {
                    Button {
                        isPasswordVisible.toggle()
                    } label: {
                        Image(systemName: isPasswordVisible ? "eye.slash.fill" : "eye.fill")
                            .foregroundStyle(.secondary)
                            .accessibilityLabel(isPasswordVisible ? "Hide Password" : "Show Password")
                    }
                }
            }
            .padding()
            .background(AppTheme.Colors.secondary)
            .clipShape(RoundedRectangle(cornerRadius: AppTheme.Layout.cornerRadius))
            .overlay(
                RoundedRectangle(cornerRadius: AppTheme.Layout.cornerRadius)
                    .stroke(AppTheme.Colors.secondary, lineWidth: 1.5)
            )
        }
    }
}

#Preview {
    VStack(spacing: 20) {
        AuthTextField(title: "Email", text: .constant(""), keyboardType: .emailAddress, textInputAutocapitalization: .never)
        AuthTextField(title: "Password", text: .constant(""), isSecure: true)
    }
    .padding()
}
