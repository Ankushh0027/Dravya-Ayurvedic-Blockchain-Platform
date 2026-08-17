# Dravya Mobile (iOS Prototype)

This is the foundational iOS application for the Dravya platform, targeting the first-round SIH submission.

## Architecture

The mobile application acts purely as a presentation layer. It communicates with the existing Express backend and does not interact directly with PostgreSQL, Prisma, or Hyperledger Fabric. All business logic, role-based access control (RBAC), and blockchain transactions remain managed by the centralized backend.

**Flow:** iOS App → REST API → Backend Services → PostgreSQL / Fabric

## Prerequisites

1. **macOS** with **Xcode 15+** installed.
2. **XcodeGen** installed (`brew install xcodegen`).

## Setup Instructions

Do **not** manually open or create `DravyaMobile.xcodeproj` yet. The project file is generated dynamically to prevent `.pbxproj` merge conflicts.

1. Generate the Xcode project:
   ```bash
   cd mobile-iOS
   xcodegen generate
   ```
2. Open the generated project:
   ```bash
   open DravyaMobile.xcodeproj
   ```

## Running the App

The iOS app requires the local backend to be running.

**Terminal 1 (Backend):**
```bash
cd server
npm run dev
```

**Terminal 2 (iOS):**
Open `DravyaMobile.xcodeproj` in Xcode and press **Run (⌘R)**, selecting an iOS Simulator (e.g., iPhone 16).

## API Configuration

The base URL for the backend API is configured in:
`DravyaMobile/Resources/Config/Development.xcconfig`

### iOS Simulator vs. Physical Device

- **Simulator:** `localhost` correctly resolves to your Mac's backend. (`http://localhost:8000/api`)
- **Physical Device:** If you run the app on a physical iPhone, `localhost` means the phone itself. You must replace `localhost` in `Development.xcconfig` with your Mac's LAN IP address (e.g., `http://192.168.1.42:8000/api`). Both devices must be on the same Wi-Fi network.

## Authentication & Security

- **JWT Storage:** Authentication tokens are stored securely in the iOS Keychain via `KeychainManager`. They are never logged or stored in plain text.
- **Backend Auth:** The login service hits `POST /api/auth/login` and receives `{ user, token }`.
- **Credentials:** The mobile app source code does not contain any database or blockchain credentials.

## Folder Structure

```
mobile-iOS/
├── project.yml                 # XcodeGen configuration
├── DravyaMobile/
│   ├── App/                    # App lifecycle (DravyaMobileApp, RootView)
│   ├── Core/                   # Core managers (Networking, Authentication, Utils)
│   ├── Models/                 # Decodable models (User, APIResponse)
│   ├── Services/               # API clients (AuthService)
│   ├── Features/               # Feature modules (Auth, QRScanner - planned)
│   └── Resources/              # xcconfig, Assets
└── README.md
```
