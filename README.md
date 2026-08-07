# 🌿 Dravya — Ayurvedic Blockchain Platform

> AI-powered traceability platform ensuring authenticity, quality, and transparency in the Ayurvedic herb supply chain.

## 📁 Project Structure

```
Dravya/
├── client/     → Next.js 16 frontend (React 19, TypeScript, Tailwind CSS)
├── server/     → Express.js backend (TypeScript, Prisma, PostgreSQL)
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 18
- **PostgreSQL** ≥ 14
- **npm** ≥ 9

### 1. Clone the Repository

```bash
git clone https://github.com/AnubhavGitHub07/Dravya-Ayurvedic-Blockchain-Platform.git
cd Dravya-Ayurvedic-Blockchain-Platform
```

### 2. Setup the Server

```bash
cd server
npm install
cp .env.example .env
# Update .env with your PostgreSQL connection string and JWT secret
npx prisma generate
npx prisma db push
npm run dev
```

The server runs on **http://localhost:8000**.

### 3. Setup the Client

```bash
cd client
npm install
npm run dev
```

The client runs on **http://localhost:3000**.

## 🔧 Tech Stack

| Layer      | Technology                           |
| ---------- | ------------------------------------ |
| Frontend   | Next.js 16, React 19, Tailwind CSS  |
| Backend    | Express.js, TypeScript               |
| Database   | PostgreSQL with Prisma ORM           |
| Auth       | JWT (JSON Web Tokens)                |
| Validation | Zod                                  |
| State      | Zustand (client), React Query        |

## 📜 License

MIT
