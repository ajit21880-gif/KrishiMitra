"use client";

import React from "react";
import Link from "next/link";
import { ArrowLeft, Heart, ShieldCheck, Sparkles, Building2, Users } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 flex flex-col">
      {/* Header */}
      <header className="bg-primary-600 text-white p-4 shadow flex items-center gap-3">
        <Link 
          href="/" 
          className="p-1 rounded-full hover:bg-primary-700 transition flex items-center justify-center text-white"
          aria-label="Back to Dashboard"
        >
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="font-extrabold text-lg tracking-tight">About CrestSubarn</h1>
          <p className="text-xs text-green-100">Our Mission & Public Commitment</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-4 max-w-2xl mx-auto w-full space-y-6 py-6">
        {/* Startup Card */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-primary-50 border border-primary-100 flex items-center justify-center text-primary-600 font-extrabold text-xl">
              CS
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">CrestSubarn</h2>
              <p className="text-xs text-gray-500 font-medium">Founded in 2026 • Dedicated to Indian Agriculture</p>
            </div>
          </div>

          <p className="text-sm text-gray-700 leading-relaxed">
            <strong>CrestSubarn</strong> is an agri-technology startup founded in <strong>2026</strong> with a single, uncompromising purpose: 
            to empower Indian farmers with direct, transparent, and timely agricultural intelligence.
          </p>

          <p className="text-sm text-gray-700 leading-relaxed">
            Recognizing that market price volatility, language barriers, and fragmented data often leave farmers at a disadvantage, 
            CrestSubarn developed <strong>KrishiMitra AI</strong> as a unified, speech-enabled agricultural assistant.
          </p>
        </div>

        {/* Public Utility Commitment */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-green-900 font-bold">
            <Heart className="text-red-500 fill-red-500" size={20} />
            <h3 className="text-base">100% Free & Pro-Farmer Commitment</h3>
          </div>

          <div className="space-y-3 text-xs text-gray-700 leading-relaxed">
            <div className="flex items-start gap-2">
              <ShieldCheck className="text-primary-600 shrink-0 mt-0.5" size={16} />
              <span>
                <strong>Completely Free to Use:</strong> KrishiMitra AI is and will always remain completely free for every farmer across India.
              </span>
            </div>

            <div className="flex items-start gap-2">
              <Sparkles className="text-primary-600 shrink-0 mt-0.5" size={16} />
              <span>
                <strong>Zero Advertisements & No Commercial Exploitation:</strong> There are no commercial advertisements, sponsored placements, or popups. We have no means or intent to generate profits from farmers.
              </span>
            </div>

            <div className="flex items-start gap-2">
              <Building2 className="text-primary-600 shrink-0 mt-0.5" size={16} />
              <span>
                <strong>Intellectual Property & Transparency:</strong> Although the proprietary application code cannot be open-sourced due to corporate IP protections, its public service mandate is enshrined in our foundational mission: technology built solely in service of the Indian farmer.
              </span>
            </div>
          </div>
        </div>

        {/* Contact & Support */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-2 text-center">
          <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Farmer Support & Inquiries</p>
          <p className="text-sm font-bold text-gray-800">
            For feedback, market suggestions, or support, write to us at:
          </p>
          <p className="text-sm font-mono font-bold text-primary-600">
            <a href="mailto:support@crestsubarn.com" className="hover:underline">
              support@crestsubarn.com
            </a>
          </p>
        </div>

        {/* Navigation Links */}
        <div className="flex justify-between items-center text-xs text-primary-700 font-bold px-2">
          <Link href="/acknowledgements" className="hover:underline">
            ← Government Initiatives & Acknowledgements
          </Link>
          <Link href="/terms" className="hover:underline">
            Terms & Conditions →
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-100 text-[10px] text-gray-500 text-center py-3 border-t border-gray-200">
        © 2026 Crestsubarn. All rights reserved.
      </footer>
    </div>
  );
}
