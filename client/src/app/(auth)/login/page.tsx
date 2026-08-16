import { LoginForm } from '@/features/auth/components/LoginForm'

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 relative overflow-hidden">
      {/* Decorative background Elements */}
      <div className="absolute top-0 left-0 w-full h-[30vh] bg-gradient-to-b from-[#184E48]/5 to-transparent pointer-events-none"></div>
      
      <div className="relative z-10 w-full px-4">
        <LoginForm />
      </div>
    </div>
  )
}
