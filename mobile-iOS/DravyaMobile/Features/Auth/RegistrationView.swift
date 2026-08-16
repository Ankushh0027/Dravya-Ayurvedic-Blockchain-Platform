import SwiftUI

struct RegistrationView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var authManager: AuthManager
    
    @State private var name = ""
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var role = "PRODUCER"
    @State private var organization = ""
    @State private var phone = ""
    
    @State private var isRegistering = false
    @State private var localError: String?
    
    @FocusState private var focusedField: Field?
    
    enum Field {
        case name, email, password, confirmPassword, organization, phone
    }
    
    let roles = ["PRODUCER", "LAB", "DISTRIBUTOR"]
    
    private var isFormValid: Bool {
        !name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        email.contains("@") &&
        password.count >= 8 &&
        password == confirmPassword
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 32) {
                // Header
                VStack(spacing: 12) {
                    Image(systemName: "leaf.fill")
                        .font(.system(size: 60))
                        .foregroundStyle(AppTheme.Colors.primary)
                        .accessibilityHidden(true)
                    
                    Text("Create your account")
                        .font(.title)
                        .fontWeight(.bold)
                    
                    Text("Join the Dravya network.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                .padding(.top, 20)
                .padding(.bottom, 20)
                
                // Form Fields
                // Form Fields
                VStack(spacing: 24) {
                    
                    // Role Selection
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Account Type")
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .foregroundStyle(.secondary)
                        
                        Picker("Role", selection: $role) {
                            ForEach(roles, id: \.self) { role in
                                Text(role.capitalized).tag(role)
                            }
                        }
                        .pickerStyle(.segmented)
                    }
                    
                    // Account Details
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Personal Information")
                            .font(.headline)
                            .foregroundStyle(AppTheme.Colors.primary)
                            .padding(.bottom, 4)
                        
                        AuthTextField(
                            title: "Full Name",
                            text: $name,
                            textInputAutocapitalization: .words
                        )
                        .focused($focusedField, equals: .name)
                        .onSubmit { focusedField = .email }
                        .submitLabel(.next)
                        
                        AuthTextField(
                            title: "Email",
                            text: $email,
                            keyboardType: .emailAddress,
                            textInputAutocapitalization: .never
                        )
                        .focused($focusedField, equals: .email)
                        .onSubmit { focusedField = .password }
                        .submitLabel(.next)
                        
                        AuthTextField(
                            title: "Password",
                            text: $password,
                            isSecure: true
                        )
                        .focused($focusedField, equals: .password)
                        .onSubmit { focusedField = .confirmPassword }
                        .submitLabel(.next)
                        
                        AuthTextField(
                            title: "Confirm Password",
                            text: $confirmPassword,
                            isSecure: true
                        )
                        .focused($focusedField, equals: .confirmPassword)
                        .onSubmit { focusedField = .organization }
                        .submitLabel(.next)
                    }
                    .padding()
                    .background(Color(UIColor.secondarySystemBackground).opacity(0.5))
                    .clipShape(RoundedRectangle(cornerRadius: AppTheme.Layout.cornerRadius))
                    
                    // Additional Details
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Additional Details")
                            .font(.headline)
                            .foregroundStyle(AppTheme.Colors.primary)
                            .padding(.bottom, 4)
                        
                        AuthTextField(
                            title: "Organization (Optional)",
                            text: $organization,
                            textInputAutocapitalization: .words
                        )
                        .focused($focusedField, equals: .organization)
                        .onSubmit { focusedField = .phone }
                        .submitLabel(.next)
                        
                        AuthTextField(
                            title: "Phone (Optional)",
                            text: $phone,
                            keyboardType: .phonePad
                        )
                        .focused($focusedField, equals: .phone)
                        .onSubmit { focusedField = nil }
                        .submitLabel(.done)
                    }
                    .padding()
                    .background(Color(UIColor.secondarySystemBackground).opacity(0.5))
                    .clipShape(RoundedRectangle(cornerRadius: AppTheme.Layout.cornerRadius))
                }
                
                // Error Message
                if let errorMessage = localError ?? authManager.authError {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                        Text(errorMessage)
                    }
                    .font(.footnote)
                    .foregroundStyle(.red)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 4)
                }
                
                // Submit Button
                Button {
                    performRegistration()
                } label: {
                    HStack {
                        if isRegistering {
                            ProgressView()
                                .tint(.white)
                                .padding(.trailing, 8)
                            Text("Creating Account...")
                        } else {
                            Text("Create Account")
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(isFormValid && !isRegistering ? AppTheme.Colors.primary : Color.gray.opacity(0.3))
                    .foregroundStyle(.white)
                    .font(.headline)
                    .clipShape(RoundedRectangle(cornerRadius: AppTheme.Layout.cornerRadius))
                }
                .disabled(!isFormValid || isRegistering)
                .accessibilityLabel("Create Account")
                
                // Login Hint
                Button {
                    dismiss()
                } label: {
                    Text("Already have an account? Login")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                        .padding(.top, 20)
                }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 40)
        }
        .background(AppTheme.Colors.background.ignoresSafeArea())
        .scrollBounceBehavior(.basedOnSize)
        .navigationBarHidden(true)
        .onChange(of: name) { _ in clearError() }
        .onChange(of: email) { _ in clearError() }
        .onChange(of: password) { _ in clearError() }
        .onChange(of: confirmPassword) { _ in clearError() }
        .onReceive(authManager.$authError) { error in
            if let error {
                self.localError = error
                self.isRegistering = false
            }
        }
    }
    
    private func performRegistration() {
        focusedField = nil
        localError = nil
        
        // Client-side validation for password rules
        let passwordRegex = "^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$"
        if password.range(of: passwordRegex, options: .regularExpression) == nil {
            localError = "Password must be at least 8 characters and include uppercase, lowercase, and a number."
            return
        }
        
        isRegistering = true
        
        let req = RegistrationRequest(
            name: name.trimmingCharacters(in: .whitespacesAndNewlines),
            email: email.trimmingCharacters(in: .whitespacesAndNewlines),
            password: password,
            role: role,
            organization: organization.isEmpty ? nil : organization.trimmingCharacters(in: .whitespacesAndNewlines),
            phone: phone.isEmpty ? nil : phone.trimmingCharacters(in: .whitespacesAndNewlines)
        )
        
        Task {
            await authManager.register(request: req)
        }
    }
    
    private func clearError() {
        if localError != nil {
            localError = nil
        }
        if authManager.authError != nil {
            authManager.authError = nil
        }
    }
}

#Preview {
    RegistrationView()
        .environmentObject(AuthManager())
}
