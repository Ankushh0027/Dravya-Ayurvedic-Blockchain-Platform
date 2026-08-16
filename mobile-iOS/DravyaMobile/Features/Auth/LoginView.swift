import SwiftUI

struct LoginView: View {
    @EnvironmentObject private var authManager: AuthManager

    @State private var email = ""
    @State private var password = ""
    @State private var isLoggingIn = false
    @State private var errorMessage: String?

    @FocusState private var focusedField: Field?

    enum Field {
        case email
        case password
    }

    private var isFormValid: Bool {
        !email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !password.isEmpty &&
        email.contains("@")
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 32) {
                    // Header
                    VStack(spacing: 12) {
                        Image(systemName: "leaf.fill")
                            .font(.system(size: 60))
                            .foregroundStyle(AppTheme.Colors.primary)
                            .accessibilityHidden(true)

                        Text("Welcome to Dravya")
                            .font(.title)
                            .fontWeight(.bold)

                        Text("Traceability you can trust.")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.top, 60)
                    .padding(.bottom, 20)

                    // Form Fields
                    VStack(spacing: 20) {
                        AuthTextField(
                            title: "Email",
                            text: $email,
                            keyboardType: .emailAddress,
                            textInputAutocapitalization: .never
                        )
                        .textContentType(.username)
                        .autocorrectionDisabled()
                        .focused($focusedField, equals: .email)
                        .onSubmit { focusedField = .password }
                        .submitLabel(.next)

                        AuthTextField(
                            title: "Password",
                            text: $password,
                            isSecure: true
                        )
                        .textContentType(.password)
                        .focused($focusedField, equals: .password)
                        .onSubmit {
                            if isFormValid { performLogin() }
                        }
                        .submitLabel(.done)

                        
                        
                    }
                    .disabled(isLoggingIn)

                    // Error Message
                    if let errorMessage {
                        HStack(alignment: .top, spacing: 8) {
                            Image(systemName: "exclamationmark.triangle.fill")
                            Text(errorMessage)
                        }
                        .font(.footnote)
                        .foregroundStyle(.red)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal, 4)
                        .accessibilityElement(children: .combine)
                        .transition(.opacity.combined(with: .move(edge: .top)))
                    }

                    // Login Button
                    Button {
                        performLogin()
                    } label: {
                        HStack {
                            if isLoggingIn {
                                ProgressView()
                                    .tint(.white)
                                    .padding(.trailing, 8)
                                Text("Logging in...")
                            } else {
                                Text("Login")
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(isFormValid && !isLoggingIn ? AppTheme.Colors.primary : Color.gray.opacity(0.3))
                        .foregroundStyle(.white)
                        .font(.headline)
                        .clipShape(RoundedRectangle(cornerRadius: AppTheme.Layout.cornerRadius))
                    }
                    .disabled(!isFormValid || isLoggingIn)
                    .accessibilityLabel("Login")
                    .accessibilityHint(isFormValid ? "Double tap to log in" : "Enter email and password to log in")

                    // Registration Hint
                    NavigationLink(destination: RegistrationView()) {
                        Text("Don't have an account? Create one")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                            .multilineTextAlignment(.center)
                            .padding(.top, 20)
                    }
                    .disabled(isLoggingIn)
                }
                .padding(.horizontal, 24)
                .animation(.easeInOut(duration: 0.2), value: errorMessage)
            }
            .background(AppTheme.Colors.background.ignoresSafeArea())
            .scrollBounceBehavior(.basedOnSize)
            .scrollDismissesKeyboard(.interactively)
            .toolbar {
                ToolbarItemGroup(placement: .keyboard) {
                    Spacer()
                    Button("Done") { focusedField = nil }
                }
            }
            .onChange(of: email) { _ in clearError() }
            .onChange(of: password) { _ in clearError() }
            .onReceive(authManager.$authError) { error in
                if let error {
                    errorMessage = error
                    isLoggingIn = false
                    UIAccessibility.post(notification: .announcement, argument: error)
                    UINotificationFeedbackGenerator().notificationOccurred(.error)
                }
            }
        }
    }

    private func performLogin() {
        focusedField = nil
        errorMessage = nil
        isLoggingIn = true

        Task {
            await authManager.login(email: email, password: password)
            // Note: We don't need to set isLoggingIn = false on success because
            // RootView will transition away from LoginView.
            // On failure, authError will be published and caught by onReceive.
        }
    }

    private func clearError() {
        if errorMessage != nil {
            errorMessage = nil
        }
        if authManager.authError != nil {
            authManager.authError = nil
        }
    }
}

#Preview {
    LoginView()
        .environmentObject(AuthManager())
}