"use client";

import * as React from "react";
import { Eye, EyeOff, ChevronDown,UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sprout,
  Factory,
  FlaskConical,
  BadgeCheck,
  ShieldCheck,
   User, Mail, Lock, Building2, UserCircle, FileText,UserRoundCog} from "lucide-react"


export function RegisterForm() {
  const [showPassword, setShowPassword] = React.useState(false);

  return (
    

    <div className="w-[65%] bg-[var(--ww)] backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-[0_8px_60px_rgba(0,0,0,0.3)] relative overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-bl-[100px]" />

      <div className="relative z-10">
        

        <form className="space-y-4">
          <div className="space-y-1.5">
            <Label className="text-black text-md font-bold"><UserRoundCog className="w-4 h-4 text-accent" />Select your role</Label>
            <Select>
              <SelectTrigger className="bg-white/5 border-white/10 text-black data-[placeholder]:text-slate-500  h-11 rounded-xl focus:ring-primary/40 shadow-md w-full">
                <SelectValue  placeholder="Choose a role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Admin" className="  cursor-pointer "><BadgeCheck/>Admin</SelectItem>
                <SelectItem value="Processor" className="  cursor-pointer "><Sprout/>Processor</SelectItem>
                <SelectItem value="Lab" className="  cursor-pointer "><FlaskConical/>Lab</SelectItem>
                <SelectItem value="Manufacturer" className="  cursor-pointer "><Factory/>Manufacturer</SelectItem>
                <SelectItem value="Verification Authority" className="  cursor-pointer "><ShieldCheck/>Verification Authority</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label className="text-black text-md font-bold flex items-center gap-1.5">
              <User className="w-4 h-4 text-accent" /> Name
            </Label>
            <Input
              placeholder="Enter your full name"
              className="bg-white/5 border border-accent/15 text-black placeholder:text-slate-500 h-11 rounded-xl focus-visible:ring-primary/40 shadow-md"
            />
          </div>

          <div className="space-y-1.5">
            <Label className="text-black text-md font-bold flex items-center gap-1.5">
              <Mail className="w-4 h-4 text-accent" /> Email
            </Label>
            <Input
              type="email"
              placeholder="Enter your email"
              className="bg-white/5 border border-accent/15 text-black placeholder:text-slate-500 h-11 rounded-xl focus-visible:ring-primary/40 shadow-md"
            />
          </div>

          <div className="space-y-1.5">
            <Label className="text-black text-md font-bold flex items-center gap-1.5">
              <Lock className="w-4 h-4 text-accent" /> Create password
            </Label>
            <div className="relative">
              <Input
                type={showPassword ? "text" : "password"}
                placeholder="At least 8 characters"
                className="bg-white/5 border border-accent/15 text-black placeholder:text-slate-500 h-11 rounded-xl pr-10 focus-visible:ring-primary/40 shadow-md"
              />
              <button
                type="button"
                onClick={() => setShowPassword((p) => !p)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-black transition-colors"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="space-y-1.5">
            <Label className="text-black text-md font-bold flex items-center gap-1.5">
              <Building2 className="w-4 h-4 text-accent" /> Company name
            </Label>
            <Input
              placeholder="Enter your company name"
              className="bg-white/5 border border-accent/15 text-black placeholder:text-slate-500 h-11 rounded-xl focus-visible:ring-primary/40 shadow-md"
            />
          </div>

          <div className="space-y-1.5">
            <Label className="text-black text-md font-bold flex items-center gap-1.5">
              <UserCircle className="w-4 h-4 text-accent" /> Contact Person
            </Label>
            <Input
              placeholder="Enter name of the contact person"
              className="bg-white/5 border border-accent/15 text-black placeholder:text-slate-500 h-11 rounded-xl focus-visible:ring-primary/40 shadow-md"
            />
          </div>

          <div className="space-y-1.5">
            <Label className="text-black text-md font-bold flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-accent" /> GST number
            </Label>
            <Input
              placeholder="Enter your GST number"
              className="bg-white/5 border border-accent/15 text-black placeholder:text-slate-500 h-11 rounded-xl focus-visible:ring-primary/40 shadow-md"
            />
          </div>

          <div className="space-y-1.5">
            <Label className="text-black text-md font-bold flex items-center gap-1.5">
              <BadgeCheck className="w-4 h-4 text-accent" /> License number
            </Label>
            <Input
              placeholder="Enter your license number"
              className="bg-white/5 border border-accent/15 text-black placeholder:text-slate-500 h-11 rounded-xl focus-visible:ring-primary/40 shadow-md"
            />
          </div>

          <Button
            type="submit"
            className="w-full h-11 rounded-xl bg-[#184E48] hover:bg-[#184E48]/90 transition-all duration-300 text-white font-semibold mt-2"
          >
           <UserPlus className="h-5 w-5"/> Create account
          </Button>
        </form>
      </div>
    </div>
  );
}